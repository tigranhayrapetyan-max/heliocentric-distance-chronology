#!/usr/bin/env python3
"""Astronomy-blind Stage-B0 Wikidata enrichment for Article 4.

This is TRIAGE ONLY. Wikidata claims do not constitute final independent historical
verification. The script preserves raw claim times, precision, ranks, and reference
counts so human/source adjudication can prioritize candidates reproducibly.
"""
from __future__ import annotations
import csv,json,re,time,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path

INPUT=Path('A4_STAGE_A_OUTPUT/GLOBAL_TRANSITIONS_CANDIDATE_PRIMARY.csv')
OUT_ENTITY=Path('A4_STAGE_A_OUTPUT/GLOBAL_WIKIDATA_ENTITY_ENRICHMENT.csv')
OUT_CAND=Path('A4_STAGE_A_OUTPUT/GLOBAL_CANDIDATE_WIKIDATA_TRIAGE.csv')
CACHE=Path('A4_STAGE_A_OUTPUT/WIKIDATA_ENTITY_CACHE.json')
BATCH=40
UA='Article4-Historical-Validation/0.1 (research reproducibility; no astronomy)'
DATE_PROPS={'P571':'inception','P576':'dissolved_or_abolished','P580':'start_time','P582':'end_time'}


def read_rows():
    return list(csv.DictReader(INPUT.open(encoding='utf-8-sig')))

def qid(v):
    m=re.search(r'Q\d+',v or '')
    return m.group(0) if m else ''

def fetch(ids):
    entities={}
    for i in range(0,len(ids),BATCH):
        part=ids[i:i+BATCH]
        qs=urllib.parse.urlencode({
            'action':'wbgetentities','ids':'|'.join(part),'props':'claims|labels','languages':'en','format':'json','formatversion':'2'
        })
        req=urllib.request.Request('https://www.wikidata.org/w/api.php?'+qs,headers={'User-Agent':UA})
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req,timeout=60) as r:
                    obj=json.load(r)
                entities.update(obj.get('entities',{})); break
            except Exception:
                if attempt==4: raise
                time.sleep(2**attempt)
        time.sleep(0.15)
    return entities

def time_claims(entity,prop):
    out=[]
    for c in (entity.get('claims') or {}).get(prop,[]):
        snak=c.get('mainsnak') or {}; dv=snak.get('datavalue') or {}; val=dv.get('value')
        if not isinstance(val,dict) or 'time' not in val: continue
        out.append({
            'time':val.get('time',''),'precision':val.get('precision',''),'calendarmodel':val.get('calendarmodel',''),
            'before':val.get('before',''),'after':val.get('after',''),'rank':c.get('rank',''),
            'reference_count':len(c.get('references') or [])
        })
    return out

def parse_wd_year(t):
    m=re.match(r'^([+-])(\d+)-',t or '')
    if not m:return None
    y=int(m.group(2))
    if m.group(1)=='-': return -y
    return y

def flatten_claims(claims):
    return ' || '.join(f"{x['time']}|p{x['precision']}|rank={x['rank']}|refs={x['reference_count']}" for x in claims)

def main():
    rows=read_rows(); ids=sorted({qid(r.get('WIKIDATA','')) for r in rows if qid(r.get('WIKIDATA',''))},key=lambda x:int(x[1:]))
    entities=fetch(ids)
    CACHE.write_text(json.dumps(entities,ensure_ascii=False,sort_keys=True,separators=(',',':')),encoding='utf-8')

    erows=[]; byid={}
    for q in ids:
        e=entities.get(q,{})
        label=((e.get('labels') or {}).get('en') or {}).get('value','')
        rec={'WIKIDATA':q,'LABEL_EN':label}
        for p,name in DATE_PROPS.items():
            cl=time_claims(e,p); rec[name.upper()+'_CLAIMS']=flatten_claims(cl)
            rec[name.upper()+'_CLAIM_COUNT']=len(cl)
            rec[name.upper()+'_REFERENCED_CLAIM_COUNT']=sum(x['reference_count']>0 for x in cl)
        erows.append(rec); byid[q]=e
    efields=list(erows[0].keys()) if erows else ['WIKIDATA','LABEL_EN']
    with OUT_ENTITY.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=efields); w.writeheader(); w.writerows(erows)

    crows=[]
    for r in rows:
        q=qid(r.get('WIKIDATA','')); e=byid.get(q,{})
        candidate_year=int(r['YEAR_CLI'])
        props=['P571','P580'] if r['BOUNDARY']=='START' else ['P576','P582']
        claims=[]
        for p in props:
            for c in time_claims(e,p): claims.append((p,c))
        claim_years=[parse_wd_year(c['time']) for _,c in claims]
        claim_years=[y for y in claim_years if y is not None]
        exact_year_any=any(y==candidate_year for y in claim_years)
        min_delta=min((abs(y-candidate_year) for y in claim_years),default='')
        referenced=sum(c['reference_count']>0 for _,c in claims)
        crows.append({
            'TRANSITION_ID':r['TRANSITION_ID'],'ENTITY_KEY':r['ENTITY_KEY'],'CANONICAL_NAME':r['CANONICAL_NAME'],
            'BOUNDARY':r['BOUNDARY'],'CANDIDATE_CLASS':r['CANDIDATE_CLASS'],'YEAR_CLI':candidate_year,
            'WIKIDATA':q,'WIKIDATA_LABEL_EN':((e.get('labels') or {}).get('en') or {}).get('value',''),
            'RELEVANT_WD_DATE_CLAIMS':' || '.join(f"{p}:{c['time']}|p{c['precision']}|refs={c['reference_count']}|rank={c['rank']}" for p,c in claims),
            'RELEVANT_WD_DATE_CLAIM_COUNT':len(claims),'REFERENCED_RELEVANT_WD_CLAIM_COUNT':referenced,
            'WD_EXACT_SOURCE_COORD_YEAR_ANY':exact_year_any,'WD_MIN_ABS_YEAR_DELTA':min_delta,
            'TRIAGE_ONLY':'YES','FINAL_HISTORICAL_VERIFICATION':'PENDING'
        })
    fields=list(crows[0].keys())
    with OUT_CAND.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(crows)
    print('WIKIDATA_ENTITIES=',len(erows))
    print('CANDIDATES=',len(crows))
    print('CANDIDATES_WITH_RELEVANT_DATE_CLAIMS=',sum(int(r['RELEVANT_WD_DATE_CLAIM_COUNT'])>0 for r in crows))
    print('CANDIDATES_WITH_REFERENCED_RELEVANT_CLAIMS=',sum(int(r['REFERENCED_RELEVANT_WD_CLAIM_COUNT'])>0 for r in crows))
    print('CANDIDATES_EXACT_SOURCE_COORD_YEAR=',sum(str(r['WD_EXACT_SOURCE_COORD_YEAR_ANY']).lower()=='true' for r in crows))

if __name__=='__main__': main()
