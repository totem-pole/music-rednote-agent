# Research Engine v0.4 (prototype)

`research_engine.py` is a reproducible **offline** query planner, HTML-text extractor and fact-conflict reporter. It **does not** make web search calls or scrape locked sites. This avoids implying a tool integration that is not yet built.

## Commands
```bash
python scripts/research_engine.py plan --artist "陈淑桦" --album "一生守候" --output local/chen-plan.json
python scripts/research_engine.py plan --artist "Say Sue Me" --album "Where We Were Together" --output local/say-plan.json
python scripts/research_engine.py extract --input local/captured-public-page.html
python scripts/research_engine.py conflicts --input local/claims.json
PYTHONPATH=scripts python -m unittest discover -s tests -p 'test_*.py' -v
```
Plan entries begin with NOT_RUN. A search-capable runtime (e.g. WorkBuddy with approved tools) must run each query, record real source URLs, follow originals, and write claims. Queries are seed tasks, not proof of search completion. The planned 26 queries are a baseline; the source-discovery SOP permits expansion to 32–64 when gaps demand it.

### Security
Do not load untrusted URLs via local URL fetchers. Never provide site credentials, Cookie files or other secrets to the repository. Direct HTML extraction is only for HTML deliberately acquired through permitted access. Verification requires multiple independent provenance chains. No unattended Xiaohongshu publishing.

### Next integration
Define a `SearchProvider.search(query)` interface for a real authorized research tool; persist per-query SUCCESS/BLOCKED/NOT_FOUND results; add exact quotation provenance and domain-specific parsers for MusicBrainz, Discogs, RYM and authorized press sources. Human close listening remains mandatory for sonic assertions.
