# -*- coding: utf-8 -*-
"""glume cli."""

import sys
import argparse
from art import text2art
from typio import type_print, TypeMode
from pathlib import Path
from .params import GLUME_VERSION, GLUME_REPO, OVERVIEW
from .engine import Glume


def _print_glume_help() -> None:
    """Print Glume details."""
    type_print(text2art("Glume"), mode=TypeMode.LINE, delay=0.1)
    type_print(text2art("V:" + GLUME_VERSION), mode=TypeMode.LINE, delay=0.1)
    type_print(OVERVIEW, mode=TypeMode.CHAR, delay=0.05)
    type_print(f"Repo : {GLUME_REPO}", mode=TypeMode.CHAR, delay=0.05)


def main():
    """Run the Glume command-line interface."""
    parser = argparse.ArgumentParser(
        description="Glume: A Nano File-to-Text Packer for LLM Context Windows"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=GLUME_VERSION
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Display Glume info"
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to a Glume config file"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=None,
        help="Target directory to pack (default: current directory)"
    )
    parser.add_argument(
        "--directory",
        dest="directory_optional",
        default=None,
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
        default=None,
        help="Disable folder structure tree inclusion"
    )
    parser.add_argument(
        "-i", "--ignore",
        action="append",
        default=None,
        help="Glob patterns to ignore (can be used multiple times)"
    )
    parser.add_argument(
        "--include",
        action="append",
        default=None,
        help="Glob patterns to include (can be used multiple times)"
    )
    parser.add_argument(
        "--git-ignore",
        action="store_true",
        default=None,
        help="Automatically load and apply rules from the project's .gitignore file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=None,
        help="Enable verbose warnings for unreadable files"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Report detailed file processing statistics after run"
    )

    args = parser.parse_args()
    if args.info:
        _print_glume_help()
        return
    
    directory = args.directory_optional if args.directory_optional is not None else args.directory

    template_content = None
    if args.template:
        try:
            with open(args.template, "r", encoding="utf-8") as f:
                template_content = f.read()
        except Exception as e:
            print(f"Error reading template file: {e}", file=sys.stderr)
            sys.exit(1)

    packer = Glume.from_config(
        config=args.config,
        target_dir=Path(directory).resolve() if directory else None,
        custom_template=template_content,
        ignore_patterns=args.ignore,
        include_patterns=args.include,
        use_gitignore=args.git_ignore,
        include_tree=not args.no_tree if args.no_tree is not None else None,
        verbose=args.verbose,
    )

    try:
        if args.output:
            out_path = packer.save(args.output)
        else:
            result = packer.pack()
    except Exception as e:
        print(f"Error during packing: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
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
