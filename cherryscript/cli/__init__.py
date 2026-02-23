"""CherryScript CLI entry point."""
import sys
import os
import argparse


def main(argv=None):
    """Command-line interface for CherryScript."""
    parser = argparse.ArgumentParser(
        prog='cherryscript',
        description='CherryScript — data collection, processing, and AI program creation',
    )
    parser.add_argument('file', nargs='?', help='.cherry script file to run')
    parser.add_argument('-c', '--command', help='Execute a CherryScript command string')
    parser.add_argument('-i', '--interactive', action='store_true',
                        help='Start interactive REPL mode')
    parser.add_argument('--version', action='store_true', help='Show version and exit')

    args = parser.parse_args(argv)

    if args.version:
        from cherryscript import __version__
        print(f'CherryScript {__version__}')
        return 0

    from cherryscript.runtime.interpreter import Runtime
    runtime = Runtime()

    # ── -c / --command ───────────────────────────────────────────────────────
    if args.command:
        runtime.run(args.command)
        return 0

    # ── run a .cherry file ───────────────────────────────────────────────────
    if args.file:
        path = args.file
        if not os.path.exists(path):
            print(f'[error] File not found: {path}', file=sys.stderr)
            return 1
        with open(path, 'r', encoding='utf-8') as fh:
            source = fh.read()
        runtime.run(source)
        return 0

    # ── interactive REPL ────────────────────────────────────────────────────
    _start_repl(runtime)
    return 0


def _start_repl(runtime):
    """Simple interactive REPL."""
    from cherryscript import __version__
    print(f'CherryScript {__version__} interactive mode')
    print('Type your CherryScript code, or "exit" / "quit" to stop.\n')

    buf: list = []

    while True:
        try:
            prompt = '... ' if buf else '>>> '
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        stripped = line.strip()

        if stripped.lower() in ('exit', 'quit'):
            break

        buf.append(line)
        combined = '\n'.join(buf)

        # If we're inside a multi-line block (unmatched braces), keep buffering
        if combined.count('{') > combined.count('}'):
            continue

        if combined.strip():
            runtime.run(combined)
        buf = []
