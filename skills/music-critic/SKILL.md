---
name: music-critic
description: Evidence-driven album research and criticism across primary sources, music magazines and listener communities.
---
# Music Critic

Before research, read `skills/music-critic/source-discovery.md` and execute its eight round search protocol. Save audit records and do not treat RYM or Wikipedia as verified facts on their own.\n\n## Goal
Create an original, defensible interpretation of an album's sounds and social/cultural place. Do NOT equate the number of search hits with research quality.

## Passes
1. **Identity & versions**: artist, title, year, regional editions, credits, label, producers, recording locations, tracklist. Distinguish primary release from reissues.
2. **Primary history**: album liners, label website, artist interviews, archived announcements. Construct a dated career and production timeline. Separate self-report from established fact.
3. **Music and form**: assess representative songs, instrumentation, melody/harmony/rhythm, arrangement, lyrical themes, sequence and production. Without access to actual audio or user listening notes, report secondhand descriptions as attributed sources; do not simulate close-listening or timestamped details.
4. **Historical context**: location, industry, social change, relevant film/literary connections. No unsupported claim of causal influence.
5. **Critical reception**: probe magazines and journalism (e.g. Pitchfork, The Quietus, Bandcamp Daily, Stereogum, AllMusic, Uncut, Mojo, local music journals), archive sources, Chinese music press, verified Weibo reporting, RYM, Douban and appropriate genre forums. Record accessible, blocked, absent and contradictory findings.
6. **Synthesis**: identify at least two distinct, defensible angles and a potential weakness, not a generic glorification. Attribute critical opinions rather than passing them off as one's own listening.
7. **Evidence quality**: prioritize primary sources for factual claims; criticism for reception and interpretations; community reaction is non-representative anecdotal evidence.

## Channel abstraction adapted from Agent-Reach
Research tool layer must expose `search(query)`, `read(url)`, `healthcheck(channel)` and error category (`UNAVAILABLE`, `LOGIN_REQUIRED`, `RATE_LIMITED`, `NOT_FOUND`, `SUCCESS`). Respect authenticated session boundaries, robots/terms and licensing. A fallback is an alternate permitted data source, NOT evasion of an access restriction. RYM/Weibo may legitimately be unavailable; log and move on.

## Review gates
- No uncited significant factual assertions in the ledger.
- Do not merge two album versions or confuse artist/album titles.
- Conflicting facts visibly marked.
- At least one negative, limited, or uncertain assessment considered.
- Provide a clear evidence vs interpretation separation.
- Never describe inaccessible sources as read.
- Do not present generic LLM prose as firsthand listening.

## Output
Write structured sources.json, claim-ledger.json and research.md before composing review.md.
