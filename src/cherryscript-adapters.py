"""Adapters: optional pymysql/h2o support; FastAPI deploy/undeploy controller."""
try:
    import pymysql
    HAS_PYMYSQL = True
except Exception:
    HAS_PYMYSQL = False

try:
    import h2o
    from h2o.automl import H2OAutoML
    HAS_H2O = True
except Exception:
    HAS_H2O = False

class Frame:
    def __init__(self, rows):
        self.rows = rows
    def describe(self):
        return {'rows': len(self.rows), 'columns': list(self.rows[0].keys()) if self.rows else []}

class Model:
    def __init__(self, name, leaderboard):
        self.name = name; self.leaderboard = leaderboard

class Endpoint:
    def __init__(self, url):
        self.url = url

_MOCK = {'orders':[{'id':1,'status':'shipped','is_return':False,'amount':100.0},
                   {'id':2,'status':'shipped','is_return':True,'amount':50.0},
                   {'id':3,'status':'pending','is_return':False,'amount':75.0}]}

if HAS_PYMYSQL:
    class Database:
        def __init__(self, uri, user=None, password=None):
            from urllib.parse import urlparse
            p = urlparse(uri)
            self.host = p.hostname or 'localhost'; self.port = p.port or 3306
            self.db = p.path.lstrip('/'); self.user = user; self.password = password; self._conn = None
        def _connect(self):
            if self._conn: return self._conn
            self._conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password, database=self.db, cursorclass=pymysql.cursors.DictCursor)
            return self._conn
        def query(self, sql, params=None):
            conn = self._connect()
            with conn.cursor() as cur:
                cur.execute(sql, params or [])
                return cur.fetchall()
else:
    class Database:
        def __init__(self, uri, user=None, password=None):
            self.uri = uri; self.user = user; self.password = password
        def query(self, sql, params=None):
            if 'from orders' in sql.lower():
                rows = _MOCK['orders']
                if "where status='shipped'" in sql.lower():
                    return [r for r in rows if r['status']=='shipped']
                return rows
            return []

# H2O helpers (mock if not present)
if HAS_H2O:
    def to_frame(val):
        if hasattr(val,'frame_id') or hasattr(val,'columns'): return val
        import pandas as pd
        return h2o.H2OFrame(pd.DataFrame(val))
    def automl_train(frame, target, max_runtime_secs=3600):
        h2o.init()
        aml = H2OAutoML(max_runtime_secs=max_runtime_secs)
        aml.train(y=target, training_frame=frame)
        return aml
else:
    def to_frame(val):
        if isinstance(val, Frame): return val
        if isinstance(val, list): return Frame(val)
        return Frame([])
    def automl_train(frame, target, max_runtime_secs=3600):
        lb = [{'model':'gbm_1','auc':0.93},{'model':'glm_1','auc':0.88}]
        return Model('mock_automl', lb)

# FastAPI deployer with controller for stop and health
import threading, atexit, time
from typing import Dict, Any
_ACTIVE = []

class ServerController:
    def __init__(self, server, thread, url):
        self._server = server; self._thread = thread; self.url = url
    def stop(self, timeout=5.0):
        try:
            if hasattr(self._server, 'should_exit'):
                self._server.should_exit = True
            elif hasattr(self._server, 'stop'):
                try: self._server.stop()
                except Exception: pass
            self._thread.join(timeout)
            return True
        except Exception:
            return False

def _register(c):
    _ACTIVE.append(c)

def shutdown_all():
    for c in list(_ACTIVE):
        try: c.stop()
        except Exception: pass
    _ACTIVE.clear()

atexit.register(shutdown_all)

def deploy_model(model, endpoint_url='http://127.0.0.1:8080/predict'):
    try:
        from fastapi import FastAPI
        import uvicorn
    except Exception:
        print('FastAPI/uvicorn not installed. Install with: pip install fastapi uvicorn')
        return Endpoint(endpoint_url)

    app = FastAPI()

    @app.get('/health')
    def health():
        return {'status':'ok'}

    @app.post('/predict')
    def predict(payload: Dict = None):
        payload = payload or {}
        rows = payload.get('rows', [])
        if hasattr(model,'leaderboard') and not hasattr(model,'predict'):
            preds = [{'prediction': (1 if (r.get('amount',0)>80) else 0)} for r in rows]
            return {'predictions': preds}
        if hasattr(model,'predict'):
            try:
                import pandas as pd, h2o
                df = pd.DataFrame(rows); hf = h2o.H2OFrame(df)
                pred = model.predict(hf)
                return {'predictions': pred.as_data_frame().to_dict(orient='records')}
            except Exception as e:
                return {'error': str(e)}
        return {'predictions': []}

    try:
        host = endpoint_url.split('//')[-1].split(':')[0]; port = int(endpoint_url.split(':')[-1].split('/')[0])
    except Exception:
        host='127.0.0.1'; port=8080
    config = uvicorn.Config(app=app, host=host, port=port, log_level='warning')
    server = uvicorn.Server(config=config)
    def run(): 
        try: server.run()
        except Exception as e: print('uvicorn error:', e)
    t = threading.Thread(target=run, daemon=True); t.start()
    ctrl = ServerController(server, t, endpoint_url); _register(ctrl)
    time.sleep(0.2)
    return ctrl

def undeploy_controller(ctrl, timeout=5.0):
    if isinstance(ctrl, ServerController):
        return ctrl.stop(timeout)
    return False
