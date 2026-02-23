"""Advanced parser for CherryScript with full syntax support"""
import re
from typing import List, Tuple, Optional


class ParseError(Exception):
    """Raised when parsing fails"""
    pass


def split_statements(text: str) -> List[str]:
    """Split code into statements, handling quotes, braces, and comments.

    Newlines inside brace blocks are kept together so that multi-line
    constructs (if/while/for/fn) are returned as a single statement.
    Top-level newlines act as statement terminators just like semicolons.
    """
    if not text.strip():
        return []

    parts = []
    cur = []
    depth = 0       # brace depth
    in_q = False
    qchar = None
    i = 0

    while i < len(text):
        c = text[i]

        # ---------- quote tracking ----------
        if c in ('"', "'", '`'):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c:
                # escaped quote inside string?
                if i > 0 and text[i - 1] == '\\':
                    cur.append(c)
                    i += 1
                    continue
                in_q = False
                qchar = None
            cur.append(c)
            i += 1
            continue

        # ---------- brace/bracket depth (only outside strings) ----------
        if not in_q and c in ('{', '[', '('):
            depth += 1
            cur.append(c)
            i += 1
            continue

        if not in_q and c in ('}', ']', ')'):
            depth = max(0, depth - 1)
            cur.append(c)
            i += 1
            continue

        # ---------- line comments (// …) ----------
        if not in_q and depth == 0 and c == '/' and i + 1 < len(text) and text[i + 1] == '/':
            # Flush whatever was accumulated before the comment
            stmt = ''.join(cur).strip()
            if stmt:
                parts.append(stmt)
            cur = []
            # Skip to end of line
            while i < len(text) and text[i] != '\n':
                i += 1
            # consume the newline too
            if i < len(text):
                i += 1
            continue

        # ---------- block comments (/* … */) ----------
        if not in_q and depth == 0 and c == '/' and i + 1 < len(text) and text[i + 1] == '*':
            i += 2
            while i < len(text) - 1:
                if text[i] == '*' and text[i + 1] == '/':
                    i += 2
                    break
                i += 1
            continue

        # ---------- semicolon — statement terminator, EXCEPT inside a C-style for header ----------
        # A C-style for loop uses semicolons as separators: for init; cond; post { … }
        # We must NOT split on ';' when the current buffer starts with 'for '.
        if not in_q and depth == 0 and c == ';':
            cur_text = ''.join(cur).strip()
            if re.match(r'^for\s+', cur_text):
                # Inside a C-style for header — keep the semicolon as part of the token
                cur.append(c)
                i += 1
                continue
            if cur_text:
                parts.append(cur_text)
            cur = []
            i += 1
            continue

        # ---------- newline — only a terminator at top level ----------
        if not in_q and depth == 0 and c == '\n':
            stmt = ''.join(cur).strip()
            if stmt:
                parts.append(stmt)
            cur = []
            i += 1
            continue

        cur.append(c)
        i += 1

    # Handle any trailing content
    leftover = ''.join(cur).strip()
    if leftover:
        parts.append(leftover)

    return parts


def parse_call(text: str) -> Tuple[str, List[str]]:
    """Parse function call syntax: name(arg1, arg2, ...)

    Returns (name, [arg_strings]).
    """
    text = text.strip()

    if '(' not in text:
        raise ParseError(f"Not a function call: {text}")

    # Find the first '(' that starts the argument list (name may contain dots)
    paren_pos = -1
    depth = 0
    in_q = False
    qchar = None

    for i, c in enumerate(text):
        if c in ('"', "'", '`'):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c and (i == 0 or text[i - 1] != '\\'):
                in_q = False
                qchar = None
            continue

        if not in_q:
            if c == '(':
                if depth == 0:
                    paren_pos = i
                depth += 1
            elif c == ')':
                depth -= 1
                if depth < 0:
                    raise ParseError(f"Unbalanced parentheses in: {text}")

    if depth != 0:
        raise ParseError(f"Unbalanced parentheses in: {text}")
    if paren_pos == -1:
        raise ParseError(f"Not a function call: {text}")

    name = text[:paren_pos].strip()
    # The closing ')' is the last character
    args_text = text[paren_pos + 1:-1].strip()

    if not args_text:
        return name, []

    args = _split_by_comma(args_text)
    return name, args


def _split_by_comma(s: str) -> List[str]:
    """Split a string on top-level commas (respecting quotes and brackets)."""
    parts = []
    cur: List[str] = []
    in_q = False
    qchar = None
    depth = 0
    i = 0

    while i < len(s):
        c = s[i]
        if c in ('"', "'", '`'):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c and (i == 0 or s[i - 1] != '\\'):
                in_q = False
                qchar = None
            cur.append(c)
            i += 1
            continue
        if not in_q and c in ('(', '[', '{'):
            depth += 1
            cur.append(c)
            i += 1
            continue
        if not in_q and c in (')', ']', '}'):
            depth = max(0, depth - 1)
            cur.append(c)
            i += 1
            continue
        if not in_q and depth == 0 and c == ',':
            arg_str = ''.join(cur).strip()
            if arg_str:
                parts.append(arg_str)
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1

    if cur:
        arg_str = ''.join(cur).strip()
        if arg_str:
            parts.append(arg_str)

    return parts


def parse_assignment(text: str) -> Tuple[str, str]:
    """Parse variable assignment: var x = value or x = value"""
    text = text.strip()

    var_match = re.match(r'^(?:var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', text, re.S)
    if var_match:
        return var_match.group(1), var_match.group(2)

    assign_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', text, re.S)
    if assign_match:
        return assign_match.group(1), assign_match.group(2)

    raise ParseError(f"Invalid assignment: {text}")
