def get_governance_state(trust_score):
    """
    Automated Governance: Moves DCAs between 'Premier' and 'Restricted' status.
    This eliminates the "Manual Tracking" pain point.
    """
    if trust_score >= 82:
        return "PREMIER", "#27ae60"  
    elif trust_score >= 60:
        return "TRUSTED", "#2980b9"  
    elif trust_score >= 40:
        return "MONITORED", "#f39c12" 
    else:
        return "RESTRICTED", "#c0392b"