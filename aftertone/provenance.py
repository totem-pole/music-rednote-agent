"""Verifiable quote/claim location; no model can promote unlocated claims to VERIFIED."""
import hashlib,json,re
from .engine import corroboration,conflict

def locate_quote(text,quote):
    if not quote or len(quote)<12:return None
    pos=text.find(quote)
    if pos<0:return None
    return {"start":pos,"end":pos+len(quote),"sha256":hashlib.sha256(quote.encode()).hexdigest()}

def inspect_claims(claims,sources,documents):
    by={s["id"]:s for s in sources}
    checked=[]
    for c in claims:
        result={**c,"verified_spans":[],"errors":[],"status":"UNVERIFIED"}
        for e in c.get("evidence",[]):
            sid=e.get("source_id");src=by.get(sid);text=documents.get(sid,"")
            if not src or src.get("status")!="READ" or not text:
                result["errors"].append("source not read: "+str(sid));continue
            span=locate_quote(text,e.get("quote",""))
            if span is None:result["errors"].append("quote absent: "+str(sid));continue
            result["verified_spans"].append({"source_id":sid,**span})
        # Located evidence shows presence only, NOT semantic truth.
        result["status"]="QUOTE_LOCATED" if result["verified_spans"] and not result["errors"] else "UNVERIFIED"
        checked.append(result)
    return checked

def source_independence(claim,sources):
    by={s["id"]:s for s in sources};chains={}
    for e in claim.get("verified_spans",[]):
        s=by.get(e["source_id"],{})
        if s:
            # Different domains alone DO NOT imply independent content.
            chain=s.get("origin_chain")
            if chain:chains.setdefault(chain,[]).append(e["source_id"])
    return {"independent_chains":len(chains),"chains":chains,"cross_verified":len(chains)>=2}

def final_claim_audit(claims,sources,documents):
    located=inspect_claims(claims,sources,documents)
    return {"claims":located,"corroboration":[{"id":c.get("id"),**source_independence(c,sources)} for c in located],
            "semantic_review_required":True,"can_auto_mark_verified":False}

def extract_documents(folder,sources):
    from pathlib import Path
    path=Path(folder)/"pages";return {s["id"]:(path/(s["id"]+".txt")).read_text(encoding="utf-8") for s in sources if (path/(s["id"]+".txt")).exists()}
