def get_governance_state(trust_score):
    score = float(trust_score)

    if score >= 0.90:
        return "PREMIER PARTNER", "#4D148C"
    elif score >= 0.75:
        return "ACTIVE STANDARD", "#FF6600"
    elif score >= 0.50:
        return "PROBATIONARY", "#f39c12"
    else:
        return "RESTRICTED", "#e74c3c"
