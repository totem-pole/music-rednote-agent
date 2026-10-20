"""AFTERTONE v0.5: authorized metadata discovery and evidence auditing (stdlib only)."""
import argparse,datetime,hashlib,html,ipaddress,json,os,re,time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlencode,quote,urlsplit,urlunsplit
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError

DOMAINS={"catalog":["wikipedia.org","musicbrainz.org","discogs.com","allmusic.com","music.apple.com"],"official":["bandcamp.com","music.apple.com"],"critics":["pitchfork.com","daily.bandcamp.com","thequietus.com","pastemagazine.com","stereogum.com"],"community":["rateyourmusic.com","douban.com","albumoftheyear.org","weibo.com"]}
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def make_plan(artist,album):
 b=f'"{artist}" "{album}"'
 rounds={"identity":[b,b+" release edition",b+" tracklist",b+" discography"],"catalog":[b+" site:"+x for x in DOMAINS["catalog"]],"official":[b+" site:"+x for x in DOMAINS["official"]]+[b+" official liner notes",b+" producer recording studio"],"contemporary":[b+" contemporary interview",b+" original release press",b+" local scene history",b+" original musician interview"],"critics":[b+" site:"+x for x in DOMAINS["critics"]]+[b+" professional critical review"],"community":[b+" site:"+x for x in DOMAINS["community"]]+[b+" listeners critique"],"sonic":[b+" arrangement instrumentation",b+" production and mix",b+" track by track",b+" final track structure"],"challenge":[b+" conflicting dates",b+" negative reception",b+" primary-source verification",b+" original-language interviews"]}
 return {"artist":artist,"album":album,"created_at":stamp(),"tasks":[{"id":f"{i:02d}-{j:02d}","round":k,"query":q,"status":"NOT_RUN","results":[]} for i,(k,qs) in enumerate(rounds.items()) for j,q in enumerate(qs,1)]}
def safe_url(url):
 p=urlsplit(url)
 if p.scheme!="https" or not p.hostname or p.username or p.password or p.port not in (None,443):raise ValueError("HTTPS public URL required")
 h=p.hostname.lower().rstrip(".")
 if h=="localhost" or h.endswith((".local",".internal",".test")):raise ValueError("private hostname")
 try:
  ip=ipaddress.ip_address(h)
  if not ip.is_global:raise ValueError("nonpublic address")
 except ValueError as e:
  if str(e)=="nonpublic address":raise
 return urlunsplit(("https",h,p.path or "/",p.query,""))
def get_json(url):
 url=safe_url(url)
 req=Request(url,headers={"User-Agent":"AFTERTONE-Research/0.5 (personal scholarly use)","Accept":"application/json"})
 with urlopen(req,timeout=12) as r:
  if safe_url(r.geturl())!=url:raise ValueError("redirect not approved")
  blob=r.read(2000001)
  if len(blob)>2000000:raise ValueError("response too large")
  return json.loads(blob)
class Visible(HTMLParser):
 def __init__(self):super().__init__();self.bits=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ("script","style","nav","footer"):self.skip+=1
  if t in ("p","li","h1","h2","br"):self.bits.append(" ")
 def handle_endtag(self,t):
  if t in ("script","style","nav","footer"):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip and s.strip():self.bits.append(s)
def plain(value):
 x=Visible();x.feed(value);return re.sub(r"\s+"," "," ".join(x.bits)).strip()
def wiki(query,language="en",fetch=get_json):
 if language not in ("en","zh","ko","ja"):raise ValueError("bad language")
 u=f"https://{language}.wikipedia.org/w/api.php?"+urlencode({"action":"query","list":"search","srsearch":query,"srlimit":5,"format":"json"})
 return [{"url":f"https://{language}.wikipedia.org/wiki/"+quote(x["title"].replace(" ","_")),"title":x["title"],"publisher":"Wikipedia","snippet":plain(x.get("snippet","")),"role":"DISCOVERY_ONLY"} for x in fetch(u).get("query",{}).get("search",[])]
def mb(artist,album,fetch=get_json):
 q=f'releasegroup:"{album}" AND artist:"{artist}"'
 u="https://musicbrainz.org/ws/2/release-group/?"+urlencode({"query":q,"fmt":"json","limit":5})
 return [{"url":"https://musicbrainz.org/release-group/"+x["id"],"title":x.get("title",album),"publisher":"MusicBrainz","snippet":x.get("first-release-date",""),"role":"CROWDSOURCED_METADATA"} for x in fetch(u).get("release-groups",[]) if x.get("id")]
def brave(query,key):
 if not key:raise ValueError("BRAVE_SEARCH_API_KEY not configured")
 u="https://api.search.brave.com/res/v1/web/search?"+urlencode({"q":query,"count":8})
 with urlopen(Request(u,headers={"X-Subscription-Token":key,"Accept":"application/json"}),timeout=15) as r:res=json.loads(r.read(2000000))
 return [{"url":x["url"],"title":x.get("title",""),"publisher":urlsplit(x["url"]).hostname,"snippet":plain(x.get("description","")),"role":"SEARCH_LEAD"} for x in res.get("web",{}).get("results",[]) if x.get("url")]
def canonical(u):
 p=urlsplit(safe_url(u));return urlunsplit((p.scheme,p.netloc,p.path.rstrip("/") or "/",p.query,""))
def sources_from(rows,qid):
 seen={}
 for x in rows:
  try:u=canonical(x["url"])
  except (ValueError,KeyError):continue
  seen[u]={"id":hashlib.sha256(u.encode()).hexdigest()[:16],"url":u,"title":x.get("title",""),"publisher":x.get("publisher",""),"snippet":x.get("snippet","")[:800],"role":x.get("role","SEARCH_LEAD"),"query_id":qid,"retrieved_at":stamp(),"status":"DISCOVERED_NOT_READ","independence_group":urlsplit(u).hostname}
 return list(seen.values())
def conflict(claims):
 groups={}
 for x in claims:
  if x.get("type") not in ("FACT","REPORTED_FACT"):continue
  k=(x.get("subject"),x.get("predicate"),x.get("edition"))
  if k[0] and k[1]:groups.setdefault(k,[]).append(x)
 return [{"scope":list(k),"values":sorted({str(z.get("value")) for z in items}),"status":"UNRESOLVED"} for k,items in groups.items() if len({str(z.get("value")) for z in items})>1]
def corroboration(claims,sources):
 by={x["id"]:x for x in sources};out=[]
 for c in claims:
  if c.get("type") not in ("FACT","REPORTED_FACT"):continue
  chains={by[i].get("origin_chain") or by[i].get("independence_group") for i in c.get("source_ids",[]) if i in by and by[i].get("status")=="READ"}
  if len(chains)<2:out.append({"claim_id":c.get("id"),"independent_chains":len(chains),"status":"NEEDS_CORROBORATION"})
 return out
def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def run(plan,mode,max_tasks=8,delay=1.2):
 results=[];count=0
 for task in plan["tasks"]:
  if task["status"]!="NOT_RUN" or count>=max_tasks:continue
  if mode=="metadata" and not any(d in task["query"] for d in ("wikipedia.org","musicbrainz.org")):continue
  count+=1
  try:
   q=task["query"]
   if "musicbrainz.org" in q:found=mb(plan["artist"],plan["album"])
   elif "wikipedia.org" in q:found=wiki(plan["artist"]+" "+plan["album"],"zh" if re.search("[一-鿿]",plan["artist"]) else "en")
   elif mode=="brave":found=brave(q,os.environ.get("BRAVE_SEARCH_API_KEY",""))
   else:continue
   batch=sources_from(found,task["id"]);results.extend(batch);task["results"]=[s["id"] for s in batch];task["status"]="SUCCESS" if batch else "NOT_FOUND"
  except (HTTPError,URLError,TimeoutError,ValueError,KeyError,json.JSONDecodeError) as e:task["status"]="ERROR";task["error"]=str(e)[:150]
  task["finished_at"]=stamp()
  if delay and count<max_tasks:time.sleep(delay)
 return results
def audit(plan,sources,claims):
 return {"created_at":stamp(),"artist":plan["artist"],"album":plan["album"],"query_total":len(plan["tasks"]),"attempted":sum(t["status"]!="NOT_RUN" for t in plan["tasks"]),"statuses":{s:sum(t["status"]==s for t in plan["tasks"]) for s in set(t["status"] for t in plan["tasks"])},"source_leads":len(sources),"sources_actually_read":sum(s.get("status")=="READ" for s in sources),"conflicts":conflict(claims),"uncorroborated":corroboration(claims,sources),"publishable":False,"notes":"Search leads are not read articles; human listening, copyright, originality and approval checks required."}
def main():
 p=argparse.ArgumentParser();p.add_argument("action",choices=["plan","discover","audit"]);p.add_argument("--folder",type=Path,required=True);p.add_argument("--artist");p.add_argument("--album");p.add_argument("--mode",choices=["metadata","brave"],default="metadata");p.add_argument("--max-tasks",type=int,default=8);a=p.parse_args();f=a.folder
 if a.action=="plan":
  if not a.artist or not a.album:p.error("album and artist required")
  save(f/"plan.json",make_plan(a.artist,a.album));return
 plan=json.loads((f/"plan.json").read_text(encoding="utf8"))
 sources=json.loads((f/"sources.json").read_text(encoding="utf8")) if (f/"sources.json").exists() else []
 claims=json.loads((f/"claims.json").read_text(encoding="utf8")) if (f/"claims.json").exists() else []
 if a.action=="discover":
  sources=list({s["url"]:s for s in sources+run(plan,a.mode,a.max_tasks)}.values());save(f/"plan.json",plan);save(f/"sources.json",sources)
 save(f/"audit.json",audit(plan,sources,claims))
if __name__=="__main__":main()
