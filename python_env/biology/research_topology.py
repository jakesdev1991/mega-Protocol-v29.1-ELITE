# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from tooluniverse import ToolUniverse
import json

def main():
    print("🚀 Initializing ToolUniverse...")
    tu = ToolUniverse()
    tu.load_tools()
    
    all_names = tu.list_built_in_tools(mode='list_name')
    
    # 1. Finding a search tool
    print("\n🔍 Looking for search tools...")
    search_tools = [n for n in all_names if "search" in n.lower() and ("paper" in n.lower() or "article" in n.lower() or "pmc" in n.lower())]
    print(f"Found search tools: {search_tools[:10]}")

    # 2. Get comprehensive protein info
    target_protein = "P0AAI3" # CitT E. coli
    target_tool = "proteins_api_get_protein"
    
    print(f"\n🚀 Fetching info for {target_protein} using {target_tool}...")
    
    try:
        # Checking parameters (fixing key from previous run)
        spec = tu.tool_specification(target_tool)
        # It seems the key is 'parameter' based on the output
        params_key = 'parameter' if 'parameter' in spec else 'parameters'
        print(f"Spec for {target_tool} ({params_key}): {json.dumps(spec[params_key]['properties'], indent=2)}")
        
        result = tu.run({"name": target_tool, "arguments": {"accession": target_protein}})
        print("\n--- Protein Data (Truncated) ---")
        # Print first 1000 chars of result to see structure
        res_str = json.dumps(result, indent=2)
        print(res_str[:2000] + "...")
        
        # 3. Search for "Topological Evolution" papers if a search tool exists
        if search_tools:
            search_tool = search_tools[0] # Try the first one
            print(f"\n📚 Searching for papers using {search_tool}...")
            
            spec_search = tu.tool_specification(search_tool)
            s_key = 'parameter' if 'parameter' in spec_search else 'parameters'
            
            # Guiding the search with the user's focus
            query = "topological evolution biological form"
            args = {}
            # Guessing common search params
            if 'query' in spec_search[s_key]['properties']:
                args['query'] = query
            elif 'queryString' in spec_search[s_key]['properties']:
                args['queryString'] = query
                
            if args:
                search_res = tu.run({"name": search_tool, "arguments": args})
                print("\n--- Search Results ---")
                print(json.dumps(search_res, indent=2)[:2000] + "...")

    except Exception as e:
        print(f"⚠️ Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
