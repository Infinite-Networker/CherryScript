"""
Comprehensive parser utilities for CherryScript - A dynamic scripting language for data science and automation

This module provides robust parsing capabilities for CherryScript, including:
- Statement splitting with proper handling of quotes, braces, and comments
- Function call parsing with support for complex arguments
- Error handling for malformed syntax
- Type hints for better developer experience
"""

import re
from typing import List, Tuple, Optional, Dict, Any

class ParseError(Exception):
    """Exception raised when parsing fails due to invalid syntax"""
    def __init__(self, message: str, position: Optional[int] = None, line: Optional[int] = None):
        self.message = message
        self.position = position
        self.line = line
        super().__init__(f"ParseError: {message}" + (f" at position {position}" if position else "") + (f" on line {line}" if line else ""))


def split_statements(text: str) -> List[str]:
    """
    Split CherryScript code into individual statements, respecting quotes, braces, and comments.
    
    This function handles:
    - Semicolon-separated statements
    - String literals (both single and double quotes)
    - Braces for code blocks
    - Line comments (//) and block comments (/* */)
    
    Args:
        text (str): The CherryScript source code to parse
        
    Returns:
        List[str]: List of individual statements
        
    Raises:
        ParseError: If there are unmatched quotes or braces
    """
    if not text.strip():
        return []
    
    parts = []
    current_statement = []
    brace_depth = 0
    bracket_depth = 0
    paren_depth = 0
    in_string = False
    string_char = None
    in_comment = False
    in_block_comment = False
    line_number = 1
    char_position = 0
    
    i = 0
    text_length = len(text)
    
    while i < text_length:
        char = text[i]
        char_position += 1
        
        # Handle newlines for line counting
        if char == '\n':
            line_number += 1
            char_position = 0
        
        # Skip characters inside block comments
        if in_block_comment:
            if char == '*' and i + 1 < text_length and text[i + 1] == '/':
                in_block_comment = False
                i += 2  # Skip the '*/'
                char_position += 2
                continue
            i += 1
            char_position += 1
            continue
        
        # Handle line comments
        if not in_string and char == '/' and i + 1 < text_length:
            if text[i + 1] == '/':
                # Line comment - skip to end of line
                while i < text_length and text[i] != '\n':
                    i += 1
                    char_position += 1
                continue
            elif text[i + 1] == '*':
                # Start of block comment
                in_block_comment = True
                i += 2
                char_position += 2
                continue
        
        # Handle string literals
        if char in ('"', "'"):
            if not in_string:
                # Start of string
                in_string = True
                string_char = char
                current_statement.append(char)
            elif string_char == char:
                # Check for escaped quote
                if i > 0 and text[i - 1] == '\\':
                    current_statement.append(char)
                else:
                    # End of string
                    in_string = False
                    string_char = None
                    current_statement.append(char)
            else:
                # Different quote character inside string
                current_statement.append(char)
            i += 1
            continue
        
        # Handle braces, brackets, and parentheses
        if not in_string:
            if char == '{':
                brace_depth += 1
            elif char == '}':
                if brace_depth == 0:
                    raise ParseError(f"Unmatched closing brace '}}'", position=char_position, line=line_number)
                brace_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                if bracket_depth == 0:
                    raise ParseError(f"Unmatched closing bracket ']'", position=char_position, line=line_number)
                bracket_depth -= 1
            elif char == '(':
                paren_depth += 1
            elif char == ')':
                if paren_depth == 0:
                    raise ParseError(f"Unmatched closing parenthesis ')'", position=char_position, line=line_number)
                paren_depth -= 1
        
        # Check for statement separator when not in string or any nested structure
        if not in_string and brace_depth == 0 and bracket_depth == 0 and paren_depth == 0:
            if char == ';':
                # End of statement
                statement_text = ''.join(current_statement).strip()
                if statement_text:
                    parts.append(statement_text)
                current_statement = []
                i += 1
                continue
            
            # Also split on newlines when not in any block (simplifies REPL)
            if char == '\n':
                statement_text = ''.join(current_statement).strip()
                if statement_text and not statement_text.endswith('\\'):
                    # Check if it's a continuation line
                    parts.append(statement_text)
                    current_statement = []
                    i += 1
                    continue
        
        current_statement.append(char)
        i += 1
    
    # Handle any remaining text
    if in_string:
        raise ParseError("Unclosed string literal", position=char_position, line=line_number)
    
    if in_block_comment:
        raise ParseError("Unclosed block comment", position=char_position, line=line_number)
    
    if brace_depth > 0:
        raise ParseError(f"Unclosed brace(s) - {brace_depth} missing", position=char_position, line=line_number)
    
    if bracket_depth > 0:
        raise ParseError(f"Unclosed bracket(s) - {bracket_depth} missing", position=char_position, line=line_number)
    
    if paren_depth > 0:
        raise ParseError(f"Unclosed parenthesis - {paren_depth} missing", position=char_position, line=line_number)
    
    # Add the final statement if any
    final_statement = ''.join(current_statement).strip()
    if final_statement:
        parts.append(final_statement)
    
    return parts


def parse_call(text: str) -> Tuple[str, List[str]]:
    """
    Parse a function call expression into function name and arguments.
    
    This function handles:
    - Function names with dots (method calls, e.g., db.query())
    - Complex arguments including nested function calls
    - String literals as arguments
    - Proper handling of whitespace
    
    Args:
        text (str): The function call expression (e.g., "print('hello', 42)")
        
    Returns:
        Tuple[str, List[str]]: Tuple containing function name and list of argument strings
        
    Raises:
        ParseError: If the function call syntax is invalid
    """
    text = text.strip()
    
    # Check if it's a valid function call
    if not text.endswith(')'):
        raise ParseError(f"Function call must end with ')': {text}")
    
    # Find the opening parenthesis
    paren_pos = -1
    depth = 0
    in_string = False
    string_char = None
    escaped = False
    
    for i, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        
        if char == '\\':
            escaped = True
            continue
        
        if char in ('"', "'"):
            if not in_string:
                in_string = True
                string_char = char
            elif string_char == char:
                in_string = False
                string_char = None
            continue
        
        if not in_string and char == '(':
            if depth == 0:
                paren_pos = i
            depth += 1
        elif not in_string and char == ')':
            depth -= 1
    
    if depth != 0:
        raise ParseError(f"Unbalanced parentheses in function call: {text}")
    
    if paren_pos == -1:
        raise ParseError(f"Not a valid function call: {text}")
    
    # Extract function name
    func_name = text[:paren_pos].strip()
    
    # Validate function name
    if not func_name:
        raise ParseError(f"Missing function name in call: {text}")
    
    # Check for valid function name pattern
    func_pattern = r'^[a-zA-Z_][a-zA-Z0-9_\.]*$'
    if not re.match(func_pattern, func_name):
        raise ParseError(f"Invalid function name: {func_name}")
    
    # Extract arguments text
    args_text = text[paren_pos + 1:-1].strip()
    
    # If no arguments, return empty list
    if not args_text:
        return func_name, []
    
    # Parse arguments
    args = []
    current_arg = []
    depth = 0
    in_string = False
    string_char = None
    escaped = False
    
    i = 0
    args_length = len(args_text)
    
    while i < args_length:
        char = args_text[i]
        
        if escaped:
            escaped = False
            current_arg.append(char)
            i += 1
            continue
        
        if char == '\\':
            escaped = True
            current_arg.append(char)
            i += 1
            continue
        
        # Handle string literals
        if char in ('"', "'"):
            if not in_string:
                in_string = True
                string_char = char
            elif string_char == char:
                in_string = False
                string_char = None
            current_arg.append(char)
            i += 1
            continue
        
        # Handle parentheses for nested calls
        if not in_string and char == '(':
            depth += 1
            current_arg.append(char)
            i += 1
            continue
        
        if not in_string and char == ')':
            depth -= 1
            current_arg.append(char)
            i += 1
            continue
        
        # Handle array/object literals
        if not in_string and char == '[':
            depth += 1
            current_arg.append(char)
            i += 1
            continue
        
        if not in_string and char == ']':
            depth -= 1
            current_arg.append(char)
            i += 1
            continue
        
        if not in_string and char == '{':
            depth += 1
            current_arg.append(char)
            i += 1
            continue
        
        if not in_string and char == '}':
            depth -= 1
            current_arg.append(char)
            i += 1
            continue
        
        # Check for argument separator
        if not in_string and depth == 0 and char == ',':
            arg_text = ''.join(current_arg).strip()
            if arg_text:
                args.append(arg_text)
            current_arg = []
            i += 1
            continue
        
        current_arg.append(char)
        i += 1
    
    # Add the final argument
    if current_arg:
        arg_text = ''.join(current_arg).strip()
        if arg_text:
            args.append(arg_text)
    
    return func_name, args


def parse_assignment(text: str) -> Tuple[str, str]:
    """
    Parse an assignment statement into variable name and expression.
    
    Supports:
    - Simple assignments: x = 42
    - Variable declarations: var x = 42, let x = 42
    - Compound assignments: x += 5, y *= 2
    
    Args:
        text (str): The assignment statement
        
    Returns:
        Tuple[str, str]: Tuple containing variable name and expression
        
    Raises:
        ParseError: If the assignment syntax is invalid
    """
    text = text.strip()
    
    # Pattern for variable declaration (var/let)
    var_pattern = r'^(var|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$'
    var_match = re.match(var_pattern, text, re.DOTALL)
    
    if var_match:
        var_type = var_match.group(1)
        var_name = var_match.group(2)
        expression = var_match.group(3).strip()
        return var_name, expression
    
    # Pattern for compound assignment (+=, -=, *=, /=, %=)
    compound_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*(\+=|\-=|\*=|\/=|\%=)\s*(.+)$'
    compound_match = re.match(compound_pattern, text, re.DOTALL)
    
    if compound_match:
        var_name = compound_match.group(1)
        operator = compound_match.group(2)
        expression = compound_match.group(3).strip()
        # Convert compound assignment to regular expression
        full_expression = f"{var_name} {operator[:-1]} ({expression})"
        return var_name, full_expression
    
    # Pattern for simple assignment
    simple_pattern = r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)$'
    simple_match = re.match(simple_pattern, text, re.DOTALL)
    
    if simple_match:
        var_name = simple_match.group(1)
        expression = simple_match.group(2).strip()
        return var_name, expression
    
    raise ParseError(f"Invalid assignment syntax: {text}")


def parse_if_statement(text: str) -> Dict[str, Any]:
    """
    Parse an if/else statement into its components.
    
    Args:
        text (str): The if/else statement
        
    Returns:
        Dict[str, Any]: Dictionary with keys:
            - condition: The condition expression
            - then_block: List of statements in the then branch
            - else_block: List of statements in the else branch (optional)
            
    Raises:
        ParseError: If the if statement syntax is invalid
    """
    text = text.strip()
    
    # Basic if statement pattern
    if_pattern = r'^if\s*(?:\(?(.+?)\)?)\s*\{(.+?)\}$'
    if_match = re.match(if_pattern, text, re.DOTALL)
    
    if if_match:
        condition = if_match.group(1).strip()
        then_block = if_match.group(2).strip()
        
        # Parse else if present
        else_pattern = r'^(.+?)\}?\s*else\s*\{(.+)\}$'
        else_match = re.match(else_pattern, then_block, re.DOTALL)
        
        if else_match:
            then_block = else_match.group(1).strip()
            else_block = else_match.group(2).strip()
            return {
                'condition': condition,
                'then_block': split_statements(then_block),
                'else_block': split_statements(else_block)
            }
        
        return {
            'condition': condition,
            'then_block': split_statements(then_block),
            'else_block': None
        }
    
    raise ParseError(f"Invalid if statement syntax: {text}")


def parse_while_loop(text: str) -> Dict[str, Any]:
    """
    Parse a while loop statement into its components.
    
    Args:
        text (str): The while loop statement
        
    Returns:
        Dict[str, Any]: Dictionary with keys:
            - condition: The loop condition
            - body: List of statements in the loop body
            
    Raises:
        ParseError: If the while loop syntax is invalid
    """
    text = text.strip()
    
    # While loop pattern
    while_pattern = r'^while\s*(?:\(?(.+?)\)?)\s*\{(.+)\}$'
    while_match = re.match(while_pattern, text, re.DOTALL)
    
    if while_match:
        condition = while_match.group(1).strip()
        body = while_match.group(2).strip()
        
        return {
            'condition': condition,
            'body': split_statements(body)
        }
    
    raise ParseError(f"Invalid while loop syntax: {text}")


def parse_for_loop(text: str) -> Dict[str, Any]:
    """
    Parse a for loop statement into its components.
    
    Supports:
    - For-in loops: for item in collection { ... }
    - C-style for loops: for (i = 0; i < 10; i += 1) { ... }
    
    Args:
        text (str): The for loop statement
        
    Returns:
        Dict[str, Any]: Dictionary with loop information
        
    Raises:
        ParseError: If the for loop syntax is invalid
    """
    text = text.strip()
    
    # Try for-in pattern first
    for_in_pattern = r'^for\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+in\s+(.+?)\s*\{(.+)\}$'
    for_in_match = re.match(for_in_pattern, text, re.DOTALL)
    
    if for_in_match:
        var_name = for_in_match.group(1)
        collection = for_in_match.group(2).strip()
        body = for_in_match.group(3).strip()
        
        return {
            'type': 'for_in',
            'variable': var_name,
            'collection': collection,
            'body': split_statements(body)
        }
    
    # Try C-style for loop
    c_for_pattern = r'^for\s*\((.*?);(.*?);(.*?)\)\s*\{(.+)\}$'
    c_for_match = re.match(c_for_pattern, text, re.DOTALL)
    
    if c_for_match:
        initialization = c_for_match.group(1).strip()
        condition = c_for_match.group(2).strip()
        increment = c_for_match.group(3).strip()
        body = c_for_match.group(4).strip()
        
        return {
            'type': 'c_style',
            'initialization': initialization,
            'condition': condition,
            'increment': increment,
            'body': split_statements(body)
        }
    
    raise ParseError(f"Invalid for loop syntax: {text}")


def validate_syntax(text: str) -> bool:
    """
    Perform basic syntax validation on CherryScript code.
    
    Args:
        text (str): The code to validate
        
    Returns:
        bool: True if syntax appears valid, False otherwise
    """
    try:
        # Try to split statements - this will catch many syntax errors
        statements = split_statements(text)
        
        # Validate each statement
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            
            # Check for basic statement patterns
            # This is a simplified validation - a real implementation would be more thorough
            
            # Check for balanced quotes
            if stmt.count('"') % 2 != 0:
                return False
            if stmt.count("'") % 2 != 0:
                return False
            
            # Check for balanced parentheses
            if stmt.count('(') != stmt.count(')'):
                return False
            
            # Check for balanced braces
            if stmt.count('{') != stmt.count('}'):
                return False
            
            # Check for balanced brackets
            if stmt.count('[') != stmt.count(']'):
                return False
        
        return True
        
    except ParseError:
        return False
    except Exception:
        return False


def extract_comments(text: str) -> List[Dict[str, Any]]:
    """
    Extract comments from CherryScript code.
    
    Args:
        text (str): The code to extract comments from
        
    Returns:
        List[Dict[str, Any]]: List of comment dictionaries with:
            - type: 'line' or 'block'
            - content: The comment text
            - line: Line number (1-indexed)
            - position: Character position
    """
    comments = []
    lines = text.split('\n')
    in_block_comment = False
    block_comment_start = None
    
    for line_num, line in enumerate(lines, 1):
        i = 0
        line_length = len(line)
        
        while i < line_length:
            # Skip strings
            in_string = False
            string_char = None
            
            # Check for line comments
            if not in_block_comment and not in_string and line[i:i+2] == '//':
                comment_content = line[i+2:].strip()
                comments.append({
                    'type': 'line',
                    'content': comment_content,
                    'line': line_num,
                    'position': i
                })
                break  # Rest of line is comment
            
            # Check for block comment start
            if not in_string and line[i:i+2] == '/*':
                in_block_comment = True
                block_comment_start = (line_num, i)
                i += 2
                continue
            
            # Check for block comment end
            if in_block_comment and line[i:i+2] == '*/':
                # We don't track multi-line block comment content in this simple version
                in_block_comment = False
                block_comment_start = None
                i += 2
                continue
            
            i += 1
        
        # If we're still in a block comment at end of line, that's fine
    
    return comments


def pretty_print_ast(statements: List[str], indent: int = 0) -> str:
    """
    Create a pretty-printed representation of parsed statements (simplified AST).
    
    Args:
        statements (List[str]): List of statements to format
        indent (int): Indentation level
        
    Returns:
        str: Pretty-printed representation
    """
    result = []
    indent_str = '  ' * indent
    
    for i, stmt in enumerate(statements):
        stmt = stmt.strip()
        if not stmt:
            continue
        
        # Try to identify statement type
        if stmt.startswith('if '):
            try:
                parsed = parse_if_statement(stmt)
                result.append(f"{indent_str}[{i}] IF statement:")
                result.append(f"{indent_str}  Condition: {parsed['condition']}")
                result.append(f"{indent_str}  Then block:")
                for sub_stmt in parsed['then_block']:
                    result.append(f"{indent_str}    - {sub_stmt[:50]}..." if len(sub_stmt) > 50 else f"{indent_str}    - {sub_stmt}")
                if parsed['else_block']:
                    result.append(f"{indent_str}  Else block:")
                    for sub_stmt in parsed['else_block']:
                        result.append(f"{indent_str}    - {sub_stmt[:50]}..." if len(sub_stmt) > 50 else f"{indent_str}    - {sub_stmt}")
            except ParseError:
                result.append(f"{indent_str}[{i}] IF statement (unparsed): {stmt[:50]}...")
        
        elif stmt.startswith('while '):
            try:
                parsed = parse_while_loop(stmt)
                result.append(f"{indent_str}[{i}] WHILE loop:")
                result.append(f"{indent_str}  Condition: {parsed['condition']}")
                result.append(f"{indent_str}  Body:")
                for sub_stmt in parsed['body']:
                    result.append(f"{indent_str}    - {sub_stmt[:50]}..." if len(sub_stmt) > 50 else f"{indent_str}    - {sub_stmt}")
            except ParseError:
                result.append(f"{indent_str}[{i}] WHILE loop (unparsed): {stmt[:50]}...")
        
        elif stmt.startswith('for '):
            try:
                parsed = parse_for_loop(stmt)
                result.append(f"{indent_str}[{i}] FOR loop ({parsed['type']}):")
                if parsed['type'] == 'for_in':
                    result.append(f"{indent_str}  Variable: {parsed['variable']}")
                    result.append(f"{indent_str}  Collection: {parsed['collection']}")
                else:
                    result.append(f"{indent_str}  Initialization: {parsed['initialization']}")
                    result.append(f"{indent_str}  Condition: {parsed['condition']}")
                    result.append(f"{indent_str}  Increment: {parsed['increment']}")
                result.append(f"{indent_str}  Body:")
                for sub_stmt in parsed['body']:
                    result.append(f"{indent_str}    - {sub_stmt[:50]}..." if len(sub_stmt) > 50 else f"{indent_str}    - {sub_stmt}")
            except ParseError:
                result.append(f"{indent_str}[{i}] FOR loop (unparsed): {stmt[:50]}...")
        
        elif '(' in stmt and stmt.endswith(')'):
            try:
                func_name, args = parse_call(stmt)
                result.append(f"{indent_str}[{i}] Function call: {func_name}")
                if args:
                    result.append(f"{indent_str}  Arguments:")
                    for arg in args:
                        result.append(f"{indent_str}    - {arg[:50]}..." if len(arg) > 50 else f"{indent_str}    - {arg}")
            except ParseError:
                result.append(f"{indent_str}[{i}] Function call (unparsed): {stmt[:50]}...")
        
        elif '=' in stmt:
            try:
                var_name, expression = parse_assignment(stmt)
                result.append(f"{indent_str}[{i}] Assignment: {var_name} = ...")
                result.append(f"{indent_str}  Expression: {expression[:50]}..." if len(expression) > 50 else f"{indent_str}  Expression: {expression}")
            except ParseError:
                result.append(f"{indent_str}[{i}] Assignment (unparsed): {stmt[:50]}...")
        
        else:
            result.append(f"{indent_str}[{i}] Expression: {stmt[:50]}..." if len(stmt) > 50 else f"{indent_str}[{i}] Expression: {stmt}")
    
    return '\n'.join(result)


# Test function for module
if __name__ == '__main__':
    print("CherryScript Parser Module Test")
    print("=" * 50)
    
    test_code = """
    // This is a test script
    var x = 42
    let y = "Hello, world!"
    
    if (x > 10) {
        print("x is greater than 10")
    } else {
        print("x is 10 or less")
    }
    
    for item in [1, 2, 3] {
        print("Item:", item)
    }
    
    while (x > 0) {
        x = x - 1
        print("Countdown:", x)
    }
    
    db.query("SELECT * FROM users WHERE active = true")
    h2o.automl(frame, "target_column")
    deploy(model, "http://localhost:8080/predict")
    """
    
    print("\nTest Code:")
    print("-" * 30)
    print(test_code)
    print("-" * 30)
    
    print("\nParsed Statements:")
    print("-" * 30)
    try:
        statements = split_statements(test_code)
        for i, stmt in enumerate(statements):
            print(f"[{i}] {stmt}")
        
        print("\nAST Pretty Print:")
        print("-" * 30)
        print(pretty_print_ast(statements))
        
        print("\nExtracted Comments:")
        print("-" * 30)
        comments = extract_comments(test_code)
        for comment in comments:
            print(f"Line {comment['line']}: {comment['type']} comment: {comment['content']}")
        
        print("\nSyntax Validation:")
        print("-" * 30)
        is_valid = validate_syntax(test_code)
        print(f"Code is valid: {is_valid}")
        
    except ParseError as e:
        print(f"Parse error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Parser module test complete!")
