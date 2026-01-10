from ai_engine import predict_recovery_probability
from governance import get_governance_state

def smart_allocate(cases, dcas):
    """
    Smart Matching: Only matches high-value ₹ cases to Premier DCAs.
    """
    allocations = {dca['dca_name']: [] for dca in dcas}
    sorted_dcas = sorted(dcas, key=lambda x: x['trust_score'], reverse=True)

    for case in cases:
        assigned = False
        for dca in sorted_dcas:
            state, _ = get_governance_state(dca['trust_score'])
            
            # Policy: If DCA is RESTRICTED, they cannot handle ₹50k+ or 60+ days overdue
            if state == "RESTRICTED" and (case['amount'] > 50000 or case['days_overdue'] > 60):
                continue
            
            prob = predict_recovery_probability(case['amount'], case['days_overdue'], dca['trust_score'])
            
            allocations[dca['dca_name']].append({
                "case_id": case['case_id'],
                "amount": case['amount'],
                "recovery_prob": prob,
                "tier": state
            })
            assigned = True
            break
            
        if not assigned:
            if "FEDEX_INTERNAL_LEGAL" not in allocations:
                allocations["FEDEX_INTERNAL_LEGAL"] = []
            allocations["FEDEX_INTERNAL_LEGAL"].append(case)

    return allocations