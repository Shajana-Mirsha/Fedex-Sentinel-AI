import math

def predict_recovery_probability(amount, days_overdue, trust_score):
    """
    Explainable AI Recovery Model
    """

    base_probability = 95.0
    decay_rate = 0.005

    time_factor = math.exp(-decay_rate * days_overdue)

    # trust_score is 0.0–1.0 → scale safely
    dca_factor = 0.5 + (trust_score * 0.5)

    probability = base_probability * time_factor * dca_factor

    # High-value risk adjustment
    if amount > 200000:
        probability *= 0.9

    return round(max(2.0, min(99.0, probability)), 1)
