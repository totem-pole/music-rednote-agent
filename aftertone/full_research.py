"""Eight-round executed research with auditable query attempts and explicit source limitations.

No browser credential handling, no RYM evasion. Uses an optional Brave API key; otherwise
Wikipedia/MusicBrainz public searches cover only the supported tasks. All unsupported tasks
are tagged CONFIG_REQUIRED, not presented as executed.
"""
import argparse,json,os,time,datetime,re,unicodedata
from pathlib import Path
import urllib.request,urllib.parse,xml.etree.ElementTree as ET

from urllib.error import HTTPError,URLError
from .engine import make_plan,wiki,mb,brave,sources_from,save,stamp
from .evidence import retrieve_article,claim_candidates,similarity_report
from .engine import corroboration,conflict

ALBUMS=[("chen","陈淑桦","一生守候"),("say-sue-me","Say Sue Me","Where We Were Together")]
def bing_rss(query):
    """Public search RSS, optional and untrusted; may be blocked. Never spoof successful search."""
    url="https://www.bing.com/search?"+urllib.parse.urlencode({"q":query,"format":"rss"})
    req=urllib.request.Request(url,headers={"User-Agent":"AFTERTONE/0.8 research search client","Accept":"application/rss+xml,application/xml"})
    with urllib.request.urlopen(req,timeout=10) as res:
        raw=res.read(500000)
    root=ET.fromstring(raw)
    return [{"url":i.findtext("link",""),"title":i.findtext("title",""),"snippet":i.findtext("description",""),"publisher":"Bing RSS","role":"SEARCH_LEAD"} for i in root.findall(".//item") if i.findtext("link")]

def relevant_result(row, artist, album):
    """Reject obviously unrelated search pages; keep only album/artist name matches.
    This is a *candidate* filter, not a source credibility judgment.
    """
    hay=unicodedata.normalize("NFKC",(str(row.get("title",""))+" "+str(row.get("snippet",""))+" "+str(row.get("url",""))).lower())
    a=unicodedata.normalize("NFKC",artist).lower()
    b=unicodedata.normalize("NFKC",album).lower()
    return a in hay or b in hay

def execute_queries(artist,album,search=None,pause=.25):
    plan=make_plan(artist,album)
    discovered={}; logs=[]
    for task in plan["tasks"]:
        kind=task["round"]; q=task["query"]; provider="web-search" if search else "metadata"
        try:
            if search:rows=search(q)
            elif "site:wikipedia.org" in q:rows=wiki(f'"{artist}" "{album}"',"zh" if artist=="陈淑桦" else "en")
            elif "site:musicbrainz.org" in q:rows=mb(artist,album)
            else:
                task["status"]="CONFIG_REQUIRED"
                logs.append({"id":task["id"],"round":kind,"query":q,"provider":"brave","status":"CONFIG_REQUIRED"})
                continue
            relevant=[x for x in rows if relevant_result(x,artist,album)]
            batch=sources_from(relevant,task["id"])
            task["status"]="SUCCESS" if batch else "NO_RESULTS"
            task["results"]=[x["id"] for x in batch]
            for row in batch:discovered[row["url"]]=row
            logs.append({"id":task["id"],"round":kind,"query":q,"provider":provider,"status":task["status"],"result_count":len(batch),"raw_result_count":len(rows)})
        except (HTTPError,URLError,ValueError,TimeoutError,KeyError,TypeError) as exc:
            task["status"]="ERROR"
            logs.append({"id":task["id"],"round":kind,"query":q,"provider":provider,"status":"ERROR","error":str(exc)[:180]})
        if pause:time.sleep(pause)
    return {"plan":plan,"queries":logs,"sources":list(discovered.values())}

def score_coverage(pack):
    tasks=pack["queries"];successful=[r for r in tasks if r["status"] in ("SUCCESS","NO_RESULTS")]
    return {"planned":len(tasks),"executed":len(successful)+sum(x["status"]=="ERROR" for x in tasks),
      "config_required":sum(x["status"]=="CONFIG_REQUIRED" for x in tasks),
      "by_round":{r:{"attempted":sum(x["round"]==r and x["status"]!="CONFIG_REQUIRED" for x in tasks),
                       "success":sum(x["round"]==r and x["status"]=="SUCCESS" for x in tasks)}
                  for r in sorted({x["round"] for x in tasks})},
      "unique_source_leads":len(pack["sources"]),
      "eight_rounds_executed":all(any(x["round"]==r and x["status"]!="CONFIG_REQUIRED" for x in tasks)
                                 for r in {x["round"] for x in tasks})}

def run_all(folder,search=None):
    out={}
    for slug,artist,album in ALBUMS:
        pack=execute_queries(artist,album,search=search)
        pack["coverage"]=score_coverage(pack)
        dest=Path(folder)/slug
        for k in ("plan","queries","sources","coverage"):save(dest/(k+".json"),pack[k])
        out[slug]=pack["coverage"]
        print(slug,json.dumps(pack["coverage"],ensure_ascii=False),flush=True)
    save(Path(folder)/"summary.json",out)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",default="artifacts/eight-round")
    p.add_argument("--mode",choices=["metadata","brave","bing-rss"],default="metadata")
    args=p.parse_args()
    key=os.getenv("BRAVE_SEARCH_API_KEY","")
    if args.mode=="brave" and not key:raise SystemExit("BRAVE_SEARCH_API_KEY required for eight-round full web search; NOT claiming success")
    run_all(args.output,search=(lambda q:brave(q,key)) if args.mode=="brave" else (bing_rss if args.mode=="bing-rss" else None))
if __name__=="__main__":main()
