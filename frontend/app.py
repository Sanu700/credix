import streamlit as st
import requests
from datetime import date
import pandas as pd

BASE_URL = "http://localhost:8080/loan"

st.set_page_config(
    page_title="DebtForge",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0f0f0f;
    color: #e8e0d0;
}

h1, h2, h3 { font-family: 'Syne', sans-serif; color: #f5c542; }

.stSidebar {
    background-color: #151515 !important;
    border-right: 1px solid #2a2a2a;
}

section[data-testid="stSidebar"] * { color: #e8e0d0 !important; }

.stButton > button {
    background-color: #f5c542;
    color: #0f0f0f;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    border: none;
    border-radius: 4px;
    padding: 10px 24px;
    letter-spacing: 0.05em;
    transition: all 0.2s;
}
.stButton > button:hover {
    background-color: #e0b030;
    transform: translateY(-1px);
}

.metric-card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 4px solid #f5c542;
    border-radius: 6px;
    padding: 18px 22px;
    margin: 8px 0;
}
.metric-label { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.1em; }
.metric-value { font-size: 1.5rem; font-family: 'Syne', sans-serif; color: #f5c542; margin-top: 4px; }

.status-active  { color: #4ade80; font-weight: 700; }
.status-closed  { color: #60a5fa; font-weight: 700; }
.status-default { color: #f87171; font-weight: 700; }

.tx-row {
    background: #1a1a1a;
    border: 1px solid #252525;
    border-radius: 4px;
    padding: 10px 16px;
    margin: 4px 0;
    display: flex;
    justify-content: space-between;
}

.stTextInput > div > input,
.stNumberInput > div > input,
.stSelectbox > div > div,
.stDateInput > div > input {
    background-color: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #e8e0d0 !important;
    border-radius: 4px !important;
}

div[data-testid="stForm"] {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 24px;
}

.forge-header {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #f5c542;
    letter-spacing: -0.02em;
    margin-bottom: 0;
}
.forge-sub {
    color: #666;
    font-size: 0.85rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.success-box {
    background: #0f2a1a;
    border: 1px solid #2d6a3f;
    border-radius: 6px;
    padding: 16px 20px;
    color: #4ade80;
    margin: 12px 0;
}
.error-box {
    background: #2a0f0f;
    border: 1px solid #6a2d2d;
    border-radius: 6px;
    padding: 16px 20px;
    color: #f87171;
    margin: 12px 0;
}

.stDataFrame { background: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────
def api_post(path, payload):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload, timeout=5)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is Spring Boot running on port 8080?"}, 503
    except Exception as e:
        return {"error": str(e)}, 500

def api_get(path):
    try:
        r = requests.get(f"{BASE_URL}{path}", timeout=5)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Is Spring Boot running on port 8080?"}, 503
    except Exception as e:
        return {"error": str(e)}, 500

def fmt_inr(val):
    if val is None:
        return "—"
    return f"₹{float(val):,.2f}"

def status_badge(s):
    cls = {"ACTIVE": "status-active", "CLOSED": "status-closed", "DEFAULTED": "status-default"}.get(s, "")
    return f'<span class="{cls}">● {s}</span>'

def show_error(data):
    msg = data.get("error") or data.get("message") or str(data)
    st.markdown(f'<div class="error-box">⚠ {msg}</div>', unsafe_allow_html=True)

def show_success(msg):
    st.markdown(f'<div class="success-box">✓ {msg}</div>', unsafe_allow_html=True)

def metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙ DebtForge")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏗  Create Loan", "📐 EMI Calculator", "💳 Record Payment", "📊 Loan Summary"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown('<p style="color:#444;font-size:0.75rem;">Backend: localhost:8080</p>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 1: Create Loan
# ══════════════════════════════════════════════
if page == "🏗  Create Loan":
    st.markdown('<div class="forge-header">Create Loan</div>', unsafe_allow_html=True)
    st.markdown('<div class="forge-sub">Register a new loan in the system</div>', unsafe_allow_html=True)

    with st.form("create_loan_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Borrower Name", placeholder="e.g. Ravi Sharma")
            principal = st.number_input("Principal Amount (₹)", min_value=1000.0, value=100000.0, step=1000.0)
        with col2:
            interest = st.number_input("Annual Interest Rate (%)", min_value=0.1, max_value=100.0, value=12.0, step=0.1)
            tenure = st.number_input("Tenure (Months)", min_value=1, max_value=360, value=24, step=1)
        start = st.date_input("Start Date", value=date.today())
        submitted = st.form_submit_button("⚙ FORGE LOAN")

    if submitted:
        if not name.strip():
            show_error({"error": "Borrower name is required."})
        else:
            payload = {
                "borrowerName": name.strip(),
                "principal": principal,
                "annualInterestRate": interest,
                "tenureMonths": int(tenure),
                "startDate": str(start)
            }
            data, code = api_post("", payload)
            if code == 201:
                show_success(f"Loan #{data['id']} created for **{data['borrowerName']}**")
                c1, c2, c3 = st.columns(3)
                with c1: metric_card("Loan ID", f"#{data['id']}")
                with c2: metric_card("Monthly EMI", fmt_inr(data.get('emi')))
                with c3: metric_card("Outstanding", fmt_inr(data.get('outstandingBalance')))
            else:
                show_error(data)


# ══════════════════════════════════════════════
# PAGE 2: EMI Calculator
# ══════════════════════════════════════════════
elif page == "📐 EMI Calculator":
    st.markdown('<div class="forge-header">EMI Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="forge-sub">Fetch EMI breakdown for an existing loan</div>', unsafe_allow_html=True)

    with st.form("emi_form"):
        loan_id = st.number_input("Loan ID", min_value=1, step=1, value=1)
        go = st.form_submit_button("📐 CALCULATE EMI")

    if go:
        data, code = api_get(f"/{int(loan_id)}/emi")
        if code == 200:
            c1, c2, c3 = st.columns(3)
            with c1: metric_card("Monthly EMI", fmt_inr(data.get('monthlyEmi')))
            with c2: metric_card("Total Payable", fmt_inr(data.get('totalPayable')))
            with c3: metric_card("Total Interest", fmt_inr(data.get('totalInterest')))

            st.markdown("---")
            c4, c5, c6 = st.columns(3)
            with c4: metric_card("Principal", fmt_inr(data.get('principal')))
            with c5: metric_card("Interest Rate", f"{data.get('annualInterestRate')}% p.a.")
            with c6: metric_card("Tenure", f"{data.get('tenureMonths')} months")

            # Amortization table preview
            st.markdown("### Amortisation Schedule (first 6 months)")
            emi = float(data.get('monthlyEmi', 0))
            principal_val = float(data.get('principal', 0))
            rate = float(data.get('annualInterestRate', 0)) / 1200
            rows = []
            balance = principal_val
            for i in range(1, min(7, int(data.get('tenureMonths', 1)) + 1)):
                interest_part = round(balance * rate, 2)
                principal_part = round(emi - interest_part, 2)
                balance = max(0, round(balance - principal_part, 2))
                rows.append({
                    "Month": i,
                    "EMI (₹)": f"{emi:,.2f}",
                    "Principal (₹)": f"{principal_part:,.2f}",
                    "Interest (₹)": f"{interest_part:,.2f}",
                    "Balance (₹)": f"{balance:,.2f}"
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            show_error(data)


# ══════════════════════════════════════════════
# PAGE 3: Record Payment
# ══════════════════════════════════════════════
elif page == "💳 Record Payment":
    st.markdown('<div class="forge-header">Record Payment</div>', unsafe_allow_html=True)
    st.markdown('<div class="forge-sub">Post a payment transaction against a loan</div>', unsafe_allow_html=True)

    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        with col1:
            loan_id = st.number_input("Loan ID", min_value=1, step=1, value=1)
            amount = st.number_input("Payment Amount (₹)", min_value=1.0, value=5000.0, step=100.0)
        with col2:
            pay_date = st.date_input("Payment Date", value=date.today())
            tx_type = st.selectbox("Transaction Type", ["EMI", "PREPAYMENT", "LATE_FEE"])
        remarks = st.text_input("Remarks (optional)", placeholder="e.g. October EMI")
        submitted = st.form_submit_button("💳 RECORD PAYMENT")

    if submitted:
        payload = {
            "amount": amount,
            "paymentDate": str(pay_date),
            "type": tx_type,
            "remarks": remarks.strip() or None
        }
        data, code = api_post(f"/{int(loan_id)}/payment", payload)
        if code == 201:
            show_success(f"Payment of {fmt_inr(data.get('amount'))} recorded (Tx #{data['id']})")
            c1, c2, c3 = st.columns(3)
            with c1: metric_card("Transaction ID", f"#{data['id']}")
            with c2: metric_card("Amount Paid", fmt_inr(data.get('amount')))
            with c3: metric_card("Date", str(data.get('paymentDate')))
        else:
            show_error(data)


# ══════════════════════════════════════════════
# PAGE 4: Loan Summary
# ══════════════════════════════════════════════
elif page == "📊 Loan Summary":
    st.markdown('<div class="forge-header">Loan Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="forge-sub">Full details and transaction history</div>', unsafe_allow_html=True)

    with st.form("summary_form"):
        loan_id = st.number_input("Loan ID", min_value=1, step=1, value=1)
        go = st.form_submit_button("📊 LOAD SUMMARY")

    if go:
        data, code = api_get(f"/{int(loan_id)}")
        if code == 200:
            # Header row
            col_name, col_status = st.columns([3, 1])
            with col_name:
                st.markdown(f"### {data.get('borrowerName')}")
                st.markdown(f"Loan #{data.get('id')} · Started {data.get('startDate')} · {data.get('tenureMonths')} months")
            with col_status:
                st.markdown(f"<br>{status_badge(data.get('status', ''))}", unsafe_allow_html=True)

            st.markdown("---")

            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1: metric_card("Principal", fmt_inr(data.get('principal')))
            with c2: metric_card("Monthly EMI", fmt_inr(data.get('emi')))
            with c3: metric_card("Total Paid", fmt_inr(data.get('totalAmountPaid')))
            with c4: metric_card("Outstanding", fmt_inr(data.get('outstandingBalance')))

            # Progress bar
            emi = float(data.get('emi') or 0)
            tenure = int(data.get('tenureMonths') or 1)
            total_payable = emi * tenure
            paid = float(data.get('totalAmountPaid') or 0)
            progress = min(1.0, paid / total_payable) if total_payable > 0 else 0

            st.markdown("---")
            st.markdown(f"**Repayment Progress** — {progress*100:.1f}% complete")
            st.progress(progress)

            # Transactions
            txs = data.get("transactions", [])
            st.markdown(f"---\n### Transaction History ({len(txs)} records)")
            if txs:
                tx_df = pd.DataFrame([{
                    "Tx #": t.get("id"),
                    "Date": t.get("paymentDate"),
                    "Amount (₹)": f"{float(t.get('amount',0)):,.2f}",
                    "Type": t.get("type"),
                    "Remarks": t.get("remarks") or "—"
                } for t in txs])
                st.dataframe(tx_df, use_container_width=True, hide_index=True)
            else:
                st.markdown('<p style="color:#555;">No transactions recorded yet.</p>', unsafe_allow_html=True)
        else:
            show_error(data)
