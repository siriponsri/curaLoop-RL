# LR-BC R1: unchanged-cohort observation qualification

**FROZEN PLAN; NOT_RELEASED_OR_STARTED.** 6 November 2026.

R1 is delegated by the owner's LR-BC approval. The protocol reviewer found that
this unchanged-population qualification is within that authority. Runtime/source
release still requires a separately recorded reviewed implementation and start.
No molecular pilot or C release follows from this document alone.

## Identity, population and estimand

Retain all five A3 pairs, original source-defined readouts, transformations and
the 589 exact structure-cleared SIDs in their frozen order. Reuse the original
qualification manifest SHA256
`afca38be68334b60c2657099f316e839acb4a06c41264eedd68fe021c8ae7146`
and structure release
`fb5f8940c239be7ade7517f982cae4decf4795294405ebe63b5a32c9b37513a4`.
No replacement, new sample, replicate selection, aggregation change, missing-value
floor, new threshold or change to protected structures is permitted.

The estimand is coverage and observation-state attrition in the fixed common-listed,
structure-cleared **development-exposed** population, including complete paired
tuples. This is not full-library performance, independent-family validation,
historical-row reconstruction, clinical benefit or policy-value evaluation.
The five pairs occupy one conservative exposed component. Internal noncommercial
qualification is supported by the retained source review; publication,
redistribution and commercial data use remain NOT_CLEARED.

Preserve AID2097's original NO_GO and STOP. R0 found TID3 present in all16 old
canary rows and TID4 absent in all16; zero complete selected tuples. Native-envelope
support fixes transport representation only. It does not change endpoint eligibility.

## Frozen intake and stops

Serialize all source intake on one admitted dr-train worker. Freeze all20 exact
requests before the first new response: first16 cleared SIDs per AID for ten
canary requests, then the complete fixed lists for ten qualification requests.
All five pairs remain in the roster, including failed/zero-coverage endpoints.
Full qualification needs all canary source/identity/row-coverage/qualifier gates;
it does not select a subset based on numeric activities or cell availability.
Missing TIDs remain missing states and do not become complete measurements.

Use the unchanged pinned PubChem skill client, bounded exact GET allowlist,
no redirects, at most30-second request timeout, at least1.1seconds between calls,
**1MiB decoded bytes per response** and at most20MiB new reserved decoded bytes.
The lower response limit is within the approved16MiB maximum. Inherit24/96 PUG,
27/32 UniProt,28,715,980/268,435,456 bytes. Reserve all20 calls and20MiB durably
before launch; retain unused/failed reservations. No other source calls are
released by R1. Do not reset or edit the old stopped ledger.

The new reviewed phase explicitly references the old envelope failure and ledger
SHA256 `dee45c033a03d4e7d800f5403f2b8ea6bfe11eb4b380aa0f0a86f5b821eab906`.
A new denial, malformed response, unexpected/protected ID, version/readout drift,
ambiguous qualifier, incomplete canary row coverage or quota exhaustion stops
this phase. No retry or fallback. Interpret every returned SID before reading any
readout value. Raw values, outcomes, identifiers and parser messages stay private.
Report safe counts and source hashes only.

Canary/full responses are repeated retrievals, not independent measurements or
new replicates. Coverage uses the full phase once. A full phase is not launched
after an intake stop. Partial work and original failures remain evidence.

## Execution and release

At most6 CPU-hours for R1; initially900CPU-second retained reservations per job,
890-second whole-process guard and1800-second wall limit. Maxfour combined workers,
one CPU/4GiB/nice19/single numerical threads per remote worker. Record R1 start,
deadline=min(start+12hours,B absolute deadline) before admission. A fixture-only
job must verify envelope/type/identifier/qualifier/stop/duplicate accounting and
private-error boundaries before live intake. Preserve all tested source bytes.

Molecular fitting remains NOT_RELEASED. Any scientifically material endpoint,
aggregation, phenotype or population amendment returns to the owner with options.
Return/reread every owned remote file before exact scoped cleanup.
