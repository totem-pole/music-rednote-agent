"""Text-only research report assembler; no automated posting."""
import argparse,json
from pathlib import Path
from .evidence import claim_candidates,similarity_report,quality_gate,save_json

def assemble(folder):
    folder=Path(folder)
    sources=json.loads((folder/"sources.json").read_text(encoding="utf-8"))
    claims=json.loads((folder/"claims.json").read_text(encoding="utf-8")) if (folder/"claims.json").exists() else []
    sonic=json.loads((folder/"sonic-notes.json").read_text(encoding="utf-8")) if (folder/"sonic-notes.json").exists() else []
    manuscript=(folder/"review.md").read_text(encoding="utf-8") if (folder/"review.md").exists() else ""
    extracted=[]
    for src in sources:
        content_path=folder/"pages"/(src["id"]+".txt")
        if src.get("status")=="READ" and content_path.exists():
            text=content_path.read_text(encoding="utf-8")
            extracted.extend(claim_candidates(text,src["id"]))
            src["text"]=text[:20000]
    report={"source_count":len(sources),"read_count":sum(x.get("status")=="READ" for x in sources),
            "candidate_claims":extracted,"originality":similarity_report(manuscript,sources),
            "quality":quality_gate(claims,sources,sonic,False),
            "publishing_enabled":False}
    save_json(folder/"editorial-audit.json",report)
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--folder",type=Path,required=True)
    a=p.parse_args();r=assemble(a.folder)
    print(json.dumps({k:v for k,v in r.items() if k!="candidate_claims"},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
