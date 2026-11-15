# -*- coding: utf-8 -*-
"""glume cli."""

import sys
import argparse
from pathlib import Path
from .engine import Glume

def main():
    """Run the Glume command-line interface."""
    parser = argparse.ArgumentParser(
        description="Glume: Nano file-to-text packer for LLM context windows using Memor."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory to pack (default: current directory)"
    )
    parser.add_argument(
        "--directory",
        dest="directory_optional",
        help="Target directory to pack (overrides positional directory)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: prints to stdout)"
    )
    parser.add_argument(
        "-t", "--template",
        help="Path to a custom Jinja2 template file"
    )
    parser.add_argument(
        "--no-tree",
        action="store_true",
        help="Disable folder structure tree inclusion"
    )
    parser.add_argument(
        "-i", "--ignore",
        action="append",
        default=None,
        help="Glob patterns to ignore (can be used multiple times)"
    )
    parser.add_argument(
        "--git-ignore",
        action="store_true",
        help="Automatically load and apply rules from the project's .gitignore file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose warnings for unreadable files"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Report detailed file processing statistics after run"
    )

    args = parser.parse_args()
    directory = args.directory_optional if args.directory_optional is not None else args.directory
    dir_path = Path(directory).resolve()
    if args.output:
        output_path = Path(args.output).resolve()
        try:
            relative_output = output_path.relative_to(dir_path)
            args.ignore = (args.ignore or []) + [relative_output.as_posix()]
        except ValueError:
            pass

    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == args.directory) or (len(sys.argv) == 3 and sys.argv[1] == "--directory"):
        print(f"[Wizard Mode] Auto-packing current directory: {dir_path}", file=sys.stderr)

    template_content = None
    if args.template:
        try:
            with open(args.template, "r", encoding="utf-8") as f:
                template_content = f.read()
        except Exception as e:
            print(f"Error reading template file: {e}", file=sys.stderr)
            sys.exit(1)

    packer = Glume(
        target_dir=dir_path,
        custom_template=template_content,
        ignore_patterns=args.ignore,
        use_gitignore=args.git_ignore,
        include_tree=not args.no_tree,
        verbose=args.verbose
    )

    try:
        result = packer.pack()
    except Exception as e:
        print(f"Error during packing: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        out_path = Path(args.output)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Context packed successfully into: {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(result)

    if args.stats:
        stats = packer.get_stats()
        print("\n--- Glume Execution Statistics ---", file=sys.stderr)
        print(f"   Included Files: {stats['included_count']}", file=sys.stderr)
        print(f"   Ignored Paths:  {stats['ignored_count']}", file=sys.stderr)
        print(f"   Binary Files:   {stats['binary_count']}", file=sys.stderr)
        print(f"   Failed Files:   {stats['failed_count']}", file=sys.stderr)

        if stats['ignored']:
            print("\n  [Ignored Paths]:", file=sys.stderr)
            for p in stats['ignored']:
                print(f"    - {p}", file=sys.stderr)

        if stats['binary']:
            print("\n  [Binary Skipped]:", file=sys.stderr)
            for f in stats['binary']:
                print(f"    - {f}", file=sys.stderr)

        if stats['failed']:
            print("\n  [Failed to Read]:", file=sys.stderr)
            for f in stats['failed']:
                print(f"    - {f['path']} ({f['error']})", file=sys.stderr)
