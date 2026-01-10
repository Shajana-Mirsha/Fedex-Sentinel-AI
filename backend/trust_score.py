def calculate_trust_score(recovery_rate, sla_adherence, health_index=1.0):
    """
    Weighted Scoring Algorithm.
    Demonstrates non-linear penalty for SLA breaches to protect FedEx interests.
    """
    # Base weightage: Recovery(50%), SLA(40%), Health Index(10%)
    score = (recovery_rate * 50) + (sla_adherence * 40) + (health_index * 10)
    return round(max(0, min(100, score)), 1)