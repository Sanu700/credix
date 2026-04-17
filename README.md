# ⚙ DebtForge — Loan & Payment Management Platform

## Stack
- **Backend**: Java 17, Spring Boot 3, Maven, H2, Lombok
- **Frontend**: Python, Streamlit, requests, pandas

---

## Quick Start

### 1. Backend
```bash
cd backend
mvn spring-boot:run
# Runs on http://localhost:8080
# H2 Console: http://localhost:8080/h2-console
```

### 2. Frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
# Runs on http://localhost:8501
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/loan` | Create a new loan |
| GET | `/loan/{id}` | Get loan details + transactions |
| GET | `/loan/{id}/emi` | Get EMI breakdown |
| POST | `/loan/{id}/payment` | Record a payment |

### POST /loan — Request Body
```json
{
  "borrowerName": "Ravi Sharma",
  "principal": 500000,
  "annualInterestRate": 12.5,
  "tenureMonths": 60,
  "startDate": "2024-01-01"
}
```

### POST /loan/{id}/payment — Request Body
```json
{
  "amount": 11247.00,
  "paymentDate": "2024-02-01",
  "type": "EMI",
  "remarks": "February EMI"
}
```

---

## EMI Formula
```
EMI = P × r × (1+r)^n / ((1+r)^n − 1)
where r = annualRate / 1200,  n = tenureMonths
```
