#!/usr/bin/env python3
"""Astronomy-blind Stage-B0 Wikidata truthy-date triage for Article 4.

TRIAGE ONLY: this does not constitute final historical verification. It queries the
Wikidata Query Service in batches for truthy P571/P576/P580/P582 values and preserves
them as machine-readable hints for later source adjudication.
"""
from __future__ import annotations
import csv,json,re,time,urllib.parse,urllib.request,urllib.error
from collections import defaultdict
from pathlib import Path

INPUT=Path('A4_STAGE_A_OUTPUT/GLOBAL_TRANSITIONS_CANDIDATE_PRIMARY.csv')
OUT_ENTITY=Path('A4_STAGE_A_OUTPUT/GLOBAL_WIKIDATA_ENTITY_ENRICHMENT.csv')
OUT_CAND=Path('A4_STAGE_A_OUTPUT/GLOBAL_CANDIDATE_WIKIDATA_TRIAGE.csv')
CACHE=Path('A4_STAGE_A_OUTPUT/WIKIDATA_TRUTHY_DATE_CACHE.json')
BATCH=80
UA='Article4-Historical-Validation/0.2 (research reproducibility; no astronomy)'
PROPS=['P571','P576','P580','P582']


def qid(v):
    m=re.search(r'Q\d+',v or '')
    return m.group(0) if m else ''

def parse_year(v):
    m=re.match(r'^([+-]?)(\d{1,})-',v or '')
    if not m:return None
    y=int(m.group(2)); return -y if m.group(1)=='-' else y

def query_batch(ids):
    values=' '.join('wd:'+q for q in ids)
    query=f'''SELECT ?item ?prop ?date WHERE {{
      VALUES ?item {{ {values} }}
      VALUES (?prop ?p) {{ ("P571" wdt:P571) ("P576" wdt:P576) ("P580" wdt:P580) ("P582" wdt:P582) }}
      ?item ?p ?date .
    }}'''
    url='https://query.wikidata.org/sparql?'+urllib.parse.urlencode({'query':query,'format':'json'})
    req=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/sparql-results+json'})
    for attempt in range(10):
        try:
            with urllib.request.urlopen(req,timeout=90) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429,502,503,504) or attempt==9: raise
            retry=e.headers.get('Retry-After')
            delay=int(retry) if retry and retry.isdigit() else min(60,5*(attempt+1))
            time.sleep(delay)
        except Exception:
            if attempt==9: raise
            time.sleep(min(60,5*(attempt+1)))
    raise RuntimeError('unreachable')

def main():
    rows=list(csv.DictReader(INPUT.open(encoding='utf-8-sig')))
    ids=sorted({qid(r.get('WIKIDATA','')) for r in rows if qid(r.get('WIKIDATA',''))},key=lambda x:int(x[1:]))
    vals=defaultdict(lambda:defaultdict(list))
    completed=[]
    for i in range(0,len(ids),BATCH):
        part=ids[i:i+BATCH]
        obj=query_batch(part)
        for b in obj.get('results',{}).get('bindings',[]):
            q=(b.get('item',{}).get('value','').rsplit('/',1)[-1])
            prop=b.get('prop',{}).get('value','')
            date=b.get('date',{}).get('value','')
            if q and prop and date: vals[q][prop].append(date)
        completed.extend(part)
        CACHE.write_text(json.dumps({'completed_ids':completed,'values':vals},default=dict,ensure_ascii=False,sort_keys=True),encoding='utf-8')
        time.sleep(1.0)

    erows=[]
    for q in ids:
        d=vals.get(q,{})
        erows.append({'WIKIDATA':q,**{p+'_TRUTHY_VALUES':' || '.join(sorted(set(d.get(p,[])))) for p in PROPS}})
    with OUT_ENTITY.open('w',newline='',encoding='utf-8-sig') as f:
        fields=['WIKIDATA']+[p+'_TRUTHY_VALUES' for p in PROPS]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(erows)

    crows=[]
    for r in rows:
        q=qid(r.get('WIKIDATA','')); d=vals.get(q,{})
        props=['P571','P580'] if r['BOUNDARY']=='START' else ['P576','P582']
        relevant=[(p,v) for p in props for v in d.get(p,[])]
        years=[parse_year(v) for _,v in relevant]; years=[y for y in years if y is not None]
        cy=int(r['YEAR_CLI'])
        crows.append({
            'TRANSITION_ID':r['TRANSITION_ID'],'ENTITY_KEY':r['ENTITY_KEY'],'CANONICAL_NAME':r['CANONICAL_NAME'],
            'BOUNDARY':r['BOUNDARY'],'CANDIDATE_CLASS':r['CANDIDATE_CLASS'],'YEAR_CLI':cy,'WIKIDATA':q,
            'RELEVANT_WD_TRUTHY_DATES':' || '.join(f'{p}:{v}' for p,v in relevant),
            'RELEVANT_WD_TRUTHY_DATE_COUNT':len(relevant),
            'WD_EXACT_SOURCE_COORD_YEAR_ANY':any(y==cy for y in years),
            'WD_MIN_ABS_YEAR_DELTA':min((abs(y-cy) for y in years),default=''),
            'TRIAGE_ONLY':'YES','FINAL_HISTORICAL_VERIFICATION':'PENDING'
        })
    fields=list(crows[0].keys())
    with OUT_CAND.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(crows)

    print('WIKIDATA_ENTITIES=',len(ids))
    print('CANDIDATES=',len(crows))
    print('CANDIDATES_WITH_RELEVANT_TRUTHY_DATES=',sum(int(r['RELEVANT_WD_TRUTHY_DATE_COUNT'])>0 for r in crows))
    print('CANDIDATES_EXACT_SOURCE_COORD_YEAR=',sum(str(r['WD_EXACT_SOURCE_COORD_YEAR_ANY']).lower()=='true' for r in crows))

if __name__=='__main__': main()
