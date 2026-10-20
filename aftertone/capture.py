"""Offline-safe editorial pipeline on *actual* discovery artifacts.

Reads search results, fetches only approved public-host pages,
generates source evidence and QUOTE candidates. Does not claim semantics verified.
"""
import argparse,collections,json,re,time
from pathlib import Path
from .evidence import retrieve_article,claim_candidates,similarity_report,quality_gate,save_json
from .provenance import final_claim_audit

HOSTS=("wikipedia.org","musicbrainz.org","pitchfork.com","daily.bandcamp.com","damnably.com",
       "kexp.org","drownedinsound.com","electricmuse.bandcamp.com","music.apple.com",
       "thequietus.com","pastemagazine.com","stereogum.com","allmusic.com",
       "discogs.com","douban.com","rateyourmusic.com")
PRIORITY=("damnably.com","daily.bandcamp.com","kexp.org","pitchfork.com","music.apple.com",
          "musicbrainz.org","wikipedia.org")
def rank(source):
    url=source["url"]
    return (next((i for i,h in enumerate(PRIORITY) if h in url),len(PRIORITY)),
            0 if source.get("title") else 1)
def capture(album_folder,limit=12,fetch=None):
    folder=Path(album_folder);leads=json.loads((folder/"sources.json").read_text(encoding="utf-8"))
    source_by_url={x["url"]:x for x in leads}
    selected=sorted(leads,key=rank)
    done=0;per_host=collections.Counter();reads=[];failures=[];seen_hashes=set();thin=[];duplicates=[]
    for row in selected:
        if done>=limit:break
        try:
            from urllib.parse import urlsplit
            host=urlsplit(row["url"]).hostname or ""
            if not any(host==h or host.endswith("."+h) for h in HOSTS):continue
            if per_host[host]>=2:continue
            per_host[host]+=1;done+=1
            d=retrieve_article(row["url"],HOSTS,fetch=fetch)
            if len(d["text"])<500:
                row["status"]="THIN_CONTENT";thin.append({"source_id":row["id"],"chars":len(d["text"])});continue
            if d["text_sha256"] in seen_hashes:
                row["status"]="DUPLICATE_CONTENT";duplicates.append(row["id"]);continue
            seen_hashes.add(d["text_sha256"])
            path=folder/"pages"/(row["id"]+".txt");path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(d["text"],encoding="utf-8")
            row["status"]="READ";row["text_sha256"]=d["text_sha256"];row["retrieved_at"]=d["retrieved_at"]
            reads.append({"source_id":row["id"],"publisher":row["publisher"],"chars":len(d["text"]),"url":row["url"]})
        except Exception as e:
            row["status"]="ACCESS_FAILED";row["error"]=str(e)[:160]
            failures.append({"source_id":row["id"],"reason":str(e)[:160]})
        if fetch is None:time.sleep(.4)
    save_json(folder/"sources.json",list(source_by_url.values()))
    candidates=[];documents={}
    for s in source_by_url.values():
        p=folder/"pages"/(s["id"]+".txt")
        if s.get("status")=="READ" and p.exists():
            txt=p.read_text(encoding="utf-8");documents[s["id"]]=txt
            candidates+=claim_candidates(txt,s["id"],max_items=12)
    report={"attempted_read":done,"read":len(reads),"read_sources":reads,"failed":failures,"thin":thin,"duplicates":duplicates,"independent_host_count":len({r["url"].split("/")[2] for r in reads}),
            "unverified_candidates":len(candidates),"claims_automatically_verified":0,
            "requires_semantic_review":True,"ready_for_publication":False}
    save_json(folder/"candidate-claims.json",candidates)
    save_json(folder/"read-audit.json",report)
    return report

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",default="artifacts/eight-round");p.add_argument("--limit",type=int,default=12)
    a=p.parse_args()
    root=Path(a.root)
    for slug in ("chen","say-sue-me"):
        try:r=capture(root/slug,limit=a.limit);print(slug,json.dumps(r,ensure_ascii=False)[:1000],flush=True)
        except Exception as e:print(slug,"CAPTURE_ERROR",str(e)[:200],flush=True)
if __name__=="__main__":main()
