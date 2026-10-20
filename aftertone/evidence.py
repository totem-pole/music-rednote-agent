"""Auditable source ingestion, conservative evidence extraction and text quality gates."""
from __future__ import annotations
import hashlib, html, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from .engine import safe_url, stamp

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("redirect blocked: review destination manually")

class ArticleParser(HTMLParser):
    """Extract visible text while skipping page chrome and embedded scripts."""
    SKIP={"script","style","noscript","nav","footer","header","svg","form"}
    def __init__(self):
        super().__init__(); self.skip=[]; self.out=[]; self.title=[]; self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in self.SKIP:self.skip.append(tag)
        if tag=="title":self.in_title=True
        if tag in ("p","article","section","h1","h2","h3","li","blockquote","br") and not self.skip:self.out.append("\n")
    def handle_endtag(self,tag):
        if self.skip and tag==self.skip[-1]:self.skip.pop()
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if not self.skip and not self.in_title:self.out.append(data)
def parse_html(raw):
    p=ArticleParser();p.feed(raw)
    body="\n".join(x.strip() for x in "".join(p.out).splitlines() if x.strip())
    return {"title":html.unescape(" ".join(p.title).strip()),"text":html.unescape(body)[:60000]}

def permitted_url(url,allow_hosts):
    safe_url(url)
    host=(urlsplit(url).hostname or "").lower()
    if not any(host==allowed or host.endswith("."+allowed) for allowed in allow_hosts):
        raise ValueError("host not allowlisted")
    return url

def retrieve_article(url,allow_hosts,fetch=None):
    """Fetch one explicitly approved public HTML document; no redirects or credentials."""
    permitted_url(url,allow_hosts)
    if fetch is None:
        def fetch(value):
            opener=build_opener(NoRedirect)
            with opener.open(Request(value,headers={"User-Agent":"AFTERTONE-research/0.6","Accept":"text/html"}),timeout=12) as r:
                if "text/html" not in r.headers.get("Content-Type","").lower():raise ValueError("not HTML")
                raw=r.read(4000001)
                if len(raw)>4000000:raise ValueError("body too large")
                return raw.decode("utf-8","replace")
    doc=parse_html(fetch(url))
    if len(doc["text"])<80:raise ValueError("article text too short for verification")
    return {"url":url,"title":doc["title"],"text":doc["text"],"text_sha256":hashlib.sha256(doc["text"].encode()).hexdigest(),"retrieved_at":stamp(),"status":"READ"}

def claim_candidates(text,source_id,max_items=20):
    """Extract sentences requiring fact-check; explicitly NOT verified claims."""
    candidates=[]
    for sentence in re.split(r"(?<=[。！？.!?])\s*",text):
        sentence=sentence.strip()
        if 15<=len(sentence)<=320 and re.search(r"\b(?:19|20)\d{2}\b|发行|制作|录制|采访|创作|出自|release|recorded|produced|formed",sentence,re.I):
            candidates.append({"id":"candidate-"+str(len(candidates)+1),"claim":sentence,"source_ids":[source_id],"type":"UNVERIFIED","status":"PENDING_HUMAN_CHECK"})
        if len(candidates)>=max_items:break
    return candidates

def ngrams(text,n=7):
    s=re.sub(r"\s+|[，。！？、；：,.!?;:'“”\"（）()\-\u2014]","",text).lower()
    return {s[i:i+n] for i in range(max(0,len(s)-n+1))}
def similarity_report(draft,sources,threshold=0.24):
    """Heuristic exact-character overlap against available excerpts, not plagiarism certification."""
    a=ngrams(draft)
    alerts=[]
    for src in sources:
        b=ngrams(src.get("text",src.get("excerpt","")))
        if len(b)<7:continue
        coverage=len(a&b)/max(1,min(len(a),len(b)))
        if coverage>=threshold:alerts.append({"source_id":src.get("id"),"overlap":round(coverage,3),"needs_manual_review":True})
    return {"checked_sources":len(sources),"alerts":alerts,"certifies_originality":False}

def quality_gate(claims,sources,sonic_notes,editor_approved=False):
    idx={s["id"]:s for s in sources}
    failures=[]
    for c in claims:
        if c.get("type") in ("FACT","QUOTE","REPORTED_FACT"):
            ids=c.get("source_ids",[])
            if not ids or any(i not in idx or idx[i].get("status")!="READ" for i in ids):
                failures.append("unsupported factual claim: "+str(c.get("id")))
    grounded=[n for n in sonic_notes if n.get("track") and n.get("specific_feature") and n.get("evidence_type") in ("ATTRIBUTED_REVIEW","OFFICIAL_CREDIT") and n.get("evidence_ref") in idx and idx[n["evidence_ref"]].get("status")=="READ" or n.get("track") and n.get("specific_feature") and n.get("evidence_type")=="EDITOR_LISTENING" and n.get("editor_signature") and n.get("evidence_ref")]
    if len({n["track"] for n in grounded})<3:failures.append("fewer than 3 tracks with grounded sonic detail")
    if not editor_approved:failures.append("human approval missing")
    return {"ready_for_publication":not failures,"failures":failures,"supported_tracks":len({n["track"] for n in grounded})}

def save_json(path,obj):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
