"""Final live integration artifact: evaluated against real source-read outcomes.
No automatic LLM prose generation, listening simulation, or publisher side effects.
"""
import json,pathlib
from aftertone.evidence import similarity_report,quality_gate
P=pathlib.Path("artifacts/integration")
DRAFTS={"chen":"examples/e2e-chen-review.md","say-sue-me":"examples/e2e-say-sue-me-review.md"}
def main():
 articles=json.loads((P/"articles.json").read_text(encoding="utf-8"))
 output={}
 for slug,rs in articles.items():
  source_rows=[]
  for i,r in enumerate(rs):
   source_rows.append({"id":slug+"-"+str(i),"url":r["url"],"status":r["status"],
                       "text":r.get("excerpt",""),"publisher":r["publisher"]})
  draft=pathlib.Path(DRAFTS[slug]).read_text(encoding="utf-8")
  similarity=similarity_report(draft,source_rows)
  # The draft has not been manually listened to or signed off; fail closed.
  gate=quality_gate([],source_rows,[],editor_approved=False)
  output[slug]={"sources_attempted":len(source_rows),"sources_read":sum(s["status"]=="READ" for s in source_rows),
                "draft_chars":len(draft),"source_similarity":similarity,"quality_gate":gate,
                "end_to_end_verified":False,"editorial_stage":"DRAFT_AWAITING_LISTENING_SOURCE_REVIEW"}
  print(slug,"read",output[slug]["sources_read"],"draft",len(draft),"publishable",gate["ready_for_publication"],flush=True)
  assert not gate["ready_for_publication"],"must fail closed without listening and approval"
 (P/"editorial-e2e.json").write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding="utf-8")
if __name__=="__main__":main()
