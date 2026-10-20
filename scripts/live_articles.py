"""Live article-layer integration: retrieve several official/press pages, extract, record failures.
No fake listening or automatic editorial approval.
"""
from __future__ import annotations
import pathlib,json,urllib.request,urllib.error,hashlib,time,datetime,sys
from html.parser import HTMLParser

ALBUMS={
"chen":[
 ("Wikipedia","https://zh.wikipedia.org/wiki/%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
 ("Apple Music","https://music.apple.com/us/song/663690219"),
 ("RYM","https://rateyourmusic.com/release/album/sarah-chen/")],
"say-sue-me":[
 ("Damnably","https://www.damnably.com/release/where-we-were-together/"),
 ("Electric Muse","https://electricmuse.bandcamp.com/album/where-we-were-together"),
 ("Pitchfork","https://pitchfork.com/reviews/albums/say-sue-me-where-we-were-together/"),
 ("RYM","https://rateyourmusic.com/release/album/say-sue-me/where-we-were-together/")]}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ("script","style","nav","footer"):self.skip+=1
  if t in ("p","h1","h2","li"):self.parts.append(" ")
 def handle_endtag(self,t):
  if t in ("script","style","nav","footer"):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
def retrieve(url):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; AFTERTONE/0.7; personal research)","Accept":"text/html"})
  with urllib.request.urlopen(req,timeout=12) as r:
   buf=r.read(400001)
   if len(buf)>400000:buf=buf[:400000]
   p=Parser();p.feed(buf.decode("utf8","replace"))
   content=" ".join(p.parts)
   return {"status":"READ" if len(content)>=120 else "INSUFFICIENT_TEXT","http":r.status,"chars":len(content),"sha256":hashlib.sha256(content.encode()).hexdigest(),"excerpt":content[:450]}
 except Exception as e:return {"status":"ERROR","error":str(e)[:180]}
def main():
 folder=pathlib.Path("artifacts/integration");folder.mkdir(parents=True,exist_ok=True)
 summary={}
 for slug,items in ALBUMS.items():
  records=[]
  for name,url in items:
   r={"publisher":name,"url":url,"observed_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),**retrieve(url)}
   records.append(r);print(slug,name,r["status"],r.get("http"),r.get("chars"),r.get("error",""),flush=True);time.sleep(1.0)
  summary[slug]=records
 (folder/"articles.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
 print("Full-text usable",sum(x["status"]=="READ" for a in summary.values() for x in a),"/",sum(len(x) for x in summary.values()),flush=True)
if __name__=="__main__":main()
