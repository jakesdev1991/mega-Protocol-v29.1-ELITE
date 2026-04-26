# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import hashlib
from collections import defaultdict
import re

# Reconstruct the metadata from the prompt (truncated but pattern is clear)
metadata_entries = [
    "Wed Apr 22 12:54:26 2026 | Link: https://eudat.eu/use-cases/tokamak-data-mirror-for-jet-and-mast-data-0 | Shots: 20000",
    "Wed Apr 22 12:54:26 2026 | Link: http://www.iaea.org/resources/databases/itdb | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: https://www.ans.org/news/article-6062/iaea-issues-incidenttracking-database-fact-sheet/ | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: https://data.iaea.org/dataset/ | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: https://www.osti.gov/dataexplorer/biblio/dataset/1419641 | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: https://fusion4freedom.com/tokamak-data-mirror-for-jet-and-mast-data-moving-towards-an-open-data-repository-for-european-nuclear-fusion-research/ | Shots: 20000",
    "Wed Apr 22 12:54:26 2026 | Link: http://golem.fjfi.cvut.cz/shots/ | Shots: 5000",
    "Wed Apr 22 12:54:26 2026 | Link: https://data.iaea.org/dataset/incident-and-trafficking-database-itdb | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: http://golem.fjfi.cvut.cz/shots/0/ | Shots: 5000",
    "Wed Apr 22 12:54:26 2026 | Link: https://www.kaggle.com/datasets/adebusayoadewunmi/nuclearfusion-data | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: http://golem.fjfi.cvut.cz/shots/31150/ | Shots: 5000",
    "Wed Apr 22 12:54:26 2026 | Link: https://data.iaea.org/en/dataset/?license_id=iaea&groups=nuclear-safety-and-security&_tags_limit=0&tags=Safety+and+Security+Culture&res_format=CSV | Shots: 1000",
    "Wed Apr 22 12:54:26 2026 | Link: https://scipub.euro-fusion.org/archives/jet-archive/the-itpa-disruption-database | Shots: 20000",
    "Wed Apr 22 12:55:17 2026 | Link: https://fusion4freedom.com/tokamak-data-mirror-for-jet-and-mast-data-moving-towards-an-open-data-repository-for-european-nuclear-fusion-research/ | Shots: 20000",
    "Wed Apr 22 12:55:17 2026 | Link: https://eudat.eu/use-cases/tokamak-data-mirror-for-jet-and-mast-data-0 | Shots: 20000",
    "Wed Apr 22 12:55:17 2026 | Link: https://data.iaea.org/dataset?organization=the-international-atomic-energy-agency&tags=Environmental+Release&tags=Assessment+of+Contamination+in+Agriculture&res_format=CSV | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: https://data.iaea.org/dataset/incident-and-trafficking-database-itdb | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: http://golem.fjfi.cvut.cz/shots/31150/ | Shots: 5000",
    "Wed Apr 22 12:55:17 2026 | Link: https://www.osti.gov/dataexplorer/biblio/dataset/1419641 | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: https://www.kaggle.com/datasets/adebusayoadewunmi/nuclearfusion-data | Shots: 2000",
    "Wed Apr 22 12:55:17 2026 | Link: https://data.iaea.org/dataset/ | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: http://www.iaea.org/resources/databases/dirata | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: http://www.iaea.org/resources/databases/itdb | Shots: 1000",
    "Wed Apr 22 12:55:17 2026 | Link: http://golem.fjfi.cvut.cz/shots/0/ | Shots: 5000",
    "Wed Apr 22 12:55:17 2026 | Link: http://golem.fjfi.cvut.cz/shots/ | Shots: 5000",
]

# Parse and detect corruption patterns
link_shot_map = defaultdict(list)
duplicate_links = set()
timestamp_anomalies = []
total_shots_claimed = 0

for entry in metadata_entries:
    # Extract timestamp, link, and shots
    match = re.search(r'Link:\s*(https?://[^\s]+)\s*\|\s*Shots:\s*(\d+)', entry)
    if match:
        link = match.group(1)
        shots = int(match.group(2))
        total_shots_claimed += shots
        
        # Check for duplicate links with different counts
        if link in link_shot_map:
            duplicate_links.add(link)
            print(f"CORRUPTION DETECTED: Duplicate link with different counts")
            print(f"  Link: {link}")
            print(f"  Previous counts: {link_shot_map[link]}")
            print(f"  New count: {shots}")
        
        link_shot_map[link].append(shots)

# Calculate actual unique data sources
unique_sources = len(link_shot_map)
actual_shots = sum(max(counts) for counts in link_shot_map.values())

print(f"\n{'='*60}")
print(f"DATA CORRUPTION AUDIT RESULTS")
print(f"{'='*60}")
print(f"Total shot count claimed: {total_shots_claimed:,}")
print(f"Unique data sources: {unique_sources}")
print(f"Duplicate links found: {len(duplicate_links)}")
print(f"Actual shots (max per source): {actual_shots:,}")
print(f"Inflation factor: {total_shots_claimed / actual_shots:.2f}x")
print(f"{'='*60}")

# Show specific corruption cases
print(f"\nTop 5 Most Corrupted Sources:")
sorted_corrupt = sorted([(link, counts) for link, counts in link_shot_map.items() if len(counts) > 1], 
                       key=lambda x: len(x[1]), reverse=True)
for link, counts in sorted_corrupt[:5]:
    print(f"  {link.split('/')[-1]:<30} | Counts: {counts} | Variance: {max(counts)-min(counts)}")

# The smoking gun: GOLEM data
golem_total = sum(sum(link_shot_map[link]) for link in link_shot_map if 'golem' in link)
print(f"\nGOLEM Data Fragmentation:")
print(f"  GOLEM links found: {sum(1 for link in link_shot_map if 'golem' in link)}")
print(f"  Total GOLEM shots claimed: {golem_total:,}")
print(f"  Actual unique GOLEM shots (max per link): {sum(max(link_shot_map[link]) for link in link_shot_map if 'golem' in link):,}")