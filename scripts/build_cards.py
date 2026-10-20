#!/usr/bin/env python3
"""Generate inspectable 1080x1440 HTML editorial cards from JSON; no dependencies."""
import argparse
import html
import json
from pathlib import Path

def build(data,template):
    required=("album","kicker","date","cards")
    missing=[k for k in required if not data.get(k)]
    if missing: raise ValueError("missing "+", ".join(missing))
    cards=data["cards"]
    if not isinstance(cards,list) or not cards: raise ValueError("cards must be a nonempty list")
    outputs=[]
    for n,card in enumerate(cards,1):
        headline=str(card.get("headline","")).strip()
        body=str(card.get("body","")).strip()
        if not headline or not body: raise ValueError(f"card {n}: missing headline/body")
        if len(headline)>34: raise ValueError(f"card {n}: headline long; split manually")
        if len(body)>180: raise ValueError(f"card {n}: body over 180 chars; split card")
        out=template
        mapping={"NUMBER":f"{n:02d} / {len(cards):02d}","KICKER":data["kicker"],"HEADLINE":headline,"BODY":body,"ALBUM":data["album"],"DATE":data["date"]}
        for k,v in mapping.items():out=out.replace("{{"+k+"}}",html.escape(str(v)))
        outputs.append(out)
    return outputs

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path);p.add_argument("--output",type=Path,default=Path("output/cards"))
    a=p.parse_args()
    data=json.loads(a.input.read_text(encoding="utf-8"))
    tpl=Path(__file__).resolve().parent.parent.joinpath("templates/xhs-editorial-card.html").read_text(encoding="utf-8")
    rendered=build(data,tpl);a.output.mkdir(parents=True,exist_ok=True)
    for i,doc in enumerate(rendered,1):(a.output/f"card-{i:02d}.html").write_text(doc,encoding="utf-8")
    print(f"Generated {len(rendered)} HTML slides in {a.output}. Check layout visually; to obtain PNG, screenshot each .page at 1080x1440 using a browser/Playwright.")

if __name__=="__main__":main()
