import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Credix", layout="wide")

BASE_URL = "https://credix-1.onrender.com"

# ---------------- STYLES ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #020617, #0f172a);
}

.block-container {
    padding-top: 1.5rem;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 16px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 30px rgba(0,0,0,0.4);
    margin-bottom: 15px;
}

/* KPI */
.kpi {
    font-size: 28px;
    font-weight: bold;
}

.sub {
    color: #9CA3AF;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
col1, col2 = st.columns([1, 8])

with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2721/2721276.png", width=70)

with col2:
    st.markdown("""
    <h1 style='margin-bottom:0;'>Credix</h1>
    <p style='color:#9CA3AF;'>Loan Intelligence Platform</p>
    """, unsafe_allow_html=True)

# ---------------- NAV ----------------
menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Create Loan",
    "EMI Calculator",
    "Record Payment",
    "Loan Summary"
])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.header("📊 Portfolio Dashboard")

    try:
        res = requests.get(f"{BASE_URL}/loan/all")

        if res.status_code != 200:
            st.error("Backend not reachable")
        else:
            loans = res.json()

            if len(loans) == 0:
                st.warning("No loans yet")
            else:
                df = pd.DataFrame(loans)

                total_loans = len(df)
                total_principal = df["principal"].sum()
                avg_rate = df["annualInterestRate"].mean()

                # KPI
                c1, c2, c3 = st.columns(3)

                c1.markdown(f"<div class='card'><div class='kpi'>{total_loans}</div><div class='sub'>Total Loans</div></div>", unsafe_allow_html=True)
                c2.markdown(f"<div class='card'><div class='kpi'>₹{total_principal:,.0f}</div><div class='sub'>Portfolio Value</div></div>", unsafe_allow_html=True)
                c3.markdown(f"<div class='card'><div class='kpi'>{avg_rate:.2f}%</div><div class='sub'>Avg Interest Rate</div></div>", unsafe_allow_html=True)

                st.markdown("### 📈 Insights")

                col1, col2 = st.columns(2)

                fig1 = px.pie(df, names="borrowerName", values="principal",
                              title="Loan Distribution")
                col1.plotly_chart(fig1, use_container_width=True)

                fig2 = px.bar(df, x="borrowerName", y="principal",
                              title="Principal by Borrower")
                col2.plotly_chart(fig2, use_container_width=True)

                st.markdown("### 🧾 Loan Records")

                df["status"] = df["status"].apply(
                    lambda x: "🟢 Active" if x == "ACTIVE" else "🔴 Closed"
                )

                st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error("Error connecting backend")
        st.write(e)

# ---------------- CREATE LOAN ----------------
elif menu == "Create Loan":
    st.header("🏦 Create Loan")

    name = st.text_input("Borrower Name")

    col1, col2 = st.columns(2)
    principal = col1.number_input("Principal (₹)", min_value=0.0)
    rate = col2.number_input("Interest Rate (%)", min_value=0.0)

    tenure = st.number_input("Tenure (months)", min_value=1)

    if st.button("🚀 Create Loan"):
        st.toast("Processing...", icon="⏳")

        res = requests.post(f"{BASE_URL}/loan", json={
            "borrowerName": name,
            "principal": principal,
            "annualInterestRate": rate,
            "tenureMonths": tenure
        })

        if res.status_code in [200, 201]:
            st.success("Loan created successfully 🚀")
            st.balloons()
        else:
            st.error(f"Error: {res.status_code}")
            st.write(res.text)

# ---------------- EMI ----------------
elif menu == "EMI Calculator":
    st.header("📉 EMI Calculator")

    loan_id = st.number_input("Loan ID", min_value=1)

    if st.button("Calculate EMI"):
        res = requests.get(f"{BASE_URL}/loan/{int(loan_id)}/emi")

        if res.status_code == 200:
            data = res.json()

            st.metric("Monthly EMI", f"₹{data['monthlyEmi']}")
            st.metric("Total Interest", f"₹{data['totalInterest']}")

            months = list(range(1, data["tenureMonths"] + 1))
            emi_values = [float(data["monthlyEmi"])] * len(months)

            fig = px.line(x=months, y=emi_values,
                          labels={"x": "Month", "y": "EMI"},
                          title="EMI Timeline")

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.error("Invalid Loan ID")

# ---------------- PAYMENT ----------------
elif menu == "Record Payment":
    st.header("💸 Record Payment")

    loan_id = st.number_input("Loan ID", min_value=1)
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Pay"):
        res = requests.post(f"{BASE_URL}/loan/{int(loan_id)}/payment", json={
            "amount": amount
        })

        if res.status_code in [200, 201]:
            st.success("Payment recorded ✅")
        else:
            st.error("Payment failed")

# ---------------- SUMMARY ----------------
elif menu == "Loan Summary":
    st.header("📋 Loan Summary")

    loan_id = st.number_input("Loan ID", min_value=1)

    if st.button("Fetch"):
        res = requests.get(f"{BASE_URL}/loan/{int(loan_id)}")

        if res.status_code == 200:
            data = res.json()

            col1, col2 = st.columns(2)

            col1.metric("Principal", f"₹{data['principal']:,}")
            col2.metric("Interest Rate", f"{data['annualInterestRate']}%")

            col1.metric("Tenure", f"{data['tenureMonths']} months")
            col2.metric("Outstanding", f"₹{data['outstandingBalance']:,}")

            st.success("Data loaded ✅")

            if data.get("transactions"):
                st.subheader("Transactions")
                st.dataframe(pd.DataFrame(data["transactions"]))

        else:
            st.error("Loan not found")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Credix | Built with Spring Boot + Streamlit | Production-style FinTech Dashboard")
