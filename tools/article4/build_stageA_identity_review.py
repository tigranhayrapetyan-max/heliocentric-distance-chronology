#!/usr/bin/env python3
"""Build cross-name external-ID review queue after conservative Stage-A census."""
import csv
from collections import defaultdict
from pathlib import Path

src=Path('A4_STAGE_A_OUTPUT/GLOBAL_POLITY_EPISODES_CANDIDATE.csv')
out=Path('A4_STAGE_A_OUTPUT/GLOBAL_CROSS_NAME_IDENTITY_REVIEW.csv')
rows=list(csv.DictReader(src.open(encoding='utf-8-sig')))

review=[]
for field,label in [('WIKIDATA','Wikidata'),('SESHAT_ID','SeshatID')]:
    groups=defaultdict(list)
    for r in rows:
        v=(r.get(field) or '').strip()
        if v: groups[v].append(r)
    for value,rr in groups.items():
        keys=sorted({r['ENTITY_KEY'] for r in rr})
        if len(keys)<2: continue
        names=sorted({r['CANONICAL_NAME'] for r in rr if r.get('CANONICAL_NAME')})
        episodes=sorted({f"{r['ENTITY_KEY']}#E{r['EPISODE_NO']}" for r in rr})
        review.append({
            'LINK_TYPE':label,
            'LINK_VALUE':value,
            'ENTITY_KEY_COUNT':len(keys),
            'ENTITY_KEYS':' | '.join(keys),
            'CANONICAL_NAMES':' | '.join(names),
            'EPISODES':' | '.join(episodes),
            'REVIEW_STATUS':'PENDING_STAGE_B_IDENTITY_ADJUDICATION',
            'DECISION':'',
            'SOURCE_SUPPORT':'',
            'NOTE':'External ID is a review link only; no Stage-A merge performed.'
        })

review.sort(key=lambda r:(r['LINK_TYPE'],r['LINK_VALUE']))
fields=['LINK_TYPE','LINK_VALUE','ENTITY_KEY_COUNT','ENTITY_KEYS','CANONICAL_NAMES','EPISODES','REVIEW_STATUS','DECISION','SOURCE_SUPPORT','NOTE']
with out.open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(review)
print(f'CROSS_NAME_IDENTITY_REVIEW={len(review)}')
