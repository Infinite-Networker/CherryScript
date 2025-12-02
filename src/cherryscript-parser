"""Advanced parser for CherryScript with full syntax support"""
import re
from typing import List, Tuple, Optional

class ParseError(Exception):
    """Raised when parsing fails"""
    pass

def split_statements(text: str) -> List[str]:
    """Split code into statements, handling quotes, braces, and comments"""
    if not text.strip():
        return []
    
    parts = []
    cur = []
    depth = 0
    in_q = False
    qchar = None
    i = 0
    
    while i < len(text):
        c = text[i]
        
        # Handle quotes
        if c in ('"', "'"):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c:
                # Check for escape
                if i > 0 and text[i-1] == '\\':
                    cur.append(c)
                    i += 1
                    continue
                in_q = False
                qchar = None
            cur.append(c)
            i += 1
            continue
        
        # Handle braces
        if not in_q and c == '{':
            depth += 1
            cur.append(c)
            i += 1
            continue
            
        if not in_q and c == '}':
            depth = max(0, depth - 1)
            cur.append(c)
            i += 1
            continue
        
        # Handle line comments
        if not in_q and depth == 0 and c == '/' and i + 1 < len(text) and text[i+1] == '/':
            # Skip to end of line
            while i < len(text) and text[i] != '\n':
                i += 1
            if i < len(text):
                i += 1
            continue
        
        # Handle block comments
        if not in_q and depth == 0 and c == '/' and i + 1 < len(text) and text[i+1] == '*':
            # Skip until */
            i += 2
            while i < len(text) - 1:
                if text[i] == '*' and text[i+1] == '/':
                    i += 2
                    break
                i += 1
            continue
        
        # Split on semicolon when not in quotes/braces
        if not in_q and depth == 0 and c == ';':
            stmt = ''.join(cur).strip()
            if stmt:
                parts.append(stmt)
            cur = []
            i += 1
            continue
        
        # Handle newlines (statement terminators when not in braces)
        if not in_q and depth == 0 and c == '\n':
            stmt = ''.join(cur).strip()
            if stmt:
                parts.append(stmt)
            cur = []
            i += 1
            continue
            
        cur.append(c)
        i += 1
    
    # Handle final statement
    leftover = ''.join(cur).strip()
    if leftover:
        parts.append(leftover)
    
    return parts

def parse_call(text: str) -> Tuple[str, List[str]]:
    """Parse function call syntax: name(arg1, arg2, ...)"""
    text = text.strip()
    
    # Find matching parentheses
    if not text.endswith(')'):
        raise ParseError(f"Unclosed function call: {text}")
    
    # Find the opening parenthesis
    paren_pos = -1
    depth = 0
    in_q = False
    qchar = None
    
    for i, c in enumerate(text):
        if c in ('"', "'"):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c:
                if i > 0 and text[i-1] != '\\':
                    in_q = False
                    qchar = None
            continue
        
        if not in_q and c == '(':
            if depth == 0:
                paren_pos = i
            depth += 1
        elif not in_q and c == ')':
            depth -= 1
            if depth < 0:
                raise ParseError(f"Unbalanced parentheses in: {text}")
    
    if depth != 0:
        raise ParseError(f"Unbalanced parentheses in: {text}")
    
    if paren_pos == -1:
        raise ParseError(f"Not a function call: {text}")
    
    name = text[:paren_pos].strip()
    args_text = text[paren_pos+1:-1].strip()
    
    if not args_text:
        return name, []
    
    # Parse arguments
    args = []
    cur_arg = []
    depth = 0
    in_q = False
    qchar = None
    
    i = 0
    while i < len(args_text):
        c = args_text[i]
        
        if c in ('"', "'"):
            if not in_q:
                in_q = True
                qchar = c
            elif qchar == c:
                if i > 0 and args_text[i-1] != '\\':
                    in_q = False
                    qchar = None
            cur_arg.append(c)
            i += 1
            continue
        
        if not in_q and c == '(':
            depth += 1
            cur_arg.append(c)
            i += 1
            continue
            
        if not in_q and c == ')':
            depth -= 1
            cur_arg.append(c)
            i += 1
            continue
        
        if not in_q and depth == 0 and c == ',':
            arg_str = ''.join(cur_arg).strip()
            if arg_str:
                args.append(arg_str)
            cur_arg = []
            i += 1
            continue
        
        cur_arg.append(c)
        i += 1
    
    # Add final argument
    if cur_arg:
        arg_str = ''.join(cur_arg).strip()
        if arg_str:
            args.append(arg_str)
    
    return name, args

def parse_assignment(text: str) -> Tuple[str, str]:
    """Parse variable assignment: var x = value or x = value"""
    text = text.strip()
    
    # Match variable declaration
    var_match = re.match(r'^(var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', text, re.S)
    if var_match:
        return var_match.group(2), var_match.group(3)
    
    # Match regular assignment
    assign_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$', text, re.S)
    if assign_match:
        return assign_match.group(1), assign_match.group(2)
    
    raise ParseError(f"Invalid assignment: {text}")
