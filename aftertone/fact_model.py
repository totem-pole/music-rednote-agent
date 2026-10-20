"""Model-assisted claim extraction with machine-checkable verbatim locations.

The model proposes facts; only exact quotes are accepted as documentary support.
Semantic truth / two-independent-origin verification always remains distinct.
"""
import argparse,json,os,pathlib
from .writer import call_llm
from .provenance import locate_quote,source_independence
from .evidence import save_json

def extract_prompt(text,source):
    return {"instruction":"Extract up to 12 useful atomic music-history/production facts. Do not infer. Respond JSON with claims array; each has claim, subject, predicate, value, edition, quote. quote must be a verbatim continuous excerpt of at least 12 characters from the source. If none, return empty array.",
            "source_id":source["id"],"url":source["url"],"document":text[:11000]}
def produce_candidates(source,text,model_fn):
    raw=model_fn(extract_prompt(text,source))
    if not isinstance(raw,dict) or not isinstance(raw.get("claims"),list):raise ValueError("model did not return claims list")
    valid=[];invalid=[]
    for i,c in enumerate(raw["claims"][:12]):
        if not isinstance(c,dict):continue
        quote=str(c.get("quote",""));span=locate_quote(text,quote)
        obj={"id":source["id"]+"-"+str(i),"claim":c.get("claim"),"subject":c.get("subject"),"predicate":c.get("predicate"),"value":c.get("value"),"edition":c.get("edition"),"source_ids":[source["id"]],"evidence":[{"source_id":source["id"],"quote":quote,"span":span}],"type":"REPORTED_FACT","status":"QUOTE_LOCATED" if span else "UNVERIFIED"}
        (valid if span else invalid).append(obj)
    return {"located":valid,"rejected":invalid}
def album_extract(folder,model_fn):
    f=pathlib.Path(folder);src=json.loads((f/"sources.json").read_text(encoding="utf8"))
    located=[];invalid=[]
    for s in src:
        p=f/"pages"/(s["id"]+".txt")
        if s.get("status")!="READ" or not p.exists():continue
        res=produce_candidates(s,p.read_text(encoding="utf8"),model_fn)
        located+=res["located"];invalid+=res["rejected"]
    save_json(f/"claim-ledger-candidates.json",located)
    save_json(f/"rejected-claims.json",invalid)
    return {"located":len(located),"rejected":len(invalid),"fully_verified":0}
def main():
    p=argparse.ArgumentParser();p.add_argument("--folder",required=True);a=p.parse_args()
    def invoke(prompt):
        return call_llm(prompt,os.getenv("LLM_BASE_URL","https://api.openai.com/v1").rstrip("/"),os.getenv("LLM_API_KEY",""),os.getenv("LLM_MODEL",""))
    print(json.dumps(album_extract(a.folder,invoke),ensure_ascii=False))
if __name__=="__main__":main()
