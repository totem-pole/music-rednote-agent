# AFTERTONE E2E Acceptance — 2026-10-20 (v0.8)

User scope: automated editorial research, verified evidence and **text-only** review; exclude WorkBuddy and Xiaohongshu publishing.

## Verified on real GitHub Actions runners
- Exa MCP smoke probe succeeded: https://github.com/totem-pole/music-rednote-agent/actions/runs/39448103036 (real result: Pitchfork Say Sue Me 2018 album review).
- Full Exa sweep succeeded: https://github.com/totem-pole/music-rednote-agent/actions/runs/39448375669.
- 36 actual queries per album, 72 total, all eight research rounds attempted. Positive result counts vary by round.
- Artist+album relevance filtering: Chen 40 distinct candidate leads, Say Sue Me 60 (links are leads, not automatically verified facts).
- Reusing these same results, fixed safe redirect/readability acceptance: https://github.com/totem-pole/music-rednote-agent/actions/runs/39449671459.
- After rejecting pages shorter than 500 characters, Chen **6** read pages from Apple Music / Wikipedia / Douban; Say Sue Me **10** read pages including Damnably, KEXP, Pitchfork, Apple Music and encyclopedia. Different URLs on the same operator are NOT independent evidence.
- RYM remains inaccessible (403) from GitHub runners; do not imply its reviews were retrieved.
- Tests include real Exa output parser shape, disallow fake server success, structured quote exact location, untrusted source restriction, source overlap alerts, quality gate and LLM HTTP mock transport. Unit CI succeeded on the latest commits.

## Technical components present
- aftertone/exa.py: verified Exa MCP search.
- aftertone/full_research.py: eight-round queries + per-query status, relevance filter.
- aftertone/capture.py: approved host full-text extraction, text-hash deduplication, short-text rejection and provenance file output.
- aftertone/provenance.py: exact quote offsets, independent provenance chain checks.
- aftertone/fact_model.py: model-assisted atomic claim proposal with exact quote rejection checks.
- aftertone/writer.py: guarded external model caller for Chinese **text-only** title/body/tags; no publication.
- aftertone/evidence.py: textual overlap heuristic and music track quality gate.

## Editorial gates NOT YET PASSED (do not falsely claim completion)
1. **LLM live call not tested**: No configured LLM_API_KEY/LLM_MODEL was available through these runs. Mock transport passed. User must provision one supported model provider as a GitHub Actions secret or run locally with environment variables; never commit keys.
2. **Claim factual truth not fully verified**: exact source quote presence is necessary but insufficient. Semantic interpretation and documentary independent origin must be checked. The model is not allowed to promote its own unsupported claims.
3. **Three-track independent sonic analysis not verified**: sources contain critic observations, but no editor-signed direct listening notes. Attributed observations are acceptable as attributed analysis; first-person direct listening must not be fabricated.
4. **Originality**: lexical overlap and partial excerpts can flag risks, but cannot prove that a text is fully original or legally cleared.
5. **Final autonomous model-generated drafts not accepted**: Existing sample reviews are manually seeded examples, not CI-generated complete verified prose. Both remain unapproved.

## True status
Transport/executable multi-round retrieval: **PASS**.
Accessible source selection and evidence capture: **PASS with partial source coverage**.
Automated semantic fact verification, independent music analysis, model composition, final editorial approval: **NOT PASSED**, with dependencies clearly identified.
No WorkBuddy or Xiaohongshu integrations were tested (out of scope).

## Commands
```bash
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp --scope project
python -m aftertone.full_research --mode exa --output artifacts/eight-round
python -m aftertone.capture --root artifacts/eight-round --limit 20
python -m unittest discover -s tests -v
# After verified claims and editor listening notes exist, configure LLM_API_KEY and LLM_MODEL:
python -m aftertone.fact_model --folder artifacts/eight-round/chen
python -m aftertone.writer --folder artifacts/eight-round/chen
```

**Ethics/privacy**: do not upload private essays, passwords, cookies, proprietary audio, or unlicensed cover art. No unattended publishing; generated drafts require explicit editorial approval.
