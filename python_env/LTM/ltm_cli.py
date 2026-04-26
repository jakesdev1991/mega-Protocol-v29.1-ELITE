# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import argparse
import sys
import pyperclip
from process_memories import store_memory, search_memories
from memory_refiner import refine_memory

def main():
    parser = argparse.ArgumentParser(description="Long Term Memory (LTM) Manager for Gemini")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Store Command
    store_parser = subparsers.add_parser("store", help="Store a new memory")
    store_parser.add_argument("content", type=str, help="The memory text to store")

    # Search Command
    search_parser = subparsers.add_parser("search", help="Search and prepare memories for Gemini")
    search_parser.add_argument("query", type=str, help="The search query")
    search_parser.add_argument("--limit", type=int, default=3, help="Max memories to retrieve")
    search_parser.add_argument("--refine", action="store_true", help="Refine memories using Qwen before copying")
    search_parser.add_argument("--copy", action="store_true", help="Copy the result to the clipboard for AHK automation")

    args = parser.parse_args()

    if args.command == "store":
        store_memory(args.content)
    
    elif args.command == "search":
        print(f"Searching for: '{args.query}'...\n")
        raw_results = search_memories(args.query, limit=args.limit)
        
        final_text = raw_results
        if args.refine:
            print("Refining results with Qwen-0.5B...")
            # We refine the entire chunk or individual lines. We'll do the entire chunk here.
            final_text = refine_memory(raw_results, method="ollama")

        prompt_template = f"""I am providing specific historical context retrieved from my local vector database. Use the following snippets to inform your next response, but prioritize my current instructions over past data if they conflict.

**Retrieved Memories:**
{final_text}

**Current Query:**
{args.query}"""

        print("\n--- Context Template ---")
        print(prompt_template)
        print("------------------------")

        if args.copy:
            try:
                pyperclip.copy(prompt_template)
                print("\n✅ Context copied to clipboard! Press Ctrl+J in your browser to submit to Gemini.")
            except Exception as e:
                print(f"\n❌ Failed to copy to clipboard: {e}")
                print("Make sure pyperclip is installed and your system supports clipboard access.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
