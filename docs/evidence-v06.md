# Evidence pipeline v0.6 — TEXT ONLY

Source discovery remains in `aftertone.engine`. The new `aftertone.evidence` module provides:
- Explicit approved-host HTML retrieval, with no redirects, credentials or automatic robots evasion.
- Content cleanup and SHA256 text fingerprint.
- **Unverified** sentence candidate extraction for human fact review.
- Heuristic text-overlap alerts (not a copyright or plagiarism guarantee).
- Publication quality gate requiring source-backed factual claims, three grounded musical tracks and explicit editorial approval.

`python -m aftertone.pipeline --folder local/album` creates `editorial-audit.json` from existing `sources.json`, optional `pages/<source-id>.txt`, `claims.json`, `sonic-notes.json`, and `review.md`. It **never publishes**. It does not call a language model or hallucinate reviewed facts. Current article extraction is basic HTML, not a high-precision paywall/parser integration.

No cover images or visual cards are required or produced. All paths should remain local or in private authorized storage. Before using `retrieve_article`, check each host's applicable access terms and robots restrictions. Allowlisted domain checks are not sufficient for running untrusted URLs in a high-security environment; execute network retrieval in an isolated runtime and inspect DNS/redirect policy.

A real LLM-supported Music Critic must consume the evidence ledger, present music interpretation separately from source-derived facts, and require editor listening notes for first-person judgments.
