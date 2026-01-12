import csv, os, webbrowser
from datetime import datetime

# Import modular components
from ai_engine import predict_recovery_probability
from governance import get_governance_state
from allocator import smart_allocate
from trust_score import calculate_trust_score
from sla_checker import check_sla

# --- SYSTEM CONFIG ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

def setup_production_data():
    """Generates high-integrity mock data for the demo."""
    with open(os.path.join(DATA_DIR, "dcas.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["dca_name", "recovery_rate", "sla_adherence"])
        writer.writerows([
            ["Alpha India Recovery", 0.95, 0.98],
            ["Beta Recoveries", 0.78, 0.85],
            ["Gamma Debt-Solvers", 0.40, 0.50]
        ])

    with open(os.path.join(DATA_DIR, "cases.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["case_id", "invoice_amount", "days_overdue"])
        writer.writerows([
            ["IND-7701", 450000, 15],
            ["IND-7702", 12000, 75],
            ["IND-7703", 95000, 45],
            ["IND-7704", 5000, 95]
        ])

def build_dashboard():
    print("FedEx Sentinel: Merging Modules & Building Governance Dashboard...")
    setup_production_data()

    # 1. Load DCAs
    dcas = []
    dca_map = {}
    with open(os.path.join(DATA_DIR, "dcas.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            r["trust_score"] = calculate_trust_score(
                r["recovery_rate"], r["sla_adherence"]
            )
            dcas.append(r)
            dca_map[r["dca_name"]] = r

    # 2. Load Cases
    cases = []
    with open(os.path.join(DATA_DIR, "cases.csv"), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cases.append({
                "case_id": r["case_id"],
                "amount": float(r["invoice_amount"]),
                "days_overdue": int(r["days_overdue"])
            })

    # 3. Core Logic
    allocations = smart_allocate(cases, dcas)
    sla_alerts = check_sla(cases)

    # 4. KPIs (COMPUTED ONCE – FIXED)
    total_portfolio = sum(c["amount"] for c in cases)

    all_probs = []
    for d_list in allocations.values():
        for c in d_list:
            all_probs.append(c["recovery_prob"])

    avg_prob = round(sum(all_probs) / len(all_probs), 1) if all_probs else 0

    # 5. UI (UNCHANGED)
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>FedEx Sentinel | DCA Governance</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {{ --fedex-purple: #4D148C; --fedex-orange: #FF6600; }}
            body {{ background: #f4f7fc; font-family: 'Inter', sans-serif; color: #333; }}
            .navbar {{ background: var(--fedex-purple); color: white; border-bottom: 4px solid var(--fedex-orange); }}
            .metric-card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); text-align: center; border-bottom: 4px solid #eee; }}
            .metric-value {{ font-size: 1.8rem; font-weight: 800; color: var(--fedex-purple); }}
            .agency-header {{ background: #fff; padding: 15px; border-radius: 10px 10px 0 0; border-left: 5px solid var(--fedex-orange); margin-top: 30px; }}
            .alert-box {{ background: #fff1f1; border-left: 5px solid #d9534f; padding: 15px; border-radius: 8px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <nav class="navbar px-4 py-3 mb-4">
            <h4 class="m-0"><i class="fas fa-shield-alt"></i> FedEx Sentinel: DCA Governance</h4>
            <span class="badge bg-light text-dark">Status: LIVE</span>
        </nav>

        <div class="container">
            <div class="row g-3 mb-4">
                <div class="col-md-4">
                    <div class="metric-card">
                        <small class="text-muted">PORTFOLIO UNDER MANAGEMENT</small>
                        <div class="metric-value">₹{total_portfolio:,.1f}</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <small class="text-muted">AVG RECOVERY PROBABILITY</small>
                        <div class="metric-value">{avg_prob:.1f}%</div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="metric-card">
                        <small class="text-muted">GOVERNANCE STATUS</small>
                        <div class="metric-value text-success">ACTIVE</div>
                    </div>
                </div>
            </div>
    """

    for dca_name, d_cases in allocations.items():
        dca_info = dca_map[dca_name]
        tier, color = get_governance_state(dca_info["trust_score"])

        html += f"""
            <div class="agency-header d-flex justify-content-between align-items-center shadow-sm">
                <h5 class="m-0 fw-bold">{dca_name}</h5>
                <span class="badge" style="background:{color}">{tier}</span>
            </div>
            <div class="bg-white p-3 shadow-sm rounded-bottom mb-4">
                <table class="table table-hover align-middle m-0">
                    <thead class="table-light small">
                        <tr><th>Case ID</th><th>Invoice Amount</th><th>Recovery Probability</th><th>SOP Status</th></tr>
                    </thead>
                    <tbody>
        """

        if not d_cases:
            html += "<tr><td colspan='4' class='text-center text-muted'>No cases assigned in this cycle</td></tr>"
        else:
            for c in d_cases:
                html += f"""
                    <tr>
                        <td><strong>{c['case_id']}</strong></td>
                        <td>₹{c['amount']:,}</td>
                        <td>
                            <div class="progress" style="height:8px; width:100px;">
                                <div class="progress-bar" style="width:{c['recovery_prob']}%; background:{color}"></div>
                            </div> {c['recovery_prob']}%
                        </td>
                        <td><span class="text-success"><i class="fas fa-check-circle"></i> Verified</span></td>
                    </tr>
                """
        html += "</tbody></table></div>"

    html += """
            <div class="mt-5 mb-5">
                <h5 class="fw-bold"><i class="fas fa-exclamation-triangle text-danger"></i> SLA Alerts</h5>
                <div class="alert-box shadow-sm">
    """

    for alert in sla_alerts:
        html += f"<div class='mb-2 small'>{alert}</div>"

    html += """
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    path = os.path.join(FRONTEND_DIR, "dashboard.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"SYSTEM MERGE COMPLETE: {path}")
    webbrowser.open("file://" + path)

if __name__ == "__main__":
    build_dashboard()
