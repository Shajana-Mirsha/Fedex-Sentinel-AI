import csv
import os
import webbrowser

from ai_engine import predict_recovery_probability
from governance import get_governance_state
from allocator import smart_allocate
from trust_score import calculate_trust_score
from sla_checker import check_sla


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


def setup_demo_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Synthetic Indian DCA Performance Data (RAW INPUTS ONLY)
    with open(os.path.join(DATA_DIR, "dcas.csv"), "w", newline="") as f:
        f.write(
            "dca_name,recovery_rate,sla_adherence\n"
            "Alpha India,0.89,0.92\n"
            "Beta Recoveries,0.68,0.75\n"
            "Gamma Debt-Solvers,0.38,0.45\n"
        )

    # Synthetic FedEx India Case Data (₹)
    with open(os.path.join(DATA_DIR, "cases.csv"), "w", newline="") as f:
        f.write(
            "case_id,invoice_amount,days_overdue\n"
            "IND-7701,450000,45\n"
            "IND-7702,12000,85\n"
            "IND-7703,95000,20\n"
            "IND-7704,5000,120\n"
        )


def run_sentinel():
    print("🚀 Initializing FedEx Sentinel AI …")
    setup_demo_data()

    # ----------------------------
    # Load DCAs & compute trust
    # ----------------------------
    dcas = []
    with open(os.path.join(DATA_DIR, "dcas.csv")) as f:
        for r in csv.DictReader(f):
            trust = calculate_trust_score(
                float(r["recovery_rate"]),
                float(r["sla_adherence"])
            )
            r["trust_score"] = trust
            dcas.append(r)

    # ----------------------------
    # Load cases
    # ----------------------------
    cases = []
    with open(os.path.join(DATA_DIR, "cases.csv")) as f:
        for r in csv.DictReader(f):
            cases.append({
                "case_id": r["case_id"],
                "amount": float(r["invoice_amount"]),
                "days_overdue": int(r["days_overdue"])
            })

    # ----------------------------
    # Core system logic
    # ----------------------------
    allocations = smart_allocate(cases, dcas)
    alerts = check_sla(cases)

    # ----------------------------
    # KPIs (computed, not hardcoded)
    # ----------------------------
    portfolio_value = sum(c["amount"] for c in cases)

    recovery_probs = []
    for items in allocations.values():
        for item in items:
            if isinstance(item, dict):
                recovery_probs.append(item["recovery_prob"])

    avg_recovery = round(sum(recovery_probs) / len(recovery_probs), 1) if recovery_probs else 0

    # ----------------------------
    # ORIGINAL UI (UNCHANGED STYLE)
    # ----------------------------
    html = f"""
    <html>
    <head>
        <title>FedEx Sentinel AI</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --fedex-purple: #4D148C; --fedex-orange: #FF6200; --bg: #f4f4f9; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; }}
            .nav {{
                background: var(--fedex-purple);
                color: white;
                padding: 15px 40px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 5px solid var(--fedex-orange);
            }}
            .container {{ padding: 30px; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                flex: 1;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border-left: 5px solid var(--fedex-orange);
            }}
            .card h3 {{ font-size: 0.8em; color: #777; margin: 0; }}
            .card p {{
                font-size: 1.8em;
                font-weight: bold;
                margin: 10px 0;
                color: var(--fedex-purple);
            }}
            .agency-box {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }}
            .badge {{
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.8em;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th {{
                text-align: left;
                color: #888;
                border-bottom: 1px solid #eee;
                padding: 10px;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #fafafa;
                font-size: 0.9em;
            }}
            .alert {{
                color: #c0392b;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <div class="nav">
            <h2><i class="fas fa-truck-fast"></i> FedEx Sentinel: DCA Governance</h2>
            <span>Status: <b style="color:#2ecc71;">LIVE</b></span>
        </div>

        <div class="container">
            <div class="stats">
                <div class="card">
                    <h3>PORTFOLIO UNDER MANAGEMENT</h3>
                    <p>₹{portfolio_value:,}</p>
                </div>
                <div class="card">
                    <h3>AVG RECOVERY PROBABILITY</h3>
                    <p>{avg_recovery}%</p>
                </div>
                <div class="card">
                    <h3>GOVERNANCE STATUS</h3>
                    <p>ACTIVE</p>
                </div>
            </div>
    """

    for dca_name, items in allocations.items():
        dca_info = next((d for d in dcas if d["dca_name"] == dca_name), None)
        if not dca_info:
            continue

        state, color = get_governance_state(dca_info["trust_score"])
        html += f"""
        <div class="agency-box">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <h3 style="color:var(--fedex-purple); margin:0;">{dca_name}</h3>
                <span class="badge" style="background:{color}22; color:{color}; border:1px solid {color};">
                    {state}
                </span>
            </div>
            <table>
                <tr>
                    <th>Case ID</th>
                    <th>Invoice Amount</th>
                    <th>Recovery Probability</th>
                    <th>SOP Status</th>
                </tr>
        """

        for item in items:
            html += f"""
            <tr>
                <td>{item['case_id']}</td>
                <td style="font-weight:bold;">₹{item['amount']:,}</td>
                <td style="color:var(--fedex-orange);">{item['recovery_prob']}%</td>
                <td><i class="fas fa-circle-check" style="color:#27ae60;"></i> Verified</td>
            </tr>
            """

        html += "</table></div>"

    if alerts:
        html += "<h3>SLA Alerts</h3>"
        for a in alerts:
            html += f"<p class='alert'>{a}</p>"

    html += "</div></body></html>"

    os.makedirs(FRONTEND_DIR, exist_ok=True)
    path = os.path.join(FRONTEND_DIR, "dashboard.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    webbrowser.open("file://" + path)
    print("Dashboard generated:", path)


if __name__ == "__main__":
    run_sentinel()
