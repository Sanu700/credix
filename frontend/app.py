import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Credix", layout="wide")

BASE_URL = "https://credix-1.onrender.com"

st.title("💳 Credix — Loan Intelligence Platform")

menu = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Create Loan",
    "EMI Calculator",
    "Loan Summary"
])

# ---------------- DASHBOARD ----------------
if menu == "Dashboard":
    st.header("📊 Portfolio Dashboard")

    try:
        res = requests.get(f"{BASE_URL}/loan/all")
        loans = res.json()

        if len(loans) == 0:
            st.warning("No loans yet")
        else:
            df = pd.DataFrame(loans)

            total_loans = len(df)
            total_principal = df["principal"].sum()

            col1, col2 = st.columns(2)
            col1.metric("Total Loans", total_loans)
            col2.metric("Total Portfolio Value", f"₹{total_principal:,.0f}")

            # Chart
            fig = px.histogram(df, x="principal", nbins=10,
                               title="Loan Distribution")
            st.plotly_chart(fig, use_container_width=True)

            # Table
            st.subheader("📋 Loan Records")
            st.dataframe(df)

    except:
        st.error("Backend not reachable")

# ---------------- CREATE ----------------
elif menu == "Create Loan":
    st.header("🏦 Create Loan")

    col1, col2 = st.columns(2)

    principal = col1.number_input("Principal (₹)", min_value=0.0)
    rate = col2.number_input("Interest Rate (%)", min_value=0.0)
    tenure = st.number_input("Tenure (months)", min_value=1)

    if st.button("🚀 Create Loan"):
        res = requests.post(f"{BASE_URL}/loan", json={
            "principal": principal,
            "annualInterestRate": rate,
            "tenureMonths": tenure
        })

        if res.status_code == 200:
            st.success("Loan created successfully 🎉")
        else:
            st.error("Failed")

# ---------------- EMI ----------------
elif menu == "EMI Calculator":
    st.header("📉 EMI Calculator")

    loan_id = st.number_input("Loan ID", min_value=1)

    if st.button("Calculate EMI"):
        res = requests.get(f"{BASE_URL}/loan/{int(loan_id)}/emi")

        if res.status_code == 200:
            emi = res.json()
            st.metric("Monthly EMI", f"₹{emi:,.2f}")
        else:
            st.error("Invalid Loan ID")

# ---------------- SUMMARY ----------------
elif menu == "Loan Summary":
    st.header("📋 Loan Summary")

    loan_id = st.number_input("Loan ID", min_value=1)

    if st.button("Fetch"):
        res = requests.get(f"{BASE_URL}/loan/{int(loan_id)}")

        if res.status_code == 200:
            data = res.json()

            col1, col2 = st.columns(2)

            col1.metric("Principal", f"₹{data['principal']:,.0f}")
            col2.metric("Rate", f"{data['annualInterestRate']}%")

            col1.metric("Tenure", f"{data['tenureMonths']} months")

            st.success("Data loaded successfully")
        else:
            st.error("Loan not found")
