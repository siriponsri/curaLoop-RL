# Goal 4R2-A execution contract

6 November 2026, Bangkok. **OWNER_APPROVED; FEASIBILITY COMPLETE.**
See the [closeout](GOAL4R2A_CLOSEOUT_20261106.md); scientific advancement is NO_GO.

Base main: `1ba48632540c6e8b38bea93ac6a16e23b65d924e`.
The owner approved the [feasibility proposal](POST_4R1_DIRECTION_PROPOSAL_20261106.md)
and invited immediate dataset/benchmark expansion proposals when justified.
Expansion execution remains a separate decision.

## Window, resources and ownership

- Start: 2026-11-05 23:57:53 UTC / 6 November 06:57:53 Bangkok.
- Deadline: 2026-11-06 11:57:53 UTC / 18:57:53 Bangkok.
- Maximum 14,400 cumulative CPU-seconds and two CPU workers, no GPU or paid service.
- Processing and engineering acceptance tests run on dr-train. Local code/docs
  preparation, source retrieval and complete return verification are permitted.
- Fresh roots only: `/home/chaw/curaloop-rl/goal4r2a-20261106-v1` and its
  `-return` sibling. Inspect live access/allocation before creating either.
- Parent is sole writer. Read-only specialists review data, method and architecture.

Budget reservations: 1,800 CPU-seconds for preparation/retrieval/transport/local
checks, 1,200 for preservation/local verification, and 600 for administration.
Remote worker launches reserve their whole CPU ceilings durably before launch;
maximum remote reservations 10,800 seconds, maximum two workers (initially one).
Do not release an unresolved reservation. Retain launch failures and actual
receipts. Conservative charges and known measured CPU are reported separately;
exhaustive host CPU is not claimed. No dependency installation is planned:
the prototype and its unittest runner use Python standard-library facilities.
An owner-supplied PDF arrived during the goal. Read-only source identification
may copy the existing bundled pypdf 6.10.0 source and licence into the owned
private task tree, without installing packages on the host. This separate
bounded metadata worker is charged like the fixture worker; PDF text/reader
sources remain ignored locally and are not scientific campaign inputs.

## Deliverables and fixed scope

1. A source-backed novelty/next-question decision, including NO_GO if warranted.
2. Metadata/code-only candidate-data feasibility register: source/version/rights,
   endpoints, measured/default/missing semantics, follow-up selection and exposure
   restrictions; report actual eligible counts, including unknown or zero cleared.
3. Runnable offline evidence-to-plan-to-report tools and exactly twelve frozen
   engineering workflow cases. Synthetic fixtures are explicitly labeled and
   never presented as molecular results. Unit/robustness checks may supplement
   these cases without expanding scientific trials.
4. An inspectable next-study specification with observation/endpoint contracts,
   controls, exposure rules, identification limitations and budget unknowns.

The twelve cases are frozen in `research/configs/goal4r2a_cases_v1.json` before
implementation: six ordinary workflows and six failure/recovery cases. They do
not measure live-source, LLM, MCP, scientific discovery or customer performance.
Report engine/source/case identities and all attempts. Demonstrate local preview
only, idempotency and interrupted-state recovery without a real team write.

No scientific campaign, model training, bulk activity-table download, new final
outcome access, assay-data expansion execution, live-provider evaluation, MCP
client integration, paid API, customer contact or journal action is included.
An inactive/missing/default row cannot be silently promoted to a measured oracle.
Do not evaluate activity rows to select candidate datasets or count families.

## Acceptance and closure

Engineering cases must meet their declared expected behaviors, with errors and
proper stops retained. Data/method feasibility may conclude NO_GO. A completed
feasibility goal does not pass Goal4 or authorize 4R2-B/P1/Goal5.

Freeze tested bytes and report the Python environment, receipts, logs and output
hashes. Preserve task-owned temporary artifacts beneath the new remote root.
Snapshot all task files, return archive/manifest, verify every member and reread
all restored local bytes before scoped task/export deletion. Obtain fresh
read-only absence evidence. Keep raw originals locally; public evidence is a
bounded aggregate/metadata copy. Reconcile docs and normal main push separately.
