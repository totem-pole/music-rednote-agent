"""E2E broad source sweep: 32+ real HTTP attempts across both records.
Produces objective fetch manifest, source previews, coverage and no fictitious LLM claims.
"""
import json,pathlib,datetime,urllib.request,urllib.error,urllib.parse,time,re,hashlib
from html.parser import HTMLParser
ROOT=pathlib.Path("artifacts/full-sweep")
SOURCE={
"chen":[
("official","https://music.apple.com/tw/album/%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99/151352199"),
("encyclopedia","https://zh.wikipedia.org/wiki/%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
("community","https://rateyourmusic.com/artist/sarah-chen"),
("community","https://www.douban.com/search?q=%E9%99%88%E6%B7%91%E6%A1%A6%20%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
("catalog","https://musicbrainz.org/search?query=%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99&type=release_group&method=indexed"),
("catalog","https://www.discogs.com/search/?q=%E9%99%88%E6%B7%91%E6%A1%A6+%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99&type=all"),
("historical","https://www.rock.com.tw/"),
("news","https://www.google.com/search?q=%E9%99%88%E6%B7%91%E6%A1%A6+%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99+%E8%A3%BD%E4%BD%9C%E4%BA%BA"),
("social","https://s.weibo.com/weibo?q=%E9%99%88%E6%B7%91%E6%A1%A6%20%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
("catalog","https://www.allmusic.com/search/albums/%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
("streaming","https://music.apple.com/tw/song/151352203"),
("review","https://search.douban.com/music/subject_search?search_text=%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99"),
("news","https://www.google.com/search?q=%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99+%E9%99%B3%E6%B7%91%E6%A8%BA+%E6%BB%BE%E7%9F%B3"),
("encyclopedia","https://zh.wikipedia.org/wiki/%E9%99%B3%E6%B7%91%E6%A8%BA"),
("catalog","https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99&language=zh&format=json"),
("lyrics","https://www.google.com/search?q=%E4%B8%80%E7%94%9F%E5%AE%88%E5%80%99+%E5%B0%8F%E8%9F%B2+%E7%8E%8B%E6%B2%BB%E5%B9%B3")],
"say-sue-me":[
("official","https://www.damnably.com/release/where-we-were-together/"),
("official","https://electricmuse.bandcamp.com/album/where-we-were-together"),
("interview","https://daily.bandcamp.com/features/say-sue-me-where-we-were-together-interview"),
("interview","https://drownedinsound.com/in_depth/4151615-discover--say-sue-me"),
("interview","https://kexp.org/read/2018/4/3/say-sue-me-pens-heartfelt-expansive-epic-coming-end-kexp-premiere/"),
("review","https://pitchfork.com/reviews/albums/say-sue-me-where-we-were-together/"),
("review","https://thefirenote.com/reviews/say-sue-me-where-we-were-together-album-review/"),
("review","https://collective-zine.co.uk/2018/04/22/say-sue-me-where-we-were-together-lp-2018/"),
("review","https://spillmagazine.com/spill-album-review-say-sue-me-where-we-were-together/"),
("review","https://www.indieforbunnies.com/2018/04/27/say-sue-me-where-we-were-together/"),
("catalog","https://musicbrainz.org/label/3f19f500-a241-45e2-8c46-4f309d81a054"),
("community","https://rateyourmusic.com/release/album/say-sue-me/where-we-were-together/"),
("community","https://www.albumoftheyear.org/releases/2018-say-sue-me-where-we-were-together.php"),
("encyclopedia","https://en.wikipedia.org/wiki/Where_We_Were_Together"),
("review","https://pitchfork.com/reviews/tracks/say-sue-me-old-town/"),
("artist","https://daily.bandcamp.com/best-of-2018/artist-reflections-say-sue-me-on-becoming-a-full-time-band-in-2018")]
}
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.skip=0;self.data=[]
 def handle_starttag(self,t,a):
  if t in ("script","style","nav","footer","noscript"):self.skip+=1
 def handle_endtag(self,t):
  if t in ("script","style","nav","footer","noscript"):self.skip=max(0,self.skip-1)
 def handle_data(self,x):
  if not self.skip and x.strip():self.data.append(x.strip())
def run():
 ROOT.mkdir(parents=True,exist_ok=True);allr={}
 for album,items in SOURCE.items():
  rs=[]
  for category,url in items:
   status="ERROR";details={}
   try:
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; AFTERTONE/0.7; editorial research)","Accept":"text/html,application/json"})
    with urllib.request.urlopen(req,timeout=11) as resp:
     raw=resp.read(350000).decode("utf-8","replace");p=Parser();p.feed(raw)
     cleaned=re.sub(r"\s+"," "," ".join(p.data)).strip()
     status="READ" if len(cleaned)>=120 else "THIN"
     details={"http":resp.status,"chars":len(cleaned),"sha256":hashlib.sha256(cleaned.encode()).hexdigest(),"excerpt":cleaned[:350]}
   except Exception as ex:details={"error":str(ex)[:180]}
   item={"category":category,"url":url,"status":status,**details};rs.append(item)
   print(album,category,status,details.get("http"),details.get("chars"),details.get("error",""),flush=True)
   time.sleep(.45)
  allr[album]=rs
 (ROOT/"source-manifest.json").write_text(json.dumps(allr,ensure_ascii=False,indent=2),encoding="utf8")
 print("SUMMARY",json.dumps({k:{"attempts":len(v),"read":sum(r["status"]=="READ" for r in v),"domains":len(set(urllib.parse.urlsplit(r["url"]).hostname for r in v if r["status"]=="READ"))} for k,v in allr.items()}),flush=True)
if __name__=="__main__":run()
