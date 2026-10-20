"""AFTERTONE research planner and evidence helpers; standard library only.
This module DOES NOT execute web searches; a permitted search connector is required.
"""
import argparse,datetime as dt,hashlib,html,json,re,urllib.parse
from html.parser import HTMLParser
from pathlib import Path

SITES={
"catalog":["wikipedia.org","musicbrainz.org","discogs.com","allmusic.com","music.apple.com"],
"primary":["bandcamp.com","damnably.com"],
"critics":["pitchfork.com","daily.bandcamp.com","thequietus.com","stereogum.com","pastemagazine.com"],
"community":["rateyourmusic.com","douban.com","albumoftheyear.org","weibo.com"]}
ROUNDS=["identity","catalog","primary","historical","critics","community","sonic","challenge"]

def plan(artist,album):
    base=f'"{artist}" "{album}"'
    patterns=[
        [base,base+" release tracklist",base+" original pressing"],
        [base+" site:"+site for site in SITES["catalog"]],
        [base+" site:"+site for site in SITES["primary"]]+[base+" official liner notes credits"],
        [base+" original interview recording",base+" contemporary press"],
        [base+" site:"+site for site in SITES["critics"]],
        [base+" site:"+site for site in SITES["community"]],
        [base+" instrumentation arrangement",base+" track by track production"],
        [base+" contradictory release dates",base+" negative critical reception"]]
    return [{"round":name,"query":q,"status":"NOT_RUN"} for name,qs in zip(ROUNDS,patterns) for q in qs]

def canonical(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme not in ("http","https") or not p.hostname:raise ValueError("http(s) only")
    host=p.hostname.lower()
    if host in ("localhost",) or host.endswith(".local") or host.startswith(("127.","10.","192.168.","169.254.")):
        raise ValueError("private host rejected")
    return urllib.parse.urlunsplit(("https",host,p.path.rstrip("/") or "/",p.query,""))

class VisibleText(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.ignored=0
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","nav","footer"):self.ignored+=1
    def handle_endtag(self,tag):
        if tag in ("script","style","nav","footer"):self.ignored=max(0,self.ignored-1)
    def handle_data(self,data):
        if not self.ignored and data.strip():self.parts.append(html.unescape(data.strip()))

def extract_document(source):
    parser=VisibleText();parser.feed(source)
    return re.sub(r"\s+"," "," ".join(parser.parts)).strip()

def evidence(url,text,publisher,role):
    normalized=canonical(url)
    return {"id":hashlib.sha256(normalized.encode()).hexdigest()[:12],
            "url":normalized,"publisher":publisher,"role":role,
            "retrieved_at":dt.datetime.now(dt.timezone.utc).isoformat(),
            "text_sha256":hashlib.sha256(text.encode()).hexdigest(),
            "excerpt":text[:2000],"access_status":"SUCCESS"}

def conflicts(claims):
    scoped={}
    for c in claims:
        key=(c.get("subject"),c.get("property"),c.get("edition"))
        if all(key[:2]):scoped.setdefault(key,[]).append(c)
    return [{"scope":list(key),"values":sorted({str(c.get("value")) for c in group}),
             "claim_ids":[c.get("id") for c in group]}
            for key,group in scoped.items() if len({str(c.get("value")) for c in group})>1]

def main():
    p=argparse.ArgumentParser();p.add_argument("action",choices=["plan","extract","conflicts"])
    p.add_argument("--artist");p.add_argument("--album");p.add_argument("--input",type=Path);p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.action=="plan":
        if not a.artist or not a.album:p.error("artist and album required")
        result={"artist":a.artist,"album":a.album,"queries":plan(a.artist,a.album)}
    else:
        if not a.input:p.error("input required")
        content=a.input.read_text(encoding="utf-8")
        result={"text":extract_document(content)} if a.action=="extract" else conflicts(json.loads(content))
    output=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(output,encoding="utf-8")
    else:print(output)

if __name__=="__main__":main()
