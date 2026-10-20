# AFTERTONE — Music Rednote Agent

Private, editor-led AI research and music criticism workflow for a Xiaohongshu account. **Status: v0.1 scaffold; no automated publishing configured or tested.**

## Editorial purpose
Each day the human editor selects one domestic and one international record. An AI assistant researches the release, artist career, historical context, recording process, sonic features and diverse critical reception; it creates a traceable evidence ledger, drafts an original editorial note in an established personal style and requests human approval.

## How to start
1. Open `SKILL.md` with a Skills-capable assistant (including WorkBuddy only if this Skill format is supported by the installed version).
2. Provide artist, exact album/edition, your listening notes and suggested cultural angles.
3. Follow `skills/music-critic/SKILL.md`, `references/source-policy.md`, `references/editorial-voice.md`.
4. Create an album package with the structure specified in `SKILL.md`; run `python scripts/validate_package.py path/to/album-folder`.
5. Review research, claims, copy, originality and album-cover rights yourself. Publishing is deliberately disabled in this version.

## Source inspiration (not bundled)
- [Agent-Reach](https://github.com/Panniantong/Agent-Reach): channel healthcheck and backend routing ideas, not music interpretation.
- [xhs-album-review-skill](https://github.com/1183498834/xhs-album-review-skill): per-album working directory and human-reviewed drafting patterns.

This repository does not vendor either upstream project; audit upstream licensing, terms and security before porting code.

## Roadmap
- v0.1 Research + personal voice + QA scaffold (current).
- v0.2 Source connector interface, provider probes and robust report generation.
- v0.3 Integration tests on 陈淑桦《一生守候》 and Say Sue Me《Where We Were Together》.
- v0.4 Optional WorkBuddy/Xiaohongshu draft connector after supported APIs, credentials and terms are reviewed.
- Future: analytics and a public album archive if the initial month succeeds.

No unattended login, credential collection or posting. Copyright clearance is required for album cover uploads.
