from ai_engine import predict_recovery_probability
from governance import get_governance_state

def smart_allocate(cases, dcas):
    allocations = {dca["dca_name"]: [] for dca in dcas}
    sorted_dcas = sorted(dcas, key=lambda x: x["trust_score"], reverse=True)

    for case in cases:
        for dca in sorted_dcas:
            tier, _ = get_governance_state(dca["trust_score"])

            # SOP restriction
            if tier == "RESTRICTED" and (
                case["amount"] > 50000 or case["days_overdue"] > 60
            ):
                continue

            prob = predict_recovery_probability(
                case["amount"],
                case["days_overdue"],
                dca["trust_score"]
            )

            allocations[dca["dca_name"]].append({
                "case_id": case["case_id"],
                "amount": case["amount"],
                "days_overdue": case["days_overdue"],
                "recovery_prob": prob
            })
            break

    return allocations
