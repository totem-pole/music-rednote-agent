# AFTERTONE V0.5 | Research execution

Requires Python 3.11+, no pip dependencies.

```bash
python -m aftertone.engine plan --artist '陈淑桦' --album '一生守候' --folder local/chen
python -m aftertone.engine discover --mode metadata --folder local/chen
python -m aftertone.engine audit --folder local/chen
python -m unittest discover -s tests -v
```

To run broader legal web discovery, set BRAVE_SEARCH_API_KEY locally (NEVER GitHub) and use `discover --mode brave --max-tasks 40`. Brave API may incur charges and require a subscription. Metadata mode uses public Wikipedia and MusicBrainz search endpoints only. Respect quotas; do not aggressively scrape. Search results are marked DISCOVERED_NOT_READ and are **not** proof that a full page or its claims has been verified. For genuine evidence, read permitted pages, preserve excerpts, attach claims with source IDs and mark sources READ only after reviewing them. RYM login restrictions must not be bypassed. In CI only deterministic mock tests run; production networking must be tested in the user's permitted environment.

There is no automatic editorial approval or Xiaohongshu publishing in v0.5. Original cover image rights and explicit per-post human approval remain necessary. Avoid putting private source text, credentials or cookies in git. The base URL guard is not a full SSRF sandbox; use only specified provider endpoints in a controlled runtime.
