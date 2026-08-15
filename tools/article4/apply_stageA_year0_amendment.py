#!/usr/bin/env python3
"""Apply Article-4 Stage-A source-coordinate amendment before execution.

Reason: Cliopatria v0.2.0 contains valid rows with year 0 and its viewer exposes a
continuous integer axis including 0. Stage A therefore preserves the Cliopatria
source coordinate exactly and defers all BCE/CE -> astronomical/JD conversion to
Stage B, after independent historical source verification.
"""
from pathlib import Path

p=Path('tools/article4/a4_build_historical_stageA.py')
s=p.read_text(encoding='utf-8')

s=s.replace(
'''def historical_next_year(y: int) -> int:\n    # Historical BCE/CE numbering has no year zero.\n    return 1 if y == -1 else y + 1\n\n\ndef cli_to_astro_year(y: int) -> int:\n    # Astronomical numbering has year 0 = 1 BCE.\n    return y + 1 if y < 0 else y\n''',
'''def source_next_year(y: int) -> int:\n    # Cliopatria v0.2.0 uses a continuous signed integer source axis including year 0.\n    # Stage A preserves this coordinate without astronomical reinterpretation.\n    return y + 1\n''')

s=s.replace(
'''    if y == 0:\n        raise ValueError("year 0 is invalid in Cliopatria historical year convention")\n    return y\n''',
'''    return y\n''')

s=s.replace('historical_next_year(', 'source_next_year(')
s=s.replace('                "FROM_YEAR_ASTRO": cli_to_astro_year(m["START"]),\n                "TO_YEAR_ASTRO": cli_to_astro_year(m["END"]),\n', '')
s=s.replace('                "YEAR_ASTRO": cli_to_astro_year(y),\n', '')
s=s.replace('                "YEAR_ASTRO": cli_to_astro_year(y2),\n', '')
s=s.replace('        "CANDIDATE_CLASS","CANDIDATE_POLARITY","YEAR_CLI","YEAR_ASTRO","EDGE_CENSORED",\n', '        "CANDIDATE_CLASS","CANDIDATE_POLARITY","YEAR_CLI","EDGE_CENSORED",\n')
s=s.replace('        "FROM_YEAR_CLI","TO_YEAR_CLI","FROM_YEAR_ASTRO","TO_YEAR_ASTRO","RAW_ROW_COUNT",\n', '        "FROM_YEAR_CLI","TO_YEAR_CLI","RAW_ROW_COUNT",\n')
s=s.replace(
'''        "year_coordinate_rule": {\n            "cliopatria": "historical BCE/CE integer numbering; no year 0",\n            "astronomical_year_field": "YEAR_ASTRO = YEAR_CLI + 1 for BCE years; unchanged for CE",\n            "note": "YEAR_ASTRO is a deterministic coordinate only; it is not an astronomical match result.",\n        },''',
'''        "year_coordinate_rule": {\n            "cliopatria": "continuous signed integer source coordinate; v0.2.0 contains year 0",\n            "stage_a_policy": "preserve YEAR_CLI exactly; no astronomical-year conversion in Stage A",\n            "stage_b_policy": "convert only independently verified historical dates after source validation",\n            "note": "Year-coordinate interpretation is deferred to Stage B to protect the blind historical census.",\n        },''')
s=s.replace('"protocol_id": "A4_GLOBAL_TRANSITIONS_V2_STAGE_A",', '"protocol_id": "A4_GLOBAL_TRANSITIONS_V2_STAGE_A_YEAR0_AMENDED",')

for forbidden in ('YEAR_ASTRO','FROM_YEAR_ASTRO','TO_YEAR_ASTRO','cli_to_astro_year','historical_next_year'):
    if forbidden in s:
        raise SystemExit(f'Amendment incomplete: {forbidden} still present')

p.write_text(s, encoding='utf-8')
print('A4_STAGE_A_YEAR0_AMENDMENT=APPLIED')
