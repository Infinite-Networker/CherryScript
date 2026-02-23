"""Adapters: optional pymysql/h2o support; FastAPI deploy/undeploy controller."""
import threading
import atexit
import time
from typing import Any, Dict, List, Optional

# ── optional dependency: pymysql ────────────────────────────────────────────
try:
    import pymysql
    HAS_PYMYSQL = True
except Exception:
    HAS_PYMYSQL = False

# ── optional dependency: h2o ────────────────────────────────────────────────
try:
    import h2o
    from h2o.automl import H2OAutoML
    HAS_H2O = True
except Exception:
    HAS_H2O = False


# ── Core data types ──────────────────────────────────────────────────────────

class Frame:
    """Lightweight data-frame wrapper."""

    def __init__(self, rows: List[Dict]):
        self.rows = list(rows) if rows else []

    def describe(self) -> Dict:
        return {
            'rows': len(self.rows),
            'columns': list(self.rows[0].keys()) if self.rows else [],
        }

    def __len__(self):
        return len(self.rows)

    def __iter__(self):
        return iter(self.rows)

    def __repr__(self):
        return f"<Frame rows={len(self.rows)}>"


class Model:
    """Wraps a trained model (real H2O or mock)."""

    def __init__(self, name: str, leaderboard: List, model_obj=None):
        self.name = name
        self.leaderboard = leaderboard
        self.model_type = "AutoML"
        self._model = model_obj

    def predict(self, frame) -> List[Dict]:
        """Return predictions for a Frame or list of dicts."""
        if self._model is not None and HAS_H2O:
            try:
                import pandas as pd
                rows = frame.rows if isinstance(frame, Frame) else list(frame)
                df = pd.DataFrame(rows)
                hf = h2o.H2OFrame(df)
                pred = self._model.predict(hf)
                return pred.as_data_frame().to_dict(orient='records')
            except Exception as e:
                print(f"[warn] H2O predict error: {e}")

        # mock prediction: simple rule-based
        rows = frame.rows if isinstance(frame, Frame) else list(frame)
        results = []
        for r in rows:
            freq = r.get('purchase_frequency', r.get('freq', 3))
            income = r.get('income', 60000)
            if freq <= 1 or income < 50000:
                pred_val, conf = 1, 0.80
            else:
                pred_val, conf = 0, 0.75
            results.append({'prediction': pred_val, 'confidence': conf})
        return results

    def __repr__(self):
        return f"<Model name={self.name} leaderboard={len(self.leaderboard)}>"


class Endpoint:
    """Represents a deployed REST API endpoint."""

    def __init__(self, url: str):
        self.url = url

    def __repr__(self):
        return f"<Endpoint url={self.url}>"


# ── Mock database data ───────────────────────────────────────────────────────

_MOCK: Dict[str, List[Dict]] = {
    'orders': [
        {'id': 1, 'status': 'shipped',  'is_return': False, 'amount': 100.0},
        {'id': 2, 'status': 'shipped',  'is_return': True,  'amount': 50.0},
        {'id': 3, 'status': 'pending',  'is_return': False, 'amount': 75.0},
    ],
    'customers': [
        {'id': 1, 'name': 'Alice',   'active': True,  'signup_date': '2023-06-01', 'total_spent': 1250.50, 'orders': 5},
        {'id': 2, 'name': 'Bob',     'active': True,  'signup_date': '2023-03-15', 'total_spent': 850.75,  'orders': 3},
        {'id': 3, 'name': 'Charlie', 'active': False, 'signup_date': '2022-11-20', 'total_spent': 320.00,  'orders': 2},
    ],
}


# ── Database adapter ─────────────────────────────────────────────────────────

if HAS_PYMYSQL:
    class Database:
        def __init__(self, uri: str, user: Optional[str] = None, password: Optional[str] = None):
            from urllib.parse import urlparse
            p = urlparse(uri)
            self.host = p.hostname or 'localhost'
            self.port = p.port or 3306
            self.db = p.path.lstrip('/')
            self.user = user or p.username
            self.password = password or p.password
            self._conn = None

        def _connect(self):
            if self._conn:
                return self._conn
            self._conn = pymysql.connect(
                host=self.host, port=self.port,
                user=self.user, password=self.password,
                database=self.db,
                cursorclass=pymysql.cursors.DictCursor,
            )
            return self._conn

        def query(self, sql: str, params=None) -> List[Dict]:
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(sql, params or [])
                return list(cur.fetchall())

        def __repr__(self):
            return f"<Database host={self.host} db={self.db}>"

else:
    class Database:  # type: ignore[no-redef]
        """Mock database used when pymysql is not installed."""

        def __init__(self, uri: str, user: Optional[str] = None, password: Optional[str] = None):
            self.uri = uri
            self.user = user
            self.password = password

        def query(self, sql: str, params=None) -> List[Dict]:
            sql_lower = sql.lower()
            table = None
            for t in _MOCK:
                if f'from {t}' in sql_lower:
                    table = t
                    break
            if table is None:
                return []
            rows = list(_MOCK[table])
            if "where status='shipped'" in sql_lower:
                rows = [r for r in rows if r.get('status') == 'shipped']
            if "where active = true" in sql_lower or "where active=true" in sql_lower:
                rows = [r for r in rows if r.get('active')]
            return rows

        def __repr__(self):
            return f"<Database(mock) uri={self.uri}>"


# ── H2O / frame helpers ──────────────────────────────────────────────────────

if HAS_H2O:
    def to_frame(val) -> Any:
        if hasattr(val, 'frame_id') or hasattr(val, 'columns'):
            return val
        import pandas as pd
        if isinstance(val, Frame):
            return h2o.H2OFrame(pd.DataFrame(val.rows))
        if isinstance(val, list):
            return h2o.H2OFrame(pd.DataFrame(val))
        return h2o.H2OFrame(pd.DataFrame([]))

    def automl_train(frame, target: str, max_runtime_secs: int = 3600) -> Model:
        h2o.init()
        aml = H2OAutoML(max_runtime_secs=max_runtime_secs)
        aml.train(y=target, training_frame=frame)
        lb = aml.leaderboard.as_data_frame().to_dict(orient='records')
        return Model('h2o_automl', lb, model_obj=aml.leader)

else:
    def to_frame(val) -> Frame:  # type: ignore[misc]
        if isinstance(val, Frame):
            return val
        if isinstance(val, list):
            return Frame(val)
        return Frame([])

    def automl_train(frame, target: str, max_runtime_secs: int = 3600) -> Model:  # type: ignore[misc]
        lb = [
            {'model_id': 'GBM_1',   'model': 'GBM_1',   'auc': 0.93},
            {'model_id': 'GLM_1',   'model': 'GLM_1',   'auc': 0.88},
            {'model_id': 'DRF_1',   'model': 'DRF_1',   'auc': 0.85},
        ]
        return Model('mock_automl', lb)


# ── FastAPI deployment ───────────────────────────────────────────────────────

_ACTIVE: List['ServerController'] = []


class ServerController:
    """Controls a running uvicorn server thread."""

    def __init__(self, server, thread, url: str):
        self._server = server
        self._thread = thread
        self.url = url

    def stop(self, timeout: float = 5.0) -> bool:
        try:
            if hasattr(self._server, 'should_exit'):
                self._server.should_exit = True
            elif hasattr(self._server, 'stop'):
                try:
                    self._server.stop()
                except Exception:
                    pass
            self._thread.join(timeout)
            return True
        except Exception:
            return False

    def __repr__(self):
        return f"<ServerController url={self.url}>"


def _register(c: ServerController):
    _ACTIVE.append(c)


def shutdown_all():
    for c in list(_ACTIVE):
        try:
            c.stop()
        except Exception:
            pass
    _ACTIVE.clear()


atexit.register(shutdown_all)


def deploy_model(model, endpoint_url: str = 'http://127.0.0.1:8080/predict') -> 'ServerController | Endpoint':
    """Deploy a model as a FastAPI REST endpoint.

    Falls back to a plain Endpoint if FastAPI/uvicorn are not installed.
    """
    try:
        from fastapi import FastAPI
        import uvicorn
    except ImportError:
        print('[warn] FastAPI/uvicorn not installed. '
              'Install with: pip install fastapi uvicorn')
        return Endpoint(endpoint_url)

    app = FastAPI(title="CherryScript Model API")

    @app.get('/health')
    def health():
        return {'status': 'ok', 'model': getattr(model, 'name', 'unknown')}

    @app.post('/predict')
    def predict(payload: Dict = None):
        payload = payload or {}
        rows = payload.get('rows', [])
        if hasattr(model, 'predict'):
            try:
                result = model.predict(Frame(rows))
                return {'predictions': result}
            except Exception as e:
                return {'error': str(e), 'predictions': []}
        return {'predictions': []}

    try:
        parts = endpoint_url.split('//')[-1].split(':')
        host = parts[0]
        port = int(parts[1].split('/')[0])
    except Exception:
        host, port = '127.0.0.1', 8080

    config = uvicorn.Config(app=app, host=host, port=port, log_level='warning')
    server = uvicorn.Server(config=config)

    def _run():
        try:
            server.run()
        except Exception as e:
            print(f'[uvicorn error] {e}')

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    ctrl = ServerController(server, t, endpoint_url)
    _register(ctrl)
    time.sleep(0.3)          # give the server a moment to start
    return ctrl


def undeploy_controller(ctrl, timeout: float = 5.0) -> bool:
    if isinstance(ctrl, ServerController):
        return ctrl.stop(timeout)
    return False
