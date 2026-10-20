"""Keyless Exa MCP search adapter via installed mcporter (Agent-Reach compatible).
Requires user-approved third-party outbound search. No credentials or cookies.
"""
import json,re,subprocess
from urllib.parse import urlsplit
from .engine import safe_url

def parse_mcporter(payload):
    if isinstance(payload,str):payload=json.loads(payload)
    blocks=payload.get("content",[]) if isinstance(payload,dict) else []
    matches=[]
    for block in blocks:
        if block.get("type")!="text":continue
        t=block.get("text","")
        # Exa returns repeated blocks beginning Title:... URL:..., often with highlights.
        heads=list(re.finditer(r"(?m)^Title:\s*(.*?)\s*\nURL:\s*(https?://\S+)",t))
        for i,m in enumerate(heads):
            url=m.group(2).strip()
            try:safe_url(url)
            except ValueError:continue
            until=heads[i+1].start() if i+1<len(heads) else len(t)
            excerpt=t[m.end():until].strip()
            matches.append({"url":url,"title":m.group(1).strip(),"snippet":excerpt[:1100],
                            "publisher":urlsplit(url).hostname,"role":"SEARCH_LEAD"})
        if not heads:
            # Not a results list: do not treat server status as a search hit.
            continue
    return list({r["url"]:r for r in matches}.values())
def search(query,results=4,runner=None):
    cmd=["mcporter","call","exa.web_search_exa","--args",
         json.dumps({"query":query,"numResults":results},ensure_ascii=False),
         "--output","json","--timeout","20000"]
    if runner is None:
        def runner(cmd):
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=28,check=False)
            if p.returncode!=0:raise RuntimeError("Exa CLI error: "+p.stderr[:200])
            return p.stdout
    return parse_mcporter(runner(cmd))
