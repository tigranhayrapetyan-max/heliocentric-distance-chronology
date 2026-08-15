#!/usr/bin/env python3
"""Build Article 4 Stage-A global historical candidate census from frozen Cliopatria.

IMPORTANT: This script performs historical-side candidate generation only. It does not
read, load, or compare any astronomical catalogue.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import Counter,defaultdict
from pathlib import Path

RELEASE="v0.2.0"
RELEASE_COMMIT="ad28a691b7c07c1fca89d0e0636d324667d2a258"
EXPECTED_DATA_ZIP_GIT_BLOB_SHA1="cefab0f4b622e2e7fb3daf68d4f461f83991204c"
EXPECTED_DATA_ZIP_SIZE=44231317
ZENODO_VERSION_DOI="10.5281/zenodo.20274630"


def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def git_blob_sha1_file(path):
    h=hashlib.sha1(); size=Path(path).stat().st_size
    h.update(f"blob {size}\0".encode("ascii"))
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def clean(v): return "" if v is None else str(v).strip()
def norm_text(v): return re.sub(r"\s+"," ",clean(v).replace("_"," ")).strip().casefold()
def historical_next_year(y): return 1 if y==-1 else y+1
def cli_to_astro_year(y): return y+1 if y<0 else y

def parse_year(v):
    if v is None or clean(v)=="": raise ValueError("missing year")
    f=float(v)
    if not f.is_integer(): raise ValueError(f"non-integer year: {v}")
    y=int(f)
    if y==0: raise ValueError("year 0 invalid in historical BCE/CE numbering")
    return y

def identity_key(p):
    wd,sid,wp,name=map(clean,[p.get("Wikidata"),p.get("SeshatID"),p.get("Wikipedia"),p.get("Name")])
    if wd:return f"WD:{wd}","Wikidata"
    if sid:return f"SESHAT:{sid}","SeshatID"
    if wp:return f"WP:{norm_text(wp)}","Wikipedia"
    return f"NAME:{norm_text(name)}","Name"

def canonical(vals):
    vals=[clean(x) for x in vals if clean(x)]
    if not vals:return ""
    c=Counter(vals)
    return sorted(c,key=lambda v:(-c[v],len(v),v.casefold()))[0]

def join_unique(vals): return " | ".join(sorted({clean(x) for x in vals if clean(x)},key=str.casefold))

def write_csv(path,rows,fields):
    with open(path,"w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)

def iter_features(zip_path):
    if Path(zip_path).stat().st_size!=EXPECTED_DATA_ZIP_SIZE: raise RuntimeError("source size mismatch")
    if git_blob_sha1_file(zip_path)!=EXPECTED_DATA_ZIP_GIT_BLOB_SHA1: raise RuntimeError("source Git blob mismatch")
    with zipfile.ZipFile(zip_path) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".geojson")]
        if not names: raise RuntimeError("no GeoJSON in source zip")
        with z.open(sorted(names,key=len)[0]) as s:
            try:
                import ijson
                yield from ijson.items(s,"features.item")
            except ImportError:
                obj=json.load(io.TextIOWrapper(s,encoding="utf-8")); yield from obj.get("features",[])

def build(input_path,outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    rows=[]; qc=[]; propkeys=set(); total=0
    for idx,feat in enumerate(iter_features(input_path)):
        total+=1; p=feat.get("properties") or {}; propkeys.update(p.keys())
        name=clean(p.get("Name")); typ=clean(p.get("Type")).upper(); comps=clean(p.get("Components")); member=clean(p.get("MemberOf"))
        try:
            y0=parse_year(p.get("FromYear")); y1=parse_year(p.get("ToYear"))
            if y0>y1: raise ValueError(f"FromYear > ToYear ({y0}>{y1})")
        except Exception as e:
            qc.append({"RAW_INDEX":idx,"NAME":name,"QC_CODE":"INVALID_YEAR_BOUNDS","DETAIL":str(e)}); continue
        key,basis=identity_key(p)
        rows.append({"RAW_INDEX":idx,"ENTITY_KEY":key,"IDENTITY_BASIS":basis,"NAME":name,"FROM_YEAR":y0,"TO_YEAR":y1,"TYPE":typ,
                     "WIKIDATA":clean(p.get("Wikidata")),"SESHAT_ID":clean(p.get("SeshatID")),"WIKIPEDIA":clean(p.get("Wikipedia")),
                     "MEMBER_OF":member,"COMPONENTS":comps,"HAS_COMPONENTS":bool(comps),"ROW_PRIMARY_ELIGIBLE":typ=="POLITY" and not bool(comps)})
    polity=[r for r in rows if r["TYPE"]=="POLITY"]; relation=[r for r in rows if r["TYPE"]=="RELATION"]
    grouped=defaultdict(list)
    for r in polity: grouped[r["ENTITY_KEY"]].append(r)
    episodes=[]; identity_qc=[]
    for key,rr in grouped.items():
        rr=sorted(rr,key=lambda x:(x["FROM_YEAR"],x["TO_YEAR"],x["RAW_INDEX"]))
        names={x["NAME"] for x in rr if x["NAME"]}
        if len(names)>1: identity_qc.append({"ENTITY_KEY":key,"QC_CODE":"MULTIPLE_NAMES","DETAIL":" | ".join(sorted(names))})
        blocks=[]
        for r in rr:
            if not blocks or r["FROM_YEAR"]>historical_next_year(blocks[-1][-1]["TO_YEAR"]): blocks.append([r])
            else: blocks[-1].append(r)
        for no,blk in enumerate(blocks,1):
            episodes.append({"ENTITY_KEY":key,"IDENTITY_BASIS":blk[0]["IDENTITY_BASIS"],"EPISODE_NO":no,
                "CANONICAL_NAME":canonical(x["NAME"] for x in blk),"NAME_VARIANTS":join_unique(x["NAME"] for x in blk),
                "FROM_YEAR_CLI":min(x["FROM_YEAR"] for x in blk),"TO_YEAR_CLI":max(x["TO_YEAR"] for x in blk),
                "FROM_YEAR_ASTRO":cli_to_astro_year(min(x["FROM_YEAR"] for x in blk)),"TO_YEAR_ASTRO":cli_to_astro_year(max(x["TO_YEAR"] for x in blk)),
                "RAW_ROW_COUNT":len(blk),"WIKIDATA":canonical(x["WIKIDATA"] for x in blk),"SESHAT_ID":canonical(x["SESHAT_ID"] for x in blk),
                "WIKIPEDIA":canonical(x["WIKIPEDIA"] for x in blk),"MEMBER_OF_VALUES":join_unique(x["MEMBER_OF"] for x in blk),
                "COMPONENTS_VALUES":join_unique(x["COMPONENTS"] for x in blk),"HAS_ANY_COMPONENTS":any(x["HAS_COMPONENTS"] for x in blk),
                "PRIMARY_FRAME_ELIGIBLE":all(x["ROW_PRIMARY_ELIGIBLE"] for x in blk)})
    source_min=min(r["FROM_YEAR"] for r in polity); source_max=max(r["TO_YEAR"] for r in polity)
    by=defaultdict(list)
    for e in episodes: by[e["ENTITY_KEY"]].append(e)
    trans=[]; gaps=[]; tid=0
    for key,eps in by.items():
        eps=sorted(eps,key=lambda e:e["EPISODE_NO"])
        for i,e in enumerate(eps):
            tid+=1; y=e["FROM_YEAR_CLI"]; edge=y==source_min
            trans.append({"TRANSITION_ID":f"A4C{tid:06d}","ENTITY_KEY":key,"CANONICAL_NAME":e["CANONICAL_NAME"],"EPISODE_NO":e["EPISODE_NO"],"BOUNDARY":"START",
                "CANDIDATE_CLASS":"FIRST_ENCODED_APPEARANCE" if i==0 else "REAPPEARANCE_AFTER_GAP","CANDIDATE_POLARITY":"POSITIVE_CANDIDATE","YEAR_CLI":y,"YEAR_ASTRO":cli_to_astro_year(y),
                "EDGE_CENSORED":edge,"PRIMARY_FRAME_ELIGIBLE":bool(e["PRIMARY_FRAME_ELIGIBLE"] and not edge),"VALIDATION_STATUS":"UNVALIDATED_CANDIDATE",
                "DO_NOT_INTERPRET_AS":"automatic state formation/independence","WIKIDATA":e["WIKIDATA"],"SESHAT_ID":e["SESHAT_ID"],"WIKIPEDIA":e["WIKIPEDIA"]})
            tid+=1; y2=e["TO_YEAR_CLI"]; edge2=y2==source_max
            trans.append({"TRANSITION_ID":f"A4C{tid:06d}","ENTITY_KEY":key,"CANONICAL_NAME":e["CANONICAL_NAME"],"EPISODE_NO":e["EPISODE_NO"],"BOUNDARY":"END",
                "CANDIDATE_CLASS":"FINAL_ENCODED_APPEARANCE" if i==len(eps)-1 else "DISAPPEARANCE_BEFORE_GAP","CANDIDATE_POLARITY":"NEGATIVE_CANDIDATE","YEAR_CLI":y2,"YEAR_ASTRO":cli_to_astro_year(y2),
                "EDGE_CENSORED":edge2,"PRIMARY_FRAME_ELIGIBLE":bool(e["PRIMARY_FRAME_ELIGIBLE"] and not edge2),"VALIDATION_STATUS":"UNVALIDATED_CANDIDATE",
                "DO_NOT_INTERPRET_AS":"automatic collapse/sovereignty loss","WIKIDATA":e["WIKIDATA"],"SESHAT_ID":e["SESHAT_ID"],"WIKIPEDIA":e["WIKIPEDIA"]})
            if i<len(eps)-1:
                n=eps[i+1]; gaps.append({"ENTITY_KEY":key,"CANONICAL_NAME":e["CANONICAL_NAME"],"EPISODE_BEFORE":e["EPISODE_NO"],"END_BEFORE_CLI":e["TO_YEAR_CLI"],"EPISODE_AFTER":n["EPISODE_NO"],"START_AFTER_CLI":n["FROM_YEAR_CLI"],"NOTE":"True encoded gap"})
    ef=["ENTITY_KEY","IDENTITY_BASIS","EPISODE_NO","CANONICAL_NAME","NAME_VARIANTS","FROM_YEAR_CLI","TO_YEAR_CLI","FROM_YEAR_ASTRO","TO_YEAR_ASTRO","RAW_ROW_COUNT","WIKIDATA","SESHAT_ID","WIKIPEDIA","MEMBER_OF_VALUES","COMPONENTS_VALUES","HAS_ANY_COMPONENTS","PRIMARY_FRAME_ELIGIBLE"]
    tf=["TRANSITION_ID","ENTITY_KEY","CANONICAL_NAME","EPISODE_NO","BOUNDARY","CANDIDATE_CLASS","CANDIDATE_POLARITY","YEAR_CLI","YEAR_ASTRO","EDGE_CENSORED","PRIMARY_FRAME_ELIGIBLE","VALIDATION_STATUS","DO_NOT_INTERPRET_AS","WIKIDATA","SESHAT_ID","WIKIPEDIA"]
    write_csv(outdir/"GLOBAL_POLITY_EPISODES_CANDIDATE.csv",episodes,ef)
    write_csv(outdir/"GLOBAL_TRANSITIONS_CANDIDATE_ALL.csv",trans,tf)
    write_csv(outdir/"GLOBAL_TRANSITIONS_CANDIDATE_PRIMARY.csv",[r for r in trans if r["PRIMARY_FRAME_ELIGIBLE"]],tf)
    write_csv(outdir/"GLOBAL_TRANSITIONS_EDGE_CENSORED.csv",[r for r in trans if r["EDGE_CENSORED"]],tf)
    write_csv(outdir/"GLOBAL_TRANSITIONS_GAPS.csv",gaps,["ENTITY_KEY","CANONICAL_NAME","EPISODE_BEFORE","END_BEFORE_CLI","EPISODE_AFTER","START_AFTER_CLI","NOTE"])
    write_csv(outdir/"GLOBAL_ROW_QC.csv",qc,["RAW_INDEX","NAME","QC_CODE","DETAIL"])
    write_csv(outdir/"GLOBAL_ENTITY_IDENTITY_QC.csv",identity_qc,["ENTITY_KEY","QC_CODE","DETAIL"])
    vf=tf+["REGION_FROZEN","VERIFIED_EVENT_CLASS","VERIFIED_POLARITY","DATE_PRECISION","SOURCE_DATE_WORDING","SOURCE_1","SOURCE_2","SOURCE_3","SOURCE_SUPPORT_SCORE_0_4","DATE_PRECISION_SCORE_0_4","CHRONOLOGY_AGREEMENT_SCORE_0_4","CONTEMPORARY_SOURCE_FLAG","INDEPENDENT_SOURCE_COUNT","VERIFICATION_DECISION","EXCLUSION_REASON","HISTORIAN_NOTE"]
    vrows=[]
    for r in trans:
        v=dict(r)
        for f in vf:v.setdefault(f,"")
        vrows.append(v)
    write_csv(outdir/"GLOBAL_SOURCE_VALIDATION_TEMPLATE.csv",vrows,vf)
    manifest={"protocol_id":"A4_GLOBAL_TRANSITIONS_V2_STAGE_A","status":"CANDIDATE_CENSUS_BUILT_NOT_HISTORICALLY_FROZEN","astronomy_consulted":False,
      "source":{"dataset":"Cliopatria","release":RELEASE,"release_commit":RELEASE_COMMIT,"data_zip_git_blob_sha1":EXPECTED_DATA_ZIP_GIT_BLOB_SHA1,"data_zip_size":EXPECTED_DATA_ZIP_SIZE,"zenodo_version_doi":ZENODO_VERSION_DOI,"input_sha256":sha256_file(input_path)},
      "schema_detected":sorted(propkeys),"counts":{"raw_features_seen":total,"valid_rows":len(rows),"polity_rows":len(polity),"relation_rows_excluded":len(relation),"unique_polity_identity_keys":len(grouped),"polity_episodes":len(episodes),"candidate_transitions_all":len(trans),"candidate_transitions_primary_frame":sum(bool(r["PRIMARY_FRAME_ELIGIBLE"]) for r in trans),"edge_censored_transitions":sum(bool(r["EDGE_CENSORED"]) for r in trans),"true_encoded_gaps":len(gaps),"row_qc_records":len(qc),"identity_qc_records":len(identity_qc)},
      "interpretation_guard":"Cliopatria boundaries are candidates only; Stage-B source verification required","outputs":{}}
    for p in outdir.glob("*.csv"):manifest["outputs"][p.name]={"sha256":sha256_file(p),"bytes":p.stat().st_size}
    (outdir/"MANIFEST_STAGE_A.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
    (outdir/"HISTORICAL_FREEZE_GATE.txt").write_text("NOT FROZEN FOR ASTRONOMICAL TESTING\nStage-B independent historical verification required before any astronomical overlay.\n",encoding="utf-8")
    return manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("input",type=Path); ap.add_argument("--outdir",type=Path,default=Path("A4_STAGE_A_OUTPUT")); a=ap.parse_args()
    m=build(a.input,a.outdir); print(json.dumps(m["counts"],indent=2))
if __name__=="__main__": main()
