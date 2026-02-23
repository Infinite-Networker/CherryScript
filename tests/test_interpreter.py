"""Tests for the CherryScript interpreter."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from cherryscript.runtime.interpreter import Runtime


def make_rt():
    return Runtime()


class TestVariables:
    def test_var_integer(self):
        rt = make_rt()
        rt.run("var x = 42")
        assert rt.env["x"] == 42

    def test_var_float(self):
        rt = make_rt()
        rt.run("var x = 3.14")
        assert abs(rt.env["x"] - 3.14) < 1e-9

    def test_var_string(self):
        rt = make_rt()
        rt.run('var s = "hello"')
        assert rt.env["s"] == "hello"

    def test_var_bool_true(self):
        rt = make_rt()
        rt.run("var b = true")
        assert rt.env["b"] is True

    def test_var_bool_false(self):
        rt = make_rt()
        rt.run("var b = false")
        assert rt.env["b"] is False

    def test_let_declaration(self):
        rt = make_rt()
        rt.run("let n = 100")
        assert rt.env["n"] == 100

    def test_assignment(self):
        rt = make_rt()
        rt.run("var x = 1\nx = 99")
        assert rt.env["x"] == 99

    def test_compound_add(self):
        rt = make_rt()
        rt.run("var x = 10\nx += 5")
        assert rt.env["x"] == 15

    def test_compound_sub(self):
        rt = make_rt()
        rt.run("var x = 10\nx -= 3")
        assert rt.env["x"] == 7

    def test_array_literal(self):
        rt = make_rt()
        rt.run('var arr = [1, 2, 3]')
        assert rt.env["arr"] == [1, 2, 3]

    def test_dict_literal(self):
        rt = make_rt()
        rt.run('var d = {"key": "val"}')
        assert rt.env["d"] == {"key": "val"}


class TestArithmetic:
    def test_addition(self):
        rt = make_rt()
        rt.run("var x = 3 + 4")
        assert rt.env["x"] == 7

    def test_subtraction(self):
        rt = make_rt()
        rt.run("var x = 10 - 3")
        assert rt.env["x"] == 7

    def test_multiplication(self):
        rt = make_rt()
        rt.run("var x = 3 * 4")
        assert rt.env["x"] == 12

    def test_division(self):
        rt = make_rt()
        rt.run("var x = 10 / 4")
        assert rt.env["x"] == 2.5

    def test_string_concat(self):
        rt = make_rt()
        rt.run('var s = "hello" + " " + "world"')
        assert rt.env["s"] == "hello world"

    def test_string_repeat(self):
        rt = make_rt()
        rt.run('var s = "ab" * 3')
        assert rt.env["s"] == "ababab"


class TestControlFlow:
    def test_if_true(self, capsys):
        rt = make_rt()
        rt.run('var x = 5\nif (x > 3) {\nprint("yes")\n}')
        out = capsys.readouterr().out
        assert "yes" in out

    def test_if_false_else(self, capsys):
        rt = make_rt()
        rt.run('var x = 1\nif (x > 3) {\nprint("yes")\n} else {\nprint("no")\n}')
        out = capsys.readouterr().out
        assert "no" in out

    def test_while(self):
        rt = make_rt()
        rt.run("var i = 0\nwhile (i < 5) {\ni += 1\n}")
        assert rt.env["i"] == 5

    def test_for_in(self):
        rt = make_rt()
        rt.run("var total = 0\nfor x in [1, 2, 3] {\ntotal = total + x\n}")
        assert rt.env["total"] == 6

    def test_c_for(self):
        rt = make_rt()
        rt.run("var s = 0\nfor var i = 0; i < 4; i += 1 {\ns = s + i\n}")
        assert rt.env["s"] == 6   # 0+1+2+3


class TestBuiltins:
    def test_len_list(self):
        rt = make_rt()
        rt.run("var arr = [1, 2, 3]\nvar n = len(arr)")
        assert rt.env["n"] == 3

    def test_len_string(self):
        rt = make_rt()
        rt.run('var n = len("hello")')
        assert rt.env["n"] == 5

    def test_range(self):
        rt = make_rt()
        rt.run("var r = range(5)")
        assert rt.env["r"] == [0, 1, 2, 3, 4]

    def test_range_start_stop(self):
        rt = make_rt()
        rt.run("var r = range(2, 5)")
        assert rt.env["r"] == [2, 3, 4]

    def test_sum(self):
        rt = make_rt()
        rt.run("var s = sum([1, 2, 3, 4])")
        assert rt.env["s"] == 10

    def test_min(self):
        rt = make_rt()
        rt.run("var m = min([3, 1, 4, 1, 5])")
        assert rt.env["m"] == 1

    def test_max(self):
        rt = make_rt()
        rt.run("var m = max([3, 1, 4, 1, 5])")
        assert rt.env["m"] == 5

    def test_format(self):
        rt = make_rt()
        rt.run('var s = format(3.14159, ".2f")')
        assert rt.env["s"] == "3.14"

    def test_time(self):
        rt = make_rt()
        rt.run("var t = time()")
        assert isinstance(rt.env["t"], str) and len(rt.env["t"]) > 0


class TestStringInterpolation:
    def test_backtick_interpolation(self, capsys):
        rt = make_rt()
        rt.run('var name = "World"\nprint(`Hello ${name}!`)')
        out = capsys.readouterr().out
        assert "Hello World!" in out


class TestFunctions:
    def test_fn_definition_and_call(self):
        rt = make_rt()
        rt.run("fn double(x) {\nreturn x * 2\n}\nvar r = double(7)")
        assert rt.env["r"] == 14

    def test_fn_with_if(self):
        rt = make_rt()
        rt.run("""fn abs_val(n) {
if (n < 0) {
return n * -1
} else {
return n
}
}
var r = abs_val(-5)""")
        assert rt.env["r"] == 5

    def test_fn_scope_isolation(self):
        rt = make_rt()
        rt.run("var x = 100\nfn foo(x) {\nreturn x + 1\n}\nvar r = foo(3)")
        assert rt.env["x"] == 100
        assert rt.env["r"] == 4


class TestDatabase:
    def test_connect_mock(self):
        rt = make_rt()
        rt.run('var db = connect("mysql://localhost/test")')
        from cherryscript.runtime.adapters import Database
        assert isinstance(rt.env["db"], Database)

    def test_query_mock(self):
        rt = make_rt()
        rt.run('var db = connect("mysql://localhost/test")\nvar rows = db.query("SELECT * FROM orders")')
        assert isinstance(rt.env["rows"], list)
        assert len(rt.env["rows"]) > 0


class TestML:
    def test_h2o_frame(self):
        rt = make_rt()
        rt.run('var data = [{"a": 1}, {"a": 2}]\nvar frame = h2o.frame(data)')
        from cherryscript.runtime.adapters import Frame
        assert isinstance(rt.env["frame"], Frame)

    def test_automl_train(self):
        rt = make_rt()
        rt.run("""var data = [{"x": 1, "y": 0}, {"x": 2, "y": 1}]
var frame = h2o.frame(data)
var model = h2o.automl(frame, "y")""")
        from cherryscript.runtime.adapters import Model
        assert isinstance(rt.env["model"], Model)

    def test_model_predict(self):
        rt = make_rt()
        rt.run("""var data = [{"purchase_frequency": 5, "income": 80000}]
var frame = h2o.frame(data)
var model = h2o.automl(frame, "churned")
var preds = model.predict(h2o.frame([{"purchase_frequency": 1, "income": 40000}]))""")
        assert isinstance(rt.env["preds"], list)
        assert len(rt.env["preds"]) == 1
