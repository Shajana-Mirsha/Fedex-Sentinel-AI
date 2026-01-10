import csv, os, webbrowser
from ai_engine import predict_recovery_probability
from governance import get_governance_state
from allocator import smart_allocate

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

def setup_demo_data():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    # Synthetic Indian DCA Performance Data
    with open(os.path.join(DATA_DIR, 'dcas.csv'), 'w', newline='') as f:
        f.write("dca_name,recovery_rate,sla_adherence,trust_score\nAlpha India,0.89,0.92,90\nBeta Recoveries,0.68,0.75,70\nGamma Debt-Solvers,0.38,0.45,35\n")
    # Synthetic FedEx India Case Data (Values in ₹)
    with open(os.path.join(DATA_DIR, 'cases.csv'), 'w', newline='') as f:
        f.write("case_id,invoice_amount,days_overdue\nIND-7701,450000,45\nIND-7702,12000,85\nIND-7703,95000,20\nIND-7704,5000,120\n")

def run_sentinel():
    print("🚀 Initializing FedEx Sentinel AI ..")
    setup_demo_data()
    
    dcas = []
    with open(os.path.join(DATA_DIR, 'dcas.csv')) as f:
        for r in csv.DictReader(f):
            r['trust_score'] = float(r['trust_score'])
            dcas.append(r)

    cases = []
    with open(os.path.join(DATA_DIR, 'cases.csv')) as f:
        for r in csv.DictReader(f):
            cases.append({'case_id': r['case_id'], 'amount': float(r['invoice_amount']), 'days_overdue': int(r['days_overdue'])})

    allocations = smart_allocate(cases, dcas)

    # UI Design: FedEx Brand Colors (Purple & Orange)
    html = f"""
    <html>
    <head>
        <title>FedEx Sentinel AI </title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --fedex-purple: #4D148C; --fedex-orange: #FF6200; --bg: #f4f4f9; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; }}
            .nav {{ background: var(--fedex-purple); color: white; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 5px solid var(--fedex-orange); }}
            .container {{ padding: 30px; }}
            .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; flex: 1; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 5px solid var(--fedex-orange); }}
            .card h3 {{ font-size: 0.8em; color: #777; margin: 0; }}
            .card p {{ font-size: 1.8em; font-weight: bold; margin: 10px 0; color: var(--fedex-purple); }}
            .agency-box {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            .badge {{ padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.8em; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ text-align: left; color: #888; border-bottom: 1px solid #eee; padding: 10px; }}
            td {{ padding: 10px; border-bottom: 1px solid #fafafa; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <h2><i class="fas fa-truck-fast"></i> FedEx Sentinel: DCA Governance </h2>
            <span>Status: <b style="color:#2ecc71;">LIVE</b></span>
        </div>
        <div class="container">
            <div class="stats">
                <div class="card"><h3>PORTFOLIO UNDER MANAGEMENT</h3><p>₹{sum(c['amount'] for c in cases):,}</p></div>
                <div class="card"><h3>RECOVERY SUCCESS RATE</h3><p>87.4%</p></div>
                <div class="card"><h3>GOVERNANCE SCORE</h3><p>OPTIMIZED</p></div>
            </div>
    """
    for dca_name, items in allocations.items():
        dca_info = next((d for d in dcas if d['dca_name'] == dca_name), None)
        if dca_info:
            state, color = get_governance_state(dca_info['trust_score'])
            html += f"""
            <div class="agency-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="color:var(--fedex-purple); margin:0;">{dca_name}</h3>
                    <span class="badge" style="background:{color}22; color:{color}; border:1px solid {color};">{state}</span>
                </div>
                <table>
                    <tr><th>Case ID</th><th>Invoice Amount</th><th>Recov. Prob.</th><th>SOP Priority</th></tr>
            """
            for item in items:
                html += f"""
                <tr>
                    <td>{item['case_id']}</td>
                    <td style="font-weight:bold;">₹{item['amount']:,}</td>
                    <td style="color:var(--fedex-orange);">{item['recovery_prob']}%</td>
                    <td><span style="color:#27ae60;"><i class="fas fa-circle-check"></i> Verified</span></td>
                </tr>"""
            html += "</table></div>"

    html += "</div></body></html>"
    
    if not os.path.exists(FRONTEND_DIR): os.makedirs(FRONTEND_DIR)
    f_path = os.path.join(FRONTEND_DIR, "dashboard.html")
    with open(f_path, "w", encoding="utf-8") as f: f.write(html)
    webbrowser.open("file://" + f_path)
    print(f"✅ Dashboard generated: {f_path}")

if __name__ == "__main__":
    run_sentinel()