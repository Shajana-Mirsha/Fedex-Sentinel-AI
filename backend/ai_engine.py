import math

def predict_recovery_probability(amount, days_overdue, dca_perf):
    """
    AI Propensity Engine: Predicts the likelihood of collecting the ₹ amount.
    Higher amounts in B2B logistics are harder to recover once they cross 90 days.
    """
    # Exponential decay based on Indian market credit cycles (typically 45-60 days)
    time_decay = math.exp(-days_overdue / 120)
    
    # Large Ticket Risk: Invoices > ₹1,00,000 carry higher litigation risk
    complexity = 0.82 if amount > 100000 else 1.0
    
    probability = (dca_perf / 100) * time_decay * complexity * 100
    return round(max(5.0, min(99.0, probability)), 1)