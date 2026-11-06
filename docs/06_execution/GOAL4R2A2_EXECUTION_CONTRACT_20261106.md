# Goal 4R2-A2 execution contract

6 November 2026, Bangkok. **OWNER_APPROVED; ACTIVE.**

Base main: `19979f12bb5a07cabf4624cd8a2940e663953614`.
The owner approved [source-and-benchmark readiness](GOAL4R2A_EXPANSION_PROPOSAL_20261106.md).
This contract makes that bounded metadata-only scope executable.

## Window, ownership and resources

- Start 2026-11-06 01:05:41 UTC / 08:05:41 Bangkok.
- Deadline 2026-11-06 13:05:41 UTC / 20:05:41 Bangkok.
- Maximum 14,400 cumulative CPU-seconds, two CPU workers, no GPU/new paid service.
- Processing and validation on dr-train; local code/docs/source preparation and
  complete return verification permitted. Parent sole writer, specialists read-only.
- Fresh roots: `/home/chaw/curaloop-rl/goal4r2a2-20261106-v1` and its `-return`
  sibling. Never recreate prior closed roots; inspect live access/resources first.
- Reserve 1,800 CPU-seconds for preparation/retrieval/transport/local checks,
  1,200 for preservation/verification and 600 for administration/startup.
  Remote launches durably reserve 120 CPU-seconds each, maximum six launches,
  initially serialized. Retain unresolved reservations; no hidden retries.
- Workers have one CPU, 120 CPU-seconds, 600 wall-seconds and bounded memory;
  the absolute owner deadline takes precedence. Conservative reserves are not
  exact exhaustive host CPU accounting.

## Fixed inputs and permissible retrieval

The frozen 4R2-A SI audit defines 105 AIDs and published version/revision/date
tuples; all sixty source stage pairs remain fixed. Use bounded PubChem assay
**description metadata only**, through the existing pubchem-pug-skill script.
No full assay records, CSV/concise results, dose-response rows or compound queries.
Do not assume a description selector honours a requested historical version.
Record actual response identity, optional version fields and date semantics.

First issue one description probe. If access is denied, do not repeat it across
the roster; preserve the error and continue independent readiness work. If it
succeeds, at most 104 additional current-description requests complete the roster.
At most two additional description-only historical-selector controls may be
proposed within the fixed request plan. A control must not fall back to a full
record. HTTP 200 alone cannot establish selector support. No automatic retries
on denial or rate limits; incomplete access remains explicit.

Inspect pinned MolDesignBench paper, code/card/licence, file metadata and tool/
evaluation schemas. Do not read the JSONL tasks/questions, reference answers,
feasibility labels or reference SMILES. Card/code examples already inspected
are exposure, not a source of fresh evaluation cases. Log an external metadata
tool's internal preview attempt if it occurs; do not treat an absence of returned
rows as proof that its service performed no internal row access.

The code MIT licence and dataset CC BY-NC 4.0 card are distinct. Commercial
dataset use is NOT_CLEARED; additional creation-model terms remain a rights gate.
No payment, provider contact or dataset relicensing is authorized.

## Deliverables and validation

1. Versioned description/source/provider/endpoint register, including failures,
   absent/null/zero distinctions, S19 comparison and historical reconstruction limits.
2. A justified observation/population protocol or explicit scientific NO_GO.
   Metadata cannot certify per-compound confirmation coverage or family independence.
3. MolDesignBench compatibility, pinned provenance/licence, native metric audit,
   dependency/provider requirements and a prospective exposure/split report.
4. English evidence report, reviewed code/schema checks, full preservation and main delivery.

Ten metadata/schema validation cases are frozen before implementation in
`research/configs/goal4r2a2_cases_v1.json`. Synthetic contract examples are not
benchmark rows or scientific trials. Preserve the existing offline package and
all previous frozen scientific source/results without migration.

## Stop conditions and closure

No scientific pilot, live agent/provider/MCP evaluation, team write, bulk activity
or benchmark task/gold intake is included. A concrete heldout roster remains
NOT_FROZEN until an authorized index and example/group exclusions can be checked.
Public benchmark data do not establish absence from model pretraining.

Complete readiness may be NO_GO or conditional; do not force a cohort or change
the intended twelve-group ambition silently. Ask before material source,
population, rights or experimental changes. Retain all raw/cache/source/test
versions, return and reread every owned task file before exact task/export
deletion, obtain fresh absence, and verify normal main publication separately.
