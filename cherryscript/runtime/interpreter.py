"""CherryScript interpreter — supports the full language feature set.

Supported constructs
--------------------
- Variables      : var / let  x = <expr>
- Assignment     : x = <expr>  (also +=, -=, *=, /=, %=)
- Print          : print(...)
- Control flow   : if / else if / else,  while,  for-in,  C-style for
- Functions      : fn name(params) { body }  +  return
- Builtins       : len, range, sum, min, max, format, time, append, keys
- Data structs   : array literals [...],  dict literals {...}
- String interp  : backtick strings  `hello ${name}`
- DB             : connect(), db.query()
- ML             : h2o.frame(), h2o.preprocess(), h2o.automl()
- Deploy         : deploy(model, url),  undeploy(ctrl, timeout?)
- Method calls   : model.predict(),  frame.describe(), obj.keys() …
"""

import re
import time as _time
from typing import Any, Dict, List, Optional

from cherryscript.parser import split_statements, parse_call, _split_by_comma
from cherryscript.runtime.adapters import (
    Database, Frame, Model, Endpoint,
    to_frame, automl_train, deploy_model, undeploy_controller,
)


class CherryRuntimeError(Exception):
    pass


# ── helpers ──────────────────────────────────────────────────────────────────

def _is_str_literal(s: str) -> bool:
    """Return True only if the whole expression is a single quoted string."""
    for q in ('"', "'", '`'):
        if s.startswith(q) and s.endswith(q) and len(s) >= 2:
            # Make sure the opening quote is actually closed at the very end
            # and there's no unescaped quote of the same type in between.
            content = s[1:-1]
            # scan for unescaped closing quote
            i = 0
            while i < len(content):
                if content[i] == '\\':
                    i += 2
                    continue
                if content[i] == q:
                    return False   # quote closed before the end → not a simple literal
                i += 1
            return True
    return False


def _unquote(s: str) -> str:
    return s[1:-1]


# Sentinel used to signal "could not resolve" in subscript chain
_UNRESOLVED = object()


# ── Runtime ──────────────────────────────────────────────────────────────────

class Runtime:
    """Evaluate and execute CherryScript code."""

    def __init__(self):
        self.env: Dict[str, Any] = {}
        self._functions: Dict[str, Dict] = {}   # user-defined fn store

    # ── public API ───────────────────────────────────────────────────────────

    def run(self, text: str) -> None:
        stmts = split_statements(text)
        for s in stmts:
            s = s.strip()
            if not s:
                continue
            try:
                self._run_stmt(s)
            except _ReturnSignal:
                pass          # top-level return is silently ignored
            except CherryRuntimeError as e:
                print(f'[error] {e}')
            except Exception as e:
                print(f'[error] {type(e).__name__}: {e}')

    # ── statement execution ──────────────────────────────────────────────────

    def _run_stmt(self, stmt: str) -> Any:
        s = stmt.strip()

        # ---- function definition: fn name(params) { body } -----------------
        fn_m = re.match(
            r'^fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*\{(.*)\}$',
            s, re.S,
        )
        if fn_m:
            fname = fn_m.group(1)
            params_raw = fn_m.group(2).strip()
            body = fn_m.group(3).strip()
            params = [p.strip() for p in params_raw.split(',') if p.strip()]
            self._functions[fname] = {'params': params, 'body': body}
            return None

        # ---- if / else if / else -------------------------------------------
        if re.match(r'^if\s*[\(\s]', s):
            return self._run_if(s)

        # ---- while ---------------------------------------------------------
        if re.match(r'^while\s*[\(\s]', s):
            return self._run_while(s)

        # ---- for -----------------------------------------------------------
        if re.match(r'^for\s+', s):
            return self._run_for(s)

        # ---- return --------------------------------------------------------
        if re.match(r'^return\b', s):
            expr = s[6:].strip()
            value = self._eval(expr) if expr else None
            raise _ReturnSignal(value)

        # ---- var / let declaration -----------------------------------------
        if re.match(r'^(?:var|let)\s+', s):
            m = re.match(r'^(?:var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', s, re.S)
            if not m:
                raise CherryRuntimeError(f'Invalid declaration: {s}')
            name, expr = m.group(1), m.group(2).strip()
            val = self._eval(expr)
            self.env[name] = val
            return val

        # ---- undeploy ------------------------------------------------------
        if s.startswith('undeploy'):
            return self._run_undeploy(s)

        # ---- compound assignment (+=, -= …) --------------------------------
        comp_m = re.match(
            r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*(\+=|-=|\*=|/=|%=)\s*(.+)$', s, re.S,
        )
        if comp_m:
            name, op, rhs = comp_m.groups()
            cur = self.env.get(name, 0)
            rval = self._eval(rhs.strip())
            ops = {'+=': lambda a, b: a + b, '-=': lambda a, b: a - b,
                   '*=': lambda a, b: a * b, '/=': lambda a, b: a / b,
                   '%=': lambda a, b: a % b}
            self.env[name] = ops[op](cur, rval)
            return self.env[name]

        # ---- regular assignment --------------------------------------------
        assign_m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', s, re.S)
        if assign_m:
            name, expr = assign_m.groups()
            # Make sure it's not a comparison (==)
            if not s.lstrip().startswith(name + '=='):
                val = self._eval(expr.strip())
                self.env[name] = val
                return val

        # ---- function / method call ----------------------------------------
        if re.match(r'[a-zA-Z_][a-zA-Z0-9_.]*\s*\(', s) and s.endswith(')'):
            return self._eval(s)

        # ---- bare expression -----------------------------------------------
        return self._eval(s)

    # ── control flow helpers ─────────────────────────────────────────────────

    def _run_if(self, s: str) -> None:
        """Handle if / else-if / else chains."""
        remainder = s

        while remainder:
            remainder = remainder.strip()

            if remainder.startswith('if') or remainder.startswith('else if'):
                # strip leading keyword
                if remainder.startswith('else if'):
                    body_start = remainder[7:].lstrip()   # after 'else if'
                else:
                    body_start = remainder[2:].lstrip()   # after 'if'

                # extract condition (with or without surrounding parens)
                cond_str, rest = _extract_condition(body_start)
                rest = rest.lstrip()

                # extract then block
                then_block, rest = _extract_block(rest)

                # evaluate
                if self._eval(cond_str):
                    self._run_block(then_block)
                    return
                remainder = rest.strip()

            elif remainder.startswith('else'):
                else_body = remainder[4:].lstrip()
                else_block, _ = _extract_block(else_body)
                self._run_block(else_block)
                return
            else:
                break

    def _run_while(self, s: str) -> None:
        rest = s[5:].lstrip()                      # after 'while'
        cond_str, rest = _extract_condition(rest)
        rest = rest.lstrip()
        body, _ = _extract_block(rest)

        guard = 1_000_000
        while self._eval(cond_str):
            try:
                self._run_block(body)
            except _BreakSignal:
                break
            except _ContinueSignal:
                pass
            guard -= 1
            if guard <= 0:
                print('[warn] while loop exceeded iteration limit')
                break

    def _run_for(self, s: str) -> None:
        rest = s[3:].lstrip()                      # after 'for'

        # for-in:  for <var> in <expr> { … }
        m = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s+(.+?)\s*\{', rest, re.S)
        if m:
            var = m.group(1)
            coll_expr = m.group(2).strip()
            # find the matching block
            brace_start = rest.index('{')
            body, _ = _extract_block(rest[brace_start:])
            collection = self._eval(coll_expr)
            if collection is None:
                return
            if isinstance(collection, (Frame,)):
                collection = collection.rows
            for item in collection:
                self.env[var] = item
                try:
                    self._run_block(body)
                except _BreakSignal:
                    break
                except _ContinueSignal:
                    pass
            return

        # C-style for:  for <init>; <cond>; <post> { … }
        m2 = re.match(r'(.*?);(.*?);(.*?)\s*\{', rest, re.S)
        if m2:
            init_s = m2.group(1).strip()
            cond_s = m2.group(2).strip()
            post_s = m2.group(3).strip()
            brace_start = rest.index('{')
            body, _ = _extract_block(rest[brace_start:])
            if init_s:
                self._run_stmt(init_s)
            guard = 1_000_000
            while True:
                if cond_s and not self._eval(cond_s):
                    break
                try:
                    self._run_block(body)
                except _BreakSignal:
                    break
                except _ContinueSignal:
                    pass
                if post_s:
                    self._run_stmt(post_s)
                guard -= 1
                if guard <= 0:
                    print('[warn] for loop exceeded iteration limit')
                    break
            return

        raise CherryRuntimeError(f'Invalid for statement: {s}')

    def _run_block(self, body: str) -> None:
        for st in split_statements(body):
            st = st.strip()
            if st:
                self._run_stmt(st)

    def _run_undeploy(self, s: str) -> bool:
        _, args = parse_call(s)
        timeout = 5.0
        if len(args) >= 2:
            timeout = float(self._eval(args[1]))
        if not args:
            print('[error] undeploy: missing argument')
            return False
        ctrl = self._eval(args[0])
        ok = undeploy_controller(ctrl, timeout)
        url = getattr(ctrl, 'url', str(ctrl))
        if ok:
            print(f'[info] CherryScript undeployed {url}')
        else:
            print(f'[warn] undeploy: server at {url} did not stop in {timeout}s')
        return ok

    # ── expression evaluator ─────────────────────────────────────────────────

    def _eval(self, expr: str) -> Any:
        expr = expr.strip()
        if not expr:
            return None

        # ---- string literals (single, double, backtick) --------------------
        if _is_str_literal(expr):
            raw = _unquote(expr)
            # template string interpolation: ${...}
            def _interp(m):
                key = m.group(1).strip()
                return str(self._eval(key))
            raw = re.sub(r'\$\{([^}]+)\}', _interp, raw)
            # unescape \\n etc.
            raw = raw.replace('\\n', '\n').replace('\\t', '\t')
            return raw

        # ---- boolean / null ------------------------------------------------
        if expr == 'true':  return True
        if expr == 'false': return False
        if expr == 'null' or expr == 'None': return None

        # ---- numeric literals ----------------------------------------------
        if re.match(r'^-?[0-9]+\.[0-9]+$', expr):
            return float(expr)
        if re.match(r'^-?[0-9]+$', expr):
            return int(expr)

        # ---- array literal  [ ... ] ----------------------------------------
        if expr.startswith('[') and expr.endswith(']'):
            inner = expr[1:-1].strip()
            if not inner:
                return []
            parts = _split_by_comma(inner)
            return [self._eval(p) for p in parts]

        # ---- dict literal   { "key": val, ... } ----------------------------
        if expr.startswith('{') and expr.endswith('}'):
            return self._eval_dict(expr)

        # ---- parenthesised expression --------------------------------------
        if expr.startswith('(') and expr.endswith(')'):
            return self._eval(expr[1:-1])

        # ---- unary not -----------------------------------------------------
        if re.match(r'^not\s+', expr):
            return not self._eval(expr[4:].strip())

        # ---- function / method call (must be checked before property access)
        # Only try when expr looks like a clean call: name(...) where the FIRST '('
        # is matched by the very LAST ')'.
        call_m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_.]*)\s*\(', expr)
        if call_m and expr.endswith(')'):
            # Verify the opening '(' at open_pos is matched by the very last ')'
            open_pos = call_m.end() - 1   # position of the '('
            depth_check = 0
            in_q_check = False
            qchar_check = None
            first_close = -1
            for ci in range(open_pos, len(expr)):
                cc = expr[ci]
                if cc in ('"', "'", '`'):
                    if not in_q_check:
                        in_q_check = True; qchar_check = cc
                    elif qchar_check == cc and (ci == 0 or expr[ci-1] != '\\'):
                        in_q_check = False; qchar_check = None
                    continue
                if not in_q_check:
                    if cc == '(':  depth_check += 1
                    elif cc == ')':
                        depth_check -= 1
                        if depth_check == 0:
                            first_close = ci
                            break
            # The call is valid only if the first '(' closes at the last char
            if first_close == len(expr) - 1:
                try:
                    name, args = parse_call(expr)
                    return self._run_call(name, args)
                except Exception:
                    pass

        # ---- ternary (lowest precedence):  <then> if <cond> else <else_expr>
        ternary = self._find_ternary(expr)
        if ternary is not None:
            then_e, cond_e, else_e = ternary
            return self._eval(then_e) if self._eval(cond_e) else self._eval(else_e)

        # ---- binary logical (and / or) -------------------------------------
        for op_tok in (' and ', ' or '):
            idx = self._find_binary_op(expr, op_tok)
            if idx != -1:
                lhs = self._eval(expr[:idx].strip())
                if op_tok == ' and ':
                    if not lhs:
                        return lhs
                    return self._eval(expr[idx + len(op_tok):].strip())
                else:
                    if lhs:
                        return lhs
                    return self._eval(expr[idx + len(op_tok):].strip())

        # ---- comparison operators ------------------------------------------
        for op in ('==', '!=', '>=', '<=', '>', '<'):
            idx = self._find_binary_op(expr, op)
            if idx != -1:
                lhs = self._eval(expr[:idx].strip())
                rhs = self._eval(expr[idx + len(op):].strip())
                return _compare(lhs, rhs, op)

        # ---- additive arithmetic (+, -) ------------------------------------
        for op in ('+', '-'):
            idx = self._find_binary_op(expr, op)
            if idx != -1:
                lhs_s = expr[:idx].strip()
                rhs_s = expr[idx + len(op):].strip()
                if lhs_s:
                    lhs = self._eval(lhs_s)
                    rhs = self._eval(rhs_s)
                    if op == '+':
                        if isinstance(lhs, str) or isinstance(rhs, str):
                            return str(lhs) + str(rhs)
                        return lhs + rhs
                    else:
                        return lhs - rhs

        # ---- multiplicative arithmetic (*, //, /, %) -----------------------
        for op in ('*', '//', '/', '%'):
            idx = self._find_binary_op(expr, op)
            if idx != -1:
                lhs = self._eval(expr[:idx].strip())
                rhs = self._eval(expr[idx + len(op):].strip())
                if op == '*':
                    if isinstance(lhs, str) and isinstance(rhs, int):
                        return lhs * rhs
                    if isinstance(lhs, int) and isinstance(rhs, str):
                        return rhs * lhs
                    return lhs * rhs
                if op == '//':  return lhs // rhs
                if op == '/':   return lhs / rhs
                if op == '%':   return lhs % rhs

        # ---- exponentiation ------------------------------------------------
        for op in ('**',):
            idx = self._find_binary_op(expr, op)
            if idx != -1:
                lhs = self._eval(expr[:idx].strip())
                rhs = self._eval(expr[idx + len(op):].strip())
                return lhs ** rhs

        # ---- subscript access  expr[key] (handles chaining like a[0][1]["x"]) --
        if '[' in expr and expr.endswith(']'):
            result = self._eval_subscript_chain(expr)
            if result is not _UNRESOLVED:
                return result

        # ---- dotted property access  a.b.c ---------------------------------
        if '.' in expr:
            parts = expr.split('.')
            cur = self.env.get(parts[0])
            if cur is not None or parts[0] in self.env:
                for p in parts[1:]:
                    if isinstance(cur, dict) and p in cur:
                        cur = cur[p]
                    elif hasattr(cur, p):
                        cur = getattr(cur, p)
                    else:
                        cur = None
                        break
                return cur

        # ---- variable lookup -----------------------------------------------
        if expr in self.env:
            return self.env[expr]

        # ---- last resort — unknown token -----------------------------------
        return expr   # return as string so unknown identifiers don't crash

    # ── chained subscript evaluator ──────────────────────────────────────────

    def _eval_subscript_chain(self, expr: str):
        """Evaluate chained subscript expressions like a[0]["x"][1].

        Returns _UNRESOLVED if the expression doesn't fit this pattern.
        """
        # Split off subscript segments from the right
        # e.g. 'a["b"]["c"]' → base='a["b"]', key='"c"'
        # We find the outermost trailing [...] bracket pair
        if not expr.endswith(']'):
            return _UNRESOLVED

        # find the matching '[' for the last ']'
        depth = 0
        in_q = False
        qchar = None
        bracket_start = -1
        for i in range(len(expr) - 1, -1, -1):
            c = expr[i]
            # Note: scanning backwards, so quote tracking is simplified
            if c in ('"', "'", '`') and (i == 0 or expr[i-1] != '\\'):
                in_q = not in_q
                continue
            if not in_q:
                if c == ']':
                    depth += 1
                elif c == '[':
                    depth -= 1
                    if depth == 0:
                        bracket_start = i
                        break

        if bracket_start <= 0:
            return _UNRESOLVED

        base_expr = expr[:bracket_start].strip()
        key_expr  = expr[bracket_start + 1:-1].strip()

        obj = self._eval(base_expr)
        if obj is _UNRESOLVED:
            return _UNRESOLVED

        key = self._eval(key_expr)
        try:
            return obj[key]
        except (KeyError, IndexError, TypeError):
            return None

    # ── dict literal evaluator ───────────────────────────────────────────────

    def _eval_dict(self, expr: str) -> Dict:
        inner = expr[1:-1].strip()
        if not inner:
            return {}
        pairs = _split_by_comma(inner)
        result = {}
        for pair in pairs:
            # split on first ':'
            colon = pair.index(':')
            k = self._eval(pair[:colon].strip())
            v = self._eval(pair[colon + 1:].strip())
            result[k] = v
        return result

    # ── ternary expression finder ─────────────────────────────────────────────

    def _find_ternary(self, expr: str):
        """Find a top-level Python-style ternary: <then> if <cond> else <default>.

        Returns (then_expr, cond_expr, else_expr) or None.
        """
        # Find all top-level ' if ' positions
        if_positions = []
        depth = 0
        in_q = False
        qchar = None
        i = 0
        while i < len(expr):
            c = expr[i]
            if c in ('"', "'", '`'):
                if not in_q:
                    in_q = True; qchar = c
                elif qchar == c and (i == 0 or expr[i-1] != '\\'):
                    in_q = False; qchar = None
                i += 1; continue
            if not in_q:
                if c in ('(', '[', '{'):
                    depth += 1
                elif c in (')', ']', '}'):
                    depth -= 1
                elif depth == 0 and expr[i:i+4] == ' if ':
                    if_positions.append(i)
            i += 1

        for if_pos in reversed(if_positions):
            then_e = expr[:if_pos].strip()
            rest   = expr[if_pos+4:]   # skip ' if '
            # Find top-level ' else ' in rest
            depth2 = 0
            in_q2 = False
            qchar2 = None
            j = 0
            while j < len(rest):
                c = rest[j]
                if c in ('"', "'", '`'):
                    if not in_q2:
                        in_q2 = True; qchar2 = c
                    elif qchar2 == c and (j == 0 or rest[j-1] != '\\'):
                        in_q2 = False; qchar2 = None
                    j += 1; continue
                if not in_q2:
                    if c in ('(', '[', '{'):
                        depth2 += 1
                    elif c in (')', ']', '}'):
                        depth2 -= 1
                    elif depth2 == 0 and rest[j:j+6] == ' else ':
                        cond_e = rest[:j].strip()
                        else_e = rest[j+6:].strip()
                        if then_e and cond_e and else_e:
                            return then_e, cond_e, else_e
                j += 1
        return None

    # ── binary op search (respects quotes/brackets) ──────────────────────────

    def _find_binary_op(self, expr: str, op: str) -> int:
        """Return the index of the rightmost top-level occurrence of op,
        or -1 if not found.  Uses rightmost to achieve left-associativity."""
        depth = 0
        in_q = False
        qchar = None
        last = -1
        i = 0
        while i < len(expr):
            c = expr[i]
            if c in ('"', "'", '`'):
                if not in_q:
                    in_q = True; qchar = c
                elif qchar == c and (i == 0 or expr[i-1] != '\\'):
                    in_q = False; qchar = None
                i += 1; continue
            if not in_q:
                if c in ('(', '[', '{'):
                    depth += 1
                elif c in (')', ']', '}'):
                    depth -= 1
                elif depth == 0 and expr[i:i+len(op)] == op:
                    # For '-' ensure it's not a negative sign (no left operand
                    # or preceded by operator)
                    if op == '-':
                        left = expr[:i].strip()
                        if not left or left[-1] in ('+', '-', '*', '/', '(', ',', '='):
                            i += 1; continue
                    # For '+' skip if inside string already handled
                    last = i
                    # For single-char ops we want rightmost to handle
                    # left-associativity, but for multi-char ops just take first
                    if len(op) > 1:
                        return last
                    i += 1; continue
            i += 1
        return last

    # ── built-in function / method call dispatcher ───────────────────────────

    def _run_call(self, name: str, args: List[str]) -> Any:

        # ---- print ---------------------------------------------------------
        if name == 'print':
            parts = [self._eval(a) for a in args]
            print(*parts)
            return None

        # ---- len -----------------------------------------------------------
        if name == 'len':
            v = self._eval(args[0]) if args else None
            if v is None:
                return 0
            return len(v)

        # ---- range ---------------------------------------------------------
        if name == 'range':
            vals = [int(self._eval(a)) for a in args]
            if len(vals) == 1:
                return list(range(vals[0]))
            if len(vals) == 2:
                return list(range(vals[0], vals[1]))
            if len(vals) >= 3:
                return list(range(vals[0], vals[1], vals[2]))
            return []

        # ---- sum -----------------------------------------------------------
        if name == 'sum':
            v = self._eval(args[0]) if args else []
            return sum(v) if v else 0

        # ---- min / max -----------------------------------------------------
        if name == 'min':
            if len(args) == 1:
                v = self._eval(args[0])
                return min(v)
            return min(self._eval(a) for a in args)

        if name == 'max':
            if len(args) == 1:
                v = self._eval(args[0])
                return max(v)
            return max(self._eval(a) for a in args)

        # ---- format --------------------------------------------------------
        if name == 'format':
            val = self._eval(args[0])
            fmt = _unquote(args[1]) if len(args) > 1 else ''
            try:
                return format(val, fmt)
            except Exception:
                return str(val)

        # ---- time ----------------------------------------------------------
        if name == 'time':
            return _time.strftime('%Y-%m-%d %H:%M:%S')

        # ---- append --------------------------------------------------------
        if name == 'append':
            lst = self._eval(args[0])
            item = self._eval(args[1]) if len(args) > 1 else None
            if isinstance(lst, list):
                lst.append(item)
            return lst

        # ---- keys ----------------------------------------------------------
        if name == 'keys':
            v = self._eval(args[0]) if args else {}
            return list(v.keys()) if isinstance(v, dict) else []

        # ---- connect (database) --------------------------------------------
        if name == 'connect':
            uri  = self._eval(args[0])
            user = self._eval(args[1]) if len(args) > 1 else None
            pwd  = self._eval(args[2]) if len(args) > 2 else None
            return Database(uri, user, pwd)

        # ---- h2o.frame -----------------------------------------------------
        if name == 'h2o.frame':
            val = self._eval(args[0]) if args else []
            return to_frame(val)

        # ---- h2o.preprocess ------------------------------------------------
        if name == 'h2o.preprocess':
            return self._eval(args[0]) if args else None

        # ---- h2o.automl ----------------------------------------------------
        if name == 'h2o.automl':
            frame  = self._eval(args[0]) if args else Frame([])
            target = self._eval(args[1]) if len(args) > 1 else None
            return automl_train(frame, target)

        # ---- deploy --------------------------------------------------------
        if name == 'deploy':
            model   = self._eval(args[0]) if args else None
            url_arg = self._eval(args[1]) if len(args) > 1 else 'http://127.0.0.1:8080/predict'
            return deploy_model(model, url_arg)

        # ---- undeploy (function-call form) ---------------------------------
        if name == 'undeploy':
            ctrl    = self._eval(args[0]) if args else None
            timeout = float(self._eval(args[1])) if len(args) > 1 else 5.0
            ok = undeploy_controller(ctrl, timeout)
            url = getattr(ctrl, 'url', str(ctrl))
            if ok:
                print(f'[info] CherryScript undeployed {url}')
            else:
                print(f'[warn] undeploy: server at {url} did not stop in {timeout}s')
            return ok

        # ---- dotted method calls (db.query, model.predict, frame.describe …)
        if '.' in name:
            parts = name.split('.')
            # Resolve the object: walk through all-but-last-segment as
            # property path, last segment is the method name.
            obj = self.env.get(parts[0])
            for attr in parts[1:-1]:
                if obj is None:
                    break
                if isinstance(obj, dict) and attr in obj:
                    obj = obj[attr]
                elif hasattr(obj, attr):
                    obj = getattr(obj, attr)
                else:
                    obj = None
            method = parts[-1]

            # db.query
            if method == 'query' and isinstance(obj, Database):
                sql = self._eval(args[0])
                return obj.query(sql)

            # model.predict
            if method == 'predict' and isinstance(obj, Model):
                frame = self._eval(args[0]) if args else Frame([])
                return obj.predict(frame)

            # frame.describe
            if method == 'describe' and isinstance(obj, Frame):
                return obj.describe()

            # obj.get(key, default) — for dicts
            if method == 'get':
                key_val = self._eval(args[0]) if args else None
                default = self._eval(args[1]) if len(args) > 1 else None
                if isinstance(obj, dict):
                    return obj.get(key_val, default)
                return default

            # str.replace
            if method == 'replace' and isinstance(obj, str):
                a = self._eval(args[0]) if args else ''
                b = self._eval(args[1]) if len(args) > 1 else ''
                return obj.replace(a, b)

            # list.append
            if method == 'append' and isinstance(obj, list):
                item = self._eval(args[0]) if args else None
                obj.append(item)
                return obj

            if method == 'keys' and isinstance(obj, dict):
                return list(obj.keys())

            # generic attribute + call
            attr = getattr(obj, method, None)
            if callable(attr):
                evaluated_args = [self._eval(a) for a in args]
                return attr(*evaluated_args)
            if attr is not None:
                return attr

        # ---- user-defined function call ------------------------------------
        if name in self._functions:
            fn = self._functions[name]
            params = fn['params']
            body   = fn['body']
            evaluated_args = [self._eval(a) for a in args]
            # create a new scope (shallow copy of env)
            saved_env = dict(self.env)
            for p, v in zip(params, evaluated_args):
                self.env[p] = v
            result = None
            try:
                for st in split_statements(body):
                    st = st.strip()
                    if st:
                        self._run_stmt(st)
            except _ReturnSignal as ret:
                result = ret.value
            finally:
                self.env = saved_env
            return result

        # ---- unknown -------------------------------------------------------
        print(f'[warn] Unknown function: {name}')
        return None


# ── Signals (used for return / break / continue) ─────────────────────────────

class _ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class _BreakSignal(Exception):
    pass

class _ContinueSignal(Exception):
    pass


# ── Block / condition extraction helpers ─────────────────────────────────────

def _extract_block(text: str):
    """Extract content inside the first matching { } and return (body, rest)."""
    text = text.lstrip()
    if not text.startswith('{'):
        raise CherryRuntimeError(f'Expected {{ but got: {text[:30]!r}')
    depth = 0
    in_q = False
    qchar = None
    for i, c in enumerate(text):
        if c in ('"', "'", '`'):
            if not in_q:
                in_q = True; qchar = c
            elif qchar == c and (i == 0 or text[i-1] != '\\'):
                in_q = False; qchar = None
            continue
        if not in_q:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return text[1:i], text[i+1:]
    raise CherryRuntimeError('Unterminated block')


def _extract_condition(text: str):
    """Extract condition (with optional surrounding parens) from start of text.

    Returns (condition_string, remainder_string).
    """
    text = text.lstrip()
    if text.startswith('('):
        # find matching ')'
        depth = 0
        in_q = False
        qchar = None
        for i, c in enumerate(text):
            if c in ('"', "'", '`'):
                if not in_q:
                    in_q = True; qchar = c
                elif qchar == c:
                    in_q = False; qchar = None
                continue
            if not in_q:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        return text[1:i], text[i+1:]
        raise CherryRuntimeError('Unterminated condition')

    # no parentheses — condition ends at the first '{'
    brace_idx = text.index('{')
    return text[:brace_idx].strip(), text[brace_idx:]


def _compare(lhs: Any, rhs: Any, op: str) -> bool:
    try:
        if op == '==': return lhs == rhs
        if op == '!=': return lhs != rhs
        if op == '>':  return lhs > rhs
        if op == '<':  return lhs < rhs
        if op == '>=': return lhs >= rhs
        if op == '<=': return lhs <= rhs
    except TypeError:
        return False
    return False


if __name__ == '__main__':
    print('CherryScript runtime loaded')
