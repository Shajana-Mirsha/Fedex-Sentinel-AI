def check_sla(cases):
    alerts = []

    for case in cases:
        if case["days_overdue"] > 90:
            alerts.append(f"CRITICAL escalation: Case {case['case_id']}")
        elif case["days_overdue"] > 60:
            alerts.append(f"Warning: SLA risk for Case {case['case_id']}")

    return alerts
