# End-to-end acceptance report — 2026-10-20

Scope: exclude WorkBuddy loading and Xiaohongshu draft interface; text-only workflow.

## Reproducibility
- GitHub Actions live run: https://github.com/totem-pole/music-rednote-agent/actions/runs/39413202994 — SUCCESS.
- CI unit tests: see actions Unit Tests, latest workflow success.
- Source sweep: 32 actual HTTP requests (16 each). This is not 32 diverse keyword web-search queries; it is a URL source sweep, so the full R0–R7 query protocol is **NOT PASSED**.
- Chen: 7/16 text-length-qualified pages, 6 different hostnames. Say Sue Me: 12/16, 10 hostnames. Several 'READ' texts are generic entry pages, so semantic quality remains **NOT PASSED**.
- Metadata services in preceding live run: 6/6 HTTP 200 Wikipedia/MusicBrainz/iTunes requests.
- RYM 403 both albums; Discogs 403 for Chen. Do not claim RYM review access.
- Text-only drafts exist in examples/e2e-chen-review.md and examples/e2e-say-sue-me-review.md, created by an assistant from selected evidence BEFORE the live sweep, not autonomously LLM-generated from persisted research results.
- Source-evidence mapping only preliminary; source excerpts in HTML sweep not full documents. Automated atomic claim extraction is heuristic and marked UNVERIFIED.
- No firsthand music listening; no sonic interpretation certification.
- Similarity is a lexical screening, not plagiarism certification; automated live check has only a short excerpt per source, not full copyright corpus.
- Editorial live gate: BOTH drafts correctly NOT PUBLISHABLE, lack direct listening and human approval.

## Acceptance matrix
| Requirement | Verdict |
| --- | --- |
| Production network connectivity and per-source error recording | PASS (live) |
| Wikipedia/MusicBrainz/iTunes metadata queries | PASS (6 HTTP 200), relevance/version correctness not fully verified |
| 32 requests, multiple domains | PASS (actual requests); NOT equivalent to eight semantic-search rounds |
| 8-round adaptive search (32–64 real query executions) | FAIL / NOT IMPLEMENTED |
| Robust authoritative fact extraction with quoted spans | FAIL / INCOMPLETE |
| Cross-check album edition and independently sourced claims | FAIL / INCOMPLETE |
| RYM/Discogs/Douban review coverage | FAIL / limited access |
| Three-track firsthand sonic analysis for each album | FAIL / editor listening absent |
| Autonomous LLM research synthesis and text composition | FAIL / provider not integrated |
| Full-source originality audit | FAIL / only heuristic excerpt-level analysis |
| Draft and fail-closed quality gate | PASS; both rejected, not ready to publish |
| WorkBuddy and Xiaohongshu integration | OUT OF SCOPE by instruction |

## No false completion
GitHub workflow success reflects script execution, NOT editorial acceptance. A full green functional acceptance requires both albums to pass source coverage, claim provenance, sonic evidence, independent criticism, originality review and an appropriately audited autonomous LLM draft. Do not publish either draft yet.

## Source examples
- Damnably official: https://www.damnably.com/release/where-we-were-together/
- Bandcamp Daily primary interview: https://daily.bandcamp.com/features/say-sue-me-where-we-were-together-interview
- KEXP 2018 interview: https://kexp.org/read/2018/4/3/say-sue-me-pens-heartfelt-expansive-epic-coming-end-kexp-premiere/
- Pitchfork: https://pitchfork.com/reviews/albums/say-sue-me-where-we-were-together/
- Wikipedia (secondary discovery): https://zh.wikipedia.org/wiki/一生守候
