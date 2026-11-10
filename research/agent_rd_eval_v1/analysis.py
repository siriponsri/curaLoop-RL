"""Prespecified aggregations. Missing units never disappear from denominators."""

import random
import statistics

ORDER = ("B0", "B1", "B2", "P", "A-NOREPAIR")


def rate(numerator, denominator):
    return numerator / denominator if denominator else None


def summarize(plan, results, cards):
    by_id = {row["unit"]["unit_id"]: row for row in results}
    assert len(by_id) == len(results)
    assert set(by_id).issubset({u["unit_id"] for u in plan})
    families = {card["case_id"]: card["family"] for card in cards}
    systems = []
    family_rows = []
    for system in ORDER:
        units = [u for u in plan if u["system"] == system]
        available = [by_id[u["unit_id"]] for u in units if u["unit_id"] in by_id]
        scores = [r["score"] for r in available]
        successes = sum(s["success"] for s in scores)
        raw_n = sum(s["raw_numeric"]["claims"] for s in scores)
        raw_error = sum(s["raw_numeric"]["unsupported"] + s["raw_numeric"]["wrong"] for s in scores)
        released_n = sum(s["numeric"]["claims"] for s in scores)
        released_error = sum(s["numeric"]["unsupported"] + s["numeric"]["wrong"] for s in scores)
        costs = [s["cost"] for s in scores]
        boundary_units = [r for r in available if families[r["unit"]["case_id"]] in ("boundary", "source_fault")]
        answer_units = [r for r in available if families[r["unit"]["case_id"]] not in ("boundary", "source_fault")]
        citations = sum(s["citation_present"] for s in scores)
        correct_citations = sum(s["citation_correct"] for s in scores)
        fallback = sum(s["fallback"] == "DETERMINISTIC_ABSTENTION_AFTER_CAP" for s in scores)
        systems.append({"system": system, "planned": len(units), "attempted": len(available), "not_run": len(units) - len(available),
                        "successes": successes, "success_rate_all_planned": rate(successes, len(units)),
                        "success_rate_attempted": rate(successes, len(available)),
                        "execution_failed": sum(s["execution_failed"] for s in scores), "deterministic_abstention_fallbacks": fallback,
                        "appropriate_abstentions": sum(r["score"]["appropriate_abstention"] for r in boundary_units),
                        "abstention_expected_attempted": len(boundary_units), "overrefusals": sum(r["score"]["overrefusal"] for r in answer_units),
                        "answer_expected_attempted": len(answer_units), "raw_numeric_claims": raw_n, "raw_numeric_errors": raw_error,
                        "raw_numeric_error_rate": rate(raw_error, raw_n), "released_numeric_claims": released_n,
                        "released_numeric_errors": released_error, "released_numeric_error_rate": rate(released_error, released_n),
                        "citations_present": citations, "citations_correct": correct_citations, "citation_precision": rate(correct_citations, citations),
                        "model_calls": sum(c["model_calls"] for c in costs), "failed_model_calls_unknown_cost": sum(c["failed_calls"] for c in costs),
                        "known_model_cpu_seconds": sum(c["model_cpu_seconds"] for c in costs),
                        "recorded_model_tokens": sum(c["model_tokens"] for c in costs), "model_wall_seconds": sum(c["model_wall_seconds"] for c in costs),
                        "known_controller_cpu_seconds": sum(r.get("controller_cpu_seconds", 0) for r in available),
                        "median_unit_wall_seconds": statistics.median(r["unit_wall_seconds"] for r in available) if available else None,
                        "median_model_cpu_seconds": statistics.median(c["model_cpu_seconds"] for c in costs) if costs and system != "B0" else None,
                        "paid_api_cost_usd": sum(c["paid_cost_usd"] for c in costs)})
        for family in dict.fromkeys(families.values()):
            expected = [u for u in units if families[u["case_id"]] == family]
            found = [by_id[u["unit_id"]] for u in expected if u["unit_id"] in by_id]
            family_rows.append({"system": system, "family": family, "planned": len(expected), "attempted": len(found),
                                "successes": sum(r["score"]["success"] for r in found),
                                "success_rate_all_planned": rate(sum(r["score"]["success"] for r in found), len(expected))})
    main = [u for u in plan if u["system"] in ("P", "B2")]
    primary_complete = len(results) == len(plan) and all(u["unit_id"] in by_id for u in main)
    case_rows = []
    for identity in families:
        scores = {}
        for system in ("B2", "P"):
            units = [u for u in main if u["case_id"] == identity and u["system"] == system]
            scores[system] = sum(by_id[u["unit_id"]]["score"]["success"] if u["unit_id"] in by_id else 0 for u in units) / len(units)
        case_rows.append({"case_id": identity, "B2": scores["B2"], "P": scores["P"], "difference_pp": 100 * (scores["P"] - scores["B2"])})
    effect = statistics.mean(r["difference_pp"] for r in case_rows)
    interval = None
    if primary_complete:
        rng = random.Random(20261110)
        differences = [r["difference_pp"] for r in case_rows]
        draws = sorted(statistics.mean(rng.choices(differences, k=len(differences))) for _ in range(10000))
        # Deterministic nearest-rank empirical percentile indices, predeclared.
        interval = [draws[249], draws[9749]]
    seed_rows = []
    for seed in (17011, 17023, 17033):
        counts = {system: sum(by_id[u["unit_id"]]["score"]["success"] if u["unit_id"] in by_id else 0
                              for u in main if u["seed"] == seed and u["system"] == system) for system in ("B2", "P")}
        seed_rows.append({"seed": seed, **counts, "difference_pp": 100 * (counts["P"] - counts["B2"]) / len(families)})
    return {"status": "COMPLETE" if len(results) == len(plan) else "INCONCLUSIVE_INCOMPLETE_MATRIX", "planned": len(plan), "attempted": len(results),
            "systems": systems, "families": family_rows, "paired_cases": case_rows, "seed_differences": seed_rows,
            "primary": {"comparison": "P minus B2", "all_primary_units_present": primary_complete, "difference_pp_all_planned": effect,
                        "exploratory_paired_case_interval_95_pp": interval,
                        "scope": "Conditional authored-case resampling; not a biological or real-user population interval"},
            "protected_data_access": False, "independent_expert_validation": False}
