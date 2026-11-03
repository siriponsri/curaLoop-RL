"""Reconcile every displayed metric from the immutable public event ledger."""

from dataclasses import asdict

from .domain import Event


def curve_from_events(events: tuple[Event, ...], budget_units: int) -> list[dict]:
    spent = hits = delivered = missing = seed_hits = 0
    pending: dict[str, int] = {}
    seen_ids: set[str] = set()
    completed: set[str] = set()
    rows = []
    for index, e in enumerate(events):
        if e.event_type == "INITIAL_LABEL":
            seed_hits += int(e.delivered_active is True)
        elif e.event_type == "REQUEST_ACCEPTED":
            if e.request_id in pending or e.request_id in completed or e.compound_id in seen_ids:
                raise ValueError("Duplicate accepted experiment in ledger.")
            if e.cost_units <= 0 or not e.request_id or not e.compound_id:
                raise ValueError("Malformed accepted experiment in ledger.")
            pending[e.request_id] = e.cost_units
            seen_ids.add(e.compound_id)
        elif e.event_type in ("RESULT_DELIVERED", "RESULT_MISSING"):
            if e.request_id not in pending or e.cost_units != pending[e.request_id]:
                raise ValueError("Unmatched or duplicate outcome in ledger.")
            spent += pending.pop(e.request_id)
            completed.add(e.request_id)
            if e.event_type == "RESULT_DELIVERED":
                if type(e.delivered_active) is not bool:
                    raise ValueError("Delivered result requires a Boolean label.")
                delivered += 1
                hits += int(e.delivered_active)
            else:
                missing += 1
        reserved = sum(pending.values())
        remaining = budget_units - spent - reserved
        if remaining < 0:
            raise ValueError("Ledger exceeds configured budget.")
        rows.append({
            "event_index": index, "step": e.step, "spent_units": spent,
            "reserved_units": reserved, "remaining_units": remaining,
            "confirmed_hits": hits, "delivered_assays": delivered,
            "missing_assays": missing, "pending_assays": len(pending), "seed_hits": seed_hits,
        })
    return rows


def metrics_from_events(events: tuple[Event, ...], budget: int, assay_cost: int) -> dict:
    rows = curve_from_events(events, budget)
    last = rows[-1] if rows else {
        "spent_units": 0, "reserved_units": 0, "remaining_units": budget,
        "confirmed_hits": 0, "delivered_assays": 0, "missing_assays": 0,
        "pending_assays": 0, "seed_hits": 0, "step": 0,
    }
    previous_spent = previous_hits = area = 0
    for row in rows:
        area += (row["spent_units"] - previous_spent) * previous_hits
        previous_spent, previous_hits = row["spent_units"], row["confirmed_hits"]
    area += (budget - previous_spent) * previous_hits
    denominator = budget * (budget // assay_cost)
    controller_events = [e for e in events if e.event_type == "REQUEST_ACCEPTED" and (
        e.explanation.startswith("q_learning:") or e.explanation.startswith("contextual_bandit:"))]
    fallback_count = sum("UNSEEN_STATE_GREEDY_FALLBACK" in e.explanation for e in controller_events)
    return {**{k: v for k, v in last.items() if k != "event_index"},
            "controller_requests": len(controller_events),
            "controller_fallback_requests": fallback_count,
            "hit_rate": last["confirmed_hits"] / last["delivered_assays"] if last["delivered_assays"] else None,
            "auc_discovery_budget": area,
            "auc_discovery_budget_normalized": area / denominator if denominator else 0.0,
            "auc_definition": "Left-step integral to configured budget; normalized by budget * floor(budget/assay_cost).",
            "initial_seed_budget_rule": "PREEXISTING_SUNK_COST"}


def event_rows(events: tuple[Event, ...]) -> list[dict]:
    return [asdict(e) for e in events]
