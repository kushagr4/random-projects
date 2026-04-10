import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
import json

#fetching data from API and converting it to a DataFrame
def get_covid_data():
    df = pd.read_csv(
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
    )

    df = df[df['location'] == 'United Kingdom']

    df = df[['date', 'new_cases', 'hosp_patients']]
    df.columns = ['date', 'cases', 'admissions']

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    return df

#recommendation function based on risk level
def recommendation(risk):
    if risk == "High":
        return "Urgent action required: increase capacity or introduce restrictions"
    elif risk == "Medium":
        return "Monitor closely and prepare contingency plans"
    else:
        return "System stable"

df = get_covid_data()

#if API fails
params = {
    "filters": "areaType=nation;areaName=England",
    "structure": json.dumps({
        "date": "date",
        "cases": "newCasesByPublishDate",
        "admissions": "newAdmissions"
    })
}

#loading and cleaning data
df = df.fillna(0)
df['cases_7day'] = df['cases'].rolling(7).mean()
df['admissions_7day'] = df['admissions'].rolling(7).mean()
df['admissions_growth'] = df['admissions_7day'].pct_change()
df = df.dropna()

# Create numerical time variable
df['day'] = range(len(df))

# Features and target
X = df[['day']]
y = df['admissions_7day']

#training the model
model = LinearRegression()
model.fit(X, y)

#predicting future admissions
future_days = 14
future_X = np.array(range(len(df), len(df) + future_days)).reshape(-1, 1)
predictions = model.predict(future_X)


#using streamlit
st.set_page_config(
    page_title="Hospital Overload Dashboard",
    layout="wide"
)

st.title("🏥 Hospital Overload Prediction Dashboard")

st.markdown("""
This tool forecasts hospital admissions and identifies when capacity may be exceeded.
Use the controls below to simulate different scenarios and assess system risk.
""")

#displaying data
st.subheader("Recent Data")
with st.expander("View raw data"):
    st.write(df.tail())

#user controls
st.subheader("System Controls")
capacity = st.slider("Hospital Capacity", 500, 5000, 2000)

#simulation
increase = st.slider("Simulate increase in admissions (%)", 0, 100, 0)
adjusted_predictions = predictions * (1 + increase / 100)

#overload detection  
overload_day = None
for i, value in enumerate(adjusted_predictions):
    if value > capacity:
        overload_day = i
        break

#risk level
if overload_day is not None and overload_day < 5:
    risk = "High"
elif overload_day is not None:
    risk = "Medium"
else:
    risk = "Low"

#key metrics
st.subheader("📊 Key Metrics")
latest = df.iloc[-1]
col1, col2, col3 = st.columns(3)
col1.metric("Current Admissions (7-day avg)", f"{latest['admissions_7day']:.0f}")
col2.metric("Growth Rate", f"{latest['admissions_growth']:.2%}")
col3.metric("Predicted Peak", f"{max(adjusted_predictions):.0f}")

#display risk level
st.subheader("⚠️ Risk Assessment")
if risk == "High":
    st.error(f"High Risk: Capacity exceeded in {overload_day} days")
elif risk == "Medium":
    st.warning(f"Medium Risk: Capacity pressure expected")
else:
    st.success("Low Risk: System stable")

#sidebar controls
st.sidebar.header("⚙️ Controls")
capacity = st.sidebar.slider("Hospital Capacity", 500, 5000, 2000)
increase = st.sidebar.slider("Simulate increase in admissions (%)", 0, 100, 0)


#visualization
st.subheader("📈 Admissions Forecast")
fig, ax = plt.subplots(figsize=(10,5))

# historical
ax.plot(df['date'], df['admissions_7day'], label="Historical")

# future
future_dates = pd.date_range(df['date'].iloc[-1], periods=future_days, freq='D')
ax.plot(future_dates, adjusted_predictions, label="Forecast")

# capacity line
ax.axhline(capacity, linestyle='--', label="Capacity")
ax.legend()
ax.set_xlabel("Date")
ax.set_ylabel("Admissions")
st.pyplot(fig)

#recommendations
st.subheader("🧠 Recommendation")
st.info(recommendation(risk))

#results
st.subheader("Forecast")
st.write(f"Predicted admissions (next {future_days} days):")
st.write(predictions)
