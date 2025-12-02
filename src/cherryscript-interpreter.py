"""CherryScript interpreter prototype supporting many features.
Not a production compiler; prototype for demonstration and experimentation.
"""
from cherryscript.parser import split_statements, parse_call
from cherryscript.runtime.adapters import Database, Frame, Model, Endpoint, to_frame, automl_train, deploy_model, undeploy_controller
import re

class RuntimeError(Exception): pass

class Runtime:
    def __init__(self):
        self.env = {}
    # expression evaluator (recursive, supports arithmetic, comparisons, logic, arrays)
    def eval(self, expr):
        expr = expr.strip()
        # literals
        if expr.startswith('"') and expr.endswith('"') or expr.startswith("'") and expr.endswith("'"):
            return expr[1:-1]
        if expr == 'true': return True
        if expr == 'false': return False
        # array literal
        if expr.startswith('[') and expr.endswith(']'):
            inner = expr[1:-1].strip()
            if not inner: return []
            parts = self._split_args(inner)
            return [self.eval(p) for p in parts]
        # parenthesis
        if expr.startswith('(') and expr.endswith(')'):
            return self.eval(expr[1:-1])
        # handle simple function calls and variable references
        if '(' in expr and expr.endswith(')') and re.match(r'[a-zA-Z_][a-zA-Z0-9_\.]*\s*\(', expr):
            name, args = parse_call(expr)
            # special builtin calls
            if name == 'len':
                v = self.eval(args[0]) if args else None
                try: return len(v)
                except: return 0
            # defer to run_call
            return self.run_call(name, args)
        # dotted property access
        if '.' in expr and expr.split('.')[0] in self.env:
            parts = expr.split('.')
            cur = self.env.get(parts[0])
            for p in parts[1:]:
                if hasattr(cur,p): cur = getattr(cur,p)
                elif isinstance(cur, dict) and p in cur: cur = cur[p]
                else: cur = None
            return cur
        # variable
        if expr in self.env:
            return self.env[expr]
        # numbers
        if re.match(r'^-?[0-9]+\\.[0-9]+$', expr): return float(expr)
        if re.match(r'^-?[0-9]+$', expr): return int(expr)
        # comparisons and logical: evaluate with python safe replacements
        # translate operators to python equivalents
        safe = expr.replace(' and ', ' and ').replace(' or ', ' or ').replace(' not ', ' not ')
        safe = safe.replace('==', '==').replace('!=', '!=').replace('^', '**')
        # allow + - * / % ** parentheses
        try:
            # replace variable names with their values for eval
            tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_\.]*', safe)
            for t in sorted(set(tokens), key=lambda x: -len(x)):
                if t in ('and','or','not','True','False'): continue
                if t in self.env:
                    val = self.env[t]
                    safe = re.sub(r'\\b'+re.escape(t)+r'\\b', repr(val), safe)
            return eval(safe, {'__builtins__':None}, {})
        except Exception:
            return expr

    def _split_args(self, s):
        parts=[]; cur=[]; in_q=False; q=None; depth=0
        i=0
        while i < len(s):
            c=s[i]
            if c in ('"',"'"):
                if not in_q: in_q=True; q=c
                elif q==c: in_q=False; q=None
                cur.append(c); i+=1; continue
            if not in_q and c=='(':
                depth+=1; cur.append(c); i+=1; continue
            if not in_q and c==')':
                depth=max(0,depth-1); cur.append(c); i+=1; continue
            if not in_q and depth==0 and c==',':
                parts.append(''.join(cur).strip()); cur=[]; i+=1; continue
            cur.append(c); i+=1
        if cur: parts.append(''.join(cur).strip())
        return [p for p in parts if p!='']

    def run_call(self, name, args):
        # handle dotted calls like db.query
        if name.endswith('.query'):
            var = name.split('.')[0]; db = self.env.get(var)
            if not isinstance(db, Database): raise RuntimeError('Not a DB')
            sql = self.eval(args[0])
            return db.query(sql)
        if name == 'connect':
            uri = self.eval(args[0]); user=self.eval(args[1]) if len(args)>1 else None; pwd=self.eval(args[2]) if len(args)>2 else None
            return Database(uri, user, pwd)
        if name == 'h2o.frame':
            arg = args[0] if args else None
            val = self.eval(arg) if arg else []
            return to_frame(val)
        if name == 'h2o.preprocess':
            return self.eval(args[0])
        if name == 'h2o.automl':
            frm = args[0] if args else None
            target = self.eval(args[1]) if len(args)>1 else None
            return automl_train(self.eval(frm) if isinstance(frm,str) else frm, target)
        if name == 'deploy':
            m = args[0]; endpoint = self.eval(args[1]) if len(args)>1 else 'http://127.0.0.1:8080/predict'
            ctrl = deploy_model(self.eval(m) if isinstance(m,str) else m, endpoint)
            return ctrl
        if name == 'undeploy':
            # handled in interpreter-level
            return None
        if name == 'print':
            val = self.eval(args[0]) if args else ''
            # support interpolation if string
            if isinstance(val,str) and '${' in val:
                import re
                def repl(m):
                    key=m.group(1).strip()
                    if '.' in key:
                        return str(self.eval(key))
                    return str(self.env.get(key,''))
                val = re.sub(r'\\$\\{([^}]+)\\}', repl, val)
            print(val)
            return None
        if name == 'len':
            v = self.eval(args[0])
            return len(v) if v is not None else 0
        # unknown
        return None

    # statement execution with support for var/let, assignments, if/else, while, for, for-in, undeploy
    def run_stmt(self, stmt):
        s = stmt.strip()
        # if statement
        if s.startswith('if '):
            m = re.match(r'if\s*(\(.*\)|[^\{]+)\s*\{(.*)\}(?:\s*else\s*\{(.*)\})?$', s, flags=re.S)
            if not m:
                raise RuntimeError('Invalid if syntax')
            cond = m.group(1).strip()
            if cond.startswith('(') and cond.endswith(')'): cond=cond[1:-1]
            then_block = m.group(2).strip(); else_block = m.group(3).strip() if m.group(3) else None
            if self.eval(cond):
                for st in split_statements(then_block): self.run_stmt(st)
            elif else_block:
                for st in split_statements(else_block): self.run_stmt(st)
            return
        # while
        if s.startswith('while '):
            m = re.match(r'while\s*(\(.*\)|[^\{]+)\s*\{(.*)\}$', s, flags=re.S)
            if not m: raise RuntimeError('Invalid while')
            cond = m.group(1).strip(); body = m.group(2).strip()
            if cond.startswith('(') and cond.endswith(')'): cond=cond[1:-1]
            # loop
            loop_guard = 100000
            while self.eval(cond):
                for st in split_statements(body):
                    self.run_stmt(st)
                loop_guard -= 1
                if loop_guard <= 0: break
            return
        # for-in: for var x in expr { ... }
        if s.startswith('for '):
            # try for-in first
            m = re.match(r'for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s+(.+?)\s*\{(.*)\}$', s, flags=re.S)
            if m:
                var = m.group(1); collection = m.group(2).strip(); body = m.group(3).strip()
                coll = self.eval(collection)
                if coll is None: return
                for item in coll:
                    self.env[var] = item
                    for st in split_statements(body): self.run_stmt(st)
                return
            # C-style for: for var i = 0; condition; post { body }
            m2 = re.match(r'for\s+(.*?);(.*?);(.*?)\s*\{(.*)\}$', s, flags=re.S)
            if m2:
                init = m2.group(1).strip(); cond = m2.group(2).strip(); post = m2.group(3).strip(); body = m2.group(4).strip()
                if init: self.run_stmt(init)
                loop_guard = 100000
                while True:
                    if cond and not self.eval(cond): break
                    for st in split_statements(body): self.run_stmt(st)
                    if post: self.run_stmt(post)
                    loop_guard -= 1
                    if loop_guard <= 0: break
                return
        # var/let
        if s.startswith('var ') or s.startswith('let '):
            m = re.match(r'(var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', s, flags=re.S)
            if not m: raise RuntimeError('Invalid var decl')
            name = m.group(2); expr = m.group(3).strip()
            # compound assignment
            for op in ['+=','-=','*=','/=','%=']:
                if op in expr:
                    parts = expr.split(op)
                    lhs = parts[0].strip(); rhs = parts[1].strip()
                    val = self.eval(lhs)
                    rval = self.eval(rhs)
                    if op=='+=': self.env[name]= val + rval
                    elif op=='-=': self.env[name]= val - rval
                    elif op=='*=': self.env[name]= val * rval
                    elif op=='/=': self.env[name]= val / rval
                    elif op=='%=': self.env[name]= val % rval
                    return
            # normal
            val = self.eval(expr)
            self.env[name] = val
            print(f"[env] {name} = {val}")
            return
        # undeploy call
        if s.startswith('undeploy'):
            # parse args
            name,args = parse_call(s)
            timeout = 5.0
            if len(args)>=2:
                timeout = float(self.eval(args[1]))
            target = args[0] if args else None
            if target is None:
                print('[error] undeploy: missing argument')
                return False
            # if string literal, lookup variable
            if (target.startswith('"') and target.endswith('"')) or (target.startswith("'") and target.endswith("'")):
                varname = target[1:-1]
                ctrl = self.env.get(varname)
            else:
                ctrl = self.eval(target)
            ok = undeploy_controller(ctrl, timeout)
            if ok:
                url = getattr(ctrl,'url',str(ctrl))
                print(f"[info] CherryScript undeployed {url}")
                return True
            else:
                url = getattr(ctrl,'url',str(ctrl))
                print(f"[warn] undeploy: server at {url} did not stop in {timeout}s")
                return False
        # assignment
        m = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', s, flags=re.S)
        if m:
            name, expr = m.groups(); expr=expr.strip()
            # compound operators
            for op in ['+=','-=','*=','/=','%=']:
                if op in name+expr:
                    left = name
            val = self.eval(expr)
            self.env[name]=val
            print(f"[env] {name} = {val}")
            return
        # function or bare call
        if '(' in s and s.endswith(')'):
            name,args = parse_call(s)
            res = self.run_call(name,args)
            # print env updates for connect/query/deploy
            if isinstance(res, Database): print(f"[env] db = <Database>")
            if isinstance(res, Frame): print(f"[env] frame = <Frame rows={res.describe()['rows']}>")
            if hasattr(res,'leaderboard'): print(f"[env] model = <Model {res.name} leaderboard={len(res.leaderboard)}>")
            if hasattr(res,'url') or hasattr(res,'url'):
                url = getattr(res,'url', '')
                print(f"[env] endpoint = <Endpoint url={url}>")
            return
        # fallback
        return

    def run(self, text):
        stmts = split_statements(text)
        for s in stmts:
            if not s.strip(): continue
            try:
                self.run_stmt(s)
            except Exception as e:
                print('Error:', e)

if __name__ == '__main__':
    print('CherryScript runtime loaded')
