def calculate_trust_score(recovery_rate, sla_adherence):
    rr = float(recovery_rate)
    sla = float(sla_adherence)

    score = (rr * 0.6) + (sla * 0.4)
    return round(max(0.0, min(1.0, score)), 2)
