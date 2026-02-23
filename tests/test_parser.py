"""Tests for the CherryScript parser."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from cherryscript.parser import split_statements, parse_call, _split_by_comma


class TestSplitStatements:
    def test_simple_newline(self):
        src = "var x = 1\nvar y = 2"
        stmts = split_statements(src)
        assert stmts == ["var x = 1", "var y = 2"]

    def test_semicolons(self):
        src = "var x = 1; var y = 2"
        stmts = split_statements(src)
        assert stmts == ["var x = 1", "var y = 2"]

    def test_block_kept_together(self):
        src = 'if (x > 0) {\n  print("yes")\n}'
        stmts = split_statements(src)
        assert len(stmts) == 1

    def test_comments_stripped(self):
        src = "var x = 1 // this is x\nvar y = 2"
        stmts = split_statements(src)
        assert stmts == ["var x = 1", "var y = 2"]

    def test_block_comments(self):
        src = "/* comment */\nvar x = 1"
        stmts = split_statements(src)
        assert "var x = 1" in stmts

    def test_string_with_brace(self):
        src = 'var s = "hello{world}"\nvar n = 1'
        stmts = split_statements(src)
        assert len(stmts) == 2


class TestParseCall:
    def test_no_args(self):
        name, args = parse_call("time()")
        assert name == "time"
        assert args == []

    def test_one_arg(self):
        name, args = parse_call('print("hello")')
        assert name == "print"
        assert args == ['"hello"']

    def test_multiple_args(self):
        name, args = parse_call('connect("mysql://host", "user", "pass")')
        assert name == "connect"
        assert len(args) == 3

    def test_dotted_name(self):
        name, args = parse_call('db.query("SELECT 1")')
        assert name == "db.query"

    def test_nested_call(self):
        name, args = parse_call('h2o.automl(h2o.frame(data), "target")')
        assert name == "h2o.automl"
        assert len(args) == 2
