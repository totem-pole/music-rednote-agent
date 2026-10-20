"""Network smoke/integration runner. Operates only on explicit public provider URLs.
Writes actual HTTP statuses, metadata, evidence snippets and no publication artifacts.
"""
import json,time,urllib.request,urllib.error,urllib.parse,datetime,pathlib,hashlib,re
BASE=pathlib.Path("artifacts/integration")
ALBUMS=[("chen","陈淑桦","一生守候","zh"),("say-sue-me","Say Sue Me","Where We Were Together","en")]
def fetch(url):
 req=urllib.request.Request(url,headers={"User-Agent":"AFTERTONE-MusicResearch/0.7 (research project; contact via GitHub)","Accept":"application/json,text/html"})
 start=time.monotonic()
 try:
  with urllib.request.urlopen(req,timeout=14) as resp:
   b=resp.read(350000)
   return {"status":"SUCCESS","http":resp.status,"bytes":len(b),"content":b.decode("utf-8","replace"),"elapsed":round(time.monotonic()-start,2)}
 except Exception as e:return {"status":"ERROR","error":str(e)[:250],"elapsed":round(time.monotonic()-start,2)}
def sources(artist,album,lang):
 q=urllib.parse.urlencode({"action":"query","list":"search","srsearch":artist+" "+album,"format":"json","srlimit":5})
 mb=urllib.parse.urlencode({"query":f'releasegroup:"{album}" AND artist:"{artist}"',"fmt":"json","limit":5})
 return {"wikipedia":f"https://{lang}.wikipedia.org/w/api.php?{q}","musicbrainz":f"https://musicbrainz.org/ws/2/release-group/?{mb}","itunes":"https://itunes.apple.com/search?"+urllib.parse.urlencode({"term":artist+" "+album,"entity":"album","limit":5})}
def summarize(key,r):
 out={k:v for k,v in r.items() if k!="content"}
 if r["status"]=="SUCCESS":
  try:
   j=json.loads(r["content"])
   out["match_count"]=len(j.get("results",[]) if key=="itunes" else j.get("query",{}).get("search",[]) if key=="wikipedia" else j.get("release-groups",[]))
   out["matches"]=[{"title":v.get("collectionName") or v.get("title"),"artist":v.get("artistName"),"date":v.get("releaseDate")} for v in j.get("results",[])[:5]] if key=="itunes" else []
  except Exception as e:out["parse_error"]=str(e)
  out["sha256"]=hashlib.sha256(r["content"].encode()).hexdigest()
 return out
def main():
 BASE.mkdir(parents=True,exist_ok=True)
 overall=[]
 for slug,artist,album,lang in ALBUMS:
  outcomes={}
  for k,url in sources(artist,album,lang).items():
   r=fetch(url);outcomes[k]=summarize(k,r);outcomes[k]["url"]=url
   print(slug,k,r["status"],r.get("http"),outcomes[k].get("match_count"),flush=True)
   time.sleep(1.1)
  report={"artist":artist,"album":album,"generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"results":outcomes,"editorial_ready":False}
  (BASE/(slug+".json")).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
  overall.append(report)
 (BASE/"summary.json").write_text(json.dumps({"albums":len(overall),"succeeded":sum(x["status"]=="SUCCESS" for a in overall for x in a["results"].values()),"total_requests":6,"editorial_ready":False},indent=2),encoding="utf-8")
if __name__=="__main__":main()
