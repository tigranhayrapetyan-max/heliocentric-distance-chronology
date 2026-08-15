#!/usr/bin/env python3
"""Apply the pre-overlay Cliopatria year-zero amendment to the Stage-A builder.

Cliopatria v0.2.0 uses a continuous signed integer source coordinate and contains
valid rows with year 0. Stage A therefore preserves YEAR_CLI exactly and performs
no BCE/CE -> astronomical-year conversion. Calendar/JD conversion is deferred to
Stage B after independent historical-source verification.
"""
from pathlib import Path
import re

p = Path('tools/article4/a4_build_historical_stageA.py')
s = p.read_text(encoding='utf-8')

# 1. Source-coordinate contiguity is arithmetic y+1, including -1 -> 0 -> 1.
s = re.sub(
    r'def historical_next_year\(y\):\s*return 1 if y==-1 else y\+1\s*\n'
    r'def cli_to_astro_year\(y\):\s*return y\+1 if y<0 else y\s*\n',
    'def source_next_year(y): return y + 1\n',
    s,
)
s = s.replace('historical_next_year(', 'source_next_year(')

# 2. Year zero is a valid Cliopatria source coordinate.
s = re.sub(
    r'\n\s*if y==0:\s*raise ValueError\([^\n]*\)',
    '',
    s,
)

# 3. Remove all derived astronomical-year fields from Stage A.
s = re.sub(r'\s*"FROM_YEAR_ASTRO"\s*:\s*cli_to_astro_year\([^,]+\),', '', s)
s = re.sub(r'\s*"TO_YEAR_ASTRO"\s*:\s*cli_to_astro_year\([^,]+\),', '', s)
s = re.sub(r'\s*"YEAR_ASTRO"\s*:\s*cli_to_astro_year\([^,]+\),', '', s)
s = s.replace(',"FROM_YEAR_ASTRO","TO_YEAR_ASTRO"', '')
s = s.replace(',"YEAR_ASTRO"', '')
s = s.replace('"FROM_YEAR_ASTRO","TO_YEAR_ASTRO",', '')
s = s.replace('"YEAR_ASTRO",', '')

# Remove the now-unused converter definition if formatting differed from the first regex.
s = re.sub(r'\ndef cli_to_astro_year\(y\):[^\n]*\n', '\n', s)

# 4. Mark the executed protocol variant explicitly.
s = s.replace(
    '"protocol_id":"A4_GLOBAL_TRANSITIONS_V2_STAGE_A"',
    '"protocol_id":"A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_AMENDED"',
)

# 5. Add source-coordinate policy to manifest if not already present.
needle = '"astronomy_consulted":False,'
policy = (
    '"astronomy_consulted":False,'
    '"year_coordinate_rule":{'
    '"cliopatria":"continuous signed integer source coordinate; v0.2.0 contains year 0",'
    '"stage_a_policy":"preserve YEAR_CLI exactly; no astronomical-year conversion in Stage A",'
    '"stage_b_policy":"calendar/JD conversion only after independent historical source verification"},'
)
if '"year_coordinate_rule"' not in s:
    s = s.replace(needle, ''.join(policy), 1)

for forbidden in ('YEAR_ASTRO','FROM_YEAR_ASTRO','TO_YEAR_ASTRO','cli_to_astro_year','historical_next_year'):
    if forbidden in s:
        raise SystemExit(f'Amendment incomplete: {forbidden} still present')
if 'source_next_year' not in s:
    raise SystemExit('Amendment incomplete: source_next_year missing')
if 'A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_AMENDED' not in s:
    raise SystemExit('Amendment incomplete: protocol id not amended')

p.write_text(s, encoding='utf-8')
print('A4_STAGE_A_YEAR0_AMENDMENT=APPLIED')
