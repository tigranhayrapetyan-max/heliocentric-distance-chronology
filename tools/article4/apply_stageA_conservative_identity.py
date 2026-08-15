#!/usr/bin/env python3
"""Apply conservative pre-overlay identity resolution to Article-4 Stage A.

Policy:
- The Cliopatria Name, normalized only for case/spacing/outer parentheses, defines the
  provisional Stage-A entity key.
- Wikidata, SeshatID and Wikipedia are provenance/review links, not automatic merge keys.
- Different substantive names sharing an external ID remain separate candidates until
  Stage-B historical source adjudication.

This policy is deliberately loss-averse: unresolved renames/phases may create extra
candidate boundaries for review, but Stage A must not erase a possible transition by
silently merging distinct labels before source verification.
"""
from pathlib import Path
import re

p=Path('tools/article4/a4_build_historical_stageA.py')
s=p.read_text(encoding='utf-8')

old = '''def identity_key(p):\n    wd,sid,wp,name=map(clean,[p.get("Wikidata"),p.get("SeshatID"),p.get("Wikipedia"),p.get("Name")])\n    if wd:return f"WD:{wd}","Wikidata"\n    if sid:return f"SESHAT:{sid}","SeshatID"\n    if wp:return f"WP:{norm_text(wp)}","Wikipedia"\n    return f"NAME:{norm_text(name)}","Name"\n'''
new = '''def identity_name(v):\n    name=clean(v)\n    if name.startswith("(") and name.endswith(")") and len(name)>2:\n        name=name[1:-1].strip()\n    return norm_text(name)\n\ndef identity_key(p):\n    name=clean(p.get("Name"))\n    if name:\n        return f"NAME:{identity_name(name)}","Name-conservative"\n    wd,sid,wp=map(clean,[p.get("Wikidata"),p.get("SeshatID"),p.get("Wikipedia")])\n    if wd:return f"WD:{wd}","Wikidata-fallback"\n    if sid:return f"SESHAT:{sid}","SeshatID-fallback"\n    if wp:return f"WP:{norm_text(wp)}","Wikipedia-fallback"\n    return "NAME:[missing]","Missing-name"\n'''
if old not in s:
    raise SystemExit('Conservative identity amendment failed: identity_key block not found')
s=s.replace(old,new,1)

s=s.replace(
    '"protocol_id":"A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_AMENDED"',
    '"protocol_id":"A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_NAME_CONSERVATIVE"',
    1,
)

needle='"interpretation_guard":"Cliopatria boundaries are candidates only; Stage-B source verification required",'
replacement=(
    '"identity_policy":{'
    '"provisional_key":"normalized Cliopatria Name; outer parentheses ignored",'
    '"external_ids":"review/provenance links only; never automatic merge keys",'
    '"substantive_rename_or_phase":"remains separate until Stage-B historical adjudication"},'
    + needle
)
if needle not in s:
    raise SystemExit('Conservative identity amendment failed: manifest guard not found')
s=s.replace(needle,replacement,1)

if 'A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_NAME_CONSERVATIVE' not in s:
    raise SystemExit('Conservative identity amendment incomplete: protocol id')
if 'Name-conservative' not in s:
    raise SystemExit('Conservative identity amendment incomplete: identity function')

p.write_text(s,encoding='utf-8')
print('A4_STAGE_A_CONSERVATIVE_IDENTITY=APPLIED')
