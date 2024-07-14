import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date

st.set_page_config(layout="wide")
st.title(":green[SIP] Calculator :chart_with_upwards_trend:")

# Remove Streamlit menu and footer
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {
        max-width: 100%;
        padding: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to calculate SIP returns for Monthly Investment
def calculate_sip_monthly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation):
    months = investment_period * 12
    monthly_rate = (expected_return_rate / 100) / 12
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        inflation_adjusted_rate = expected_return_rate - 5.0
        monthly_rate = (inflation_adjusted_rate / 100) / 12
    invested_amount = monthly_investment * months
    future_value = monthly_investment * ((((1 + monthly_rate) ** months) - 1) / monthly_rate) * (1 + monthly_rate)
    return invested_amount, future_value

# Function to calculate SIP returns for Quarterly Investment
def calculate_sip_quarterly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation):
    quarters = investment_period * 4
    quarterly_rate = (expected_return_rate / 100) / 4
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        inflation_adjusted_rate = expected_return_rate - 5.0
        quarterly_rate = (inflation_adjusted_rate / 100) / 4
    invested_amount = monthly_investment * quarters
    future_value = monthly_investment * ((((1 + quarterly_rate) ** quarters) - 1) / quarterly_rate) * (1 + quarterly_rate)
    return invested_amount, future_value

# Function to calculate SIP returns for One-time Investment
def calculate_sip_one_time(one_time_investment, investment_period, expected_return_rate, adjust_for_inflation):
    annual_rate = expected_return_rate / 100
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        annual_rate -= 0.05
    future_value = one_time_investment * (1 + annual_rate) ** investment_period
    return one_time_investment, future_value

# Gather multiple investment plans
st.subheader("Compare Multiple Investment Plans")
num_plans = st.number_input("Number of Plans", min_value=1, max_value=5, value=1, step=1)

plans = []
for i in range(num_plans):
    st.subheader(f"Plan {i+1}")
    monthly_investment = st.slider(f"Investment Amount (₹) - Plan {i+1}", min_value=500, max_value=50000, value=2000, step=500)
    investment_period = st.slider(f"Investment Period (Years) - Plan {i+1}", min_value=2, max_value=30, value=4, step=1)
    expected_return_rate = st.slider(f"Expected Annual Return Rate (%) - Plan {i+1}", min_value=6.0, max_value=25.0, value=12.0, step=0.1)
    adjust_for_inflation = st.checkbox(f"Adjust for Inflation (5% annually) - Plan {i+1}", key=f"inflation_{i}")
    investment_type = st.radio(f"Choose Investment Type - Plan {i+1}", ["Monthly", "Quarterly", "One-time"], key=f"type_{i}")
    plans.append((monthly_investment, investment_period, expected_return_rate, adjust_for_inflation, investment_type))

# Calculate and plot results
if st.button("Calculate"):
    fig1 = go.Figure()
    fig2 = go.Figure()
    colors = ['#1f77b4','#9467bd',  '#2ca02c', '#d62728',  '#ff7f0e']

    for i, plan in enumerate(plans):
        monthly_investment, investment_period, expected_return_rate, adjust_for_inflation, investment_type = plan
        if investment_type == "Monthly":
            invested_amount, future_value = calculate_sip_monthly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)
            months = np.arange(1, investment_period * 12 + 1)
            invested_values = [monthly_investment * m for m in months]
            future_values = [calculate_sip_monthly(monthly_investment, m / 12, expected_return_rate, adjust_for_inflation)[1] for m in months]
        elif investment_type == "Quarterly":
            invested_amount, future_value = calculate_sip_quarterly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)
            quarters = np.arange(1, investment_period * 4 + 1)
            invested_values = [monthly_investment * 3 * q for q in quarters]
            future_values = [calculate_sip_quarterly(monthly_investment * 3, q / 4, expected_return_rate, adjust_for_inflation)[1] for q in quarters]
        elif investment_type == "One-time":
            invested_amount, future_value = calculate_sip_one_time(monthly_investment * 12, investment_period, expected_return_rate, adjust_for_inflation)
            years = np.arange(1, investment_period + 1)
            invested_values = [monthly_investment * 12] * len(years)
            future_values = [calculate_sip_one_time(monthly_investment * 12, y, expected_return_rate, adjust_for_inflation)[1] for y in years]

        st.subheader(f"Plan {i + 1}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Investment", f"₹{invested_amount:,.0f}")
        col2.metric("Expected Returns", f"₹{future_value - invested_amount:,.0f}")
        col3.metric("Total Value", f"₹{future_value:,.0f}")

        start_date = date.today()
        df = pd.DataFrame({
            'Month': pd.date_range(start=start_date, periods=len(invested_values), freq='M'),
            'Invested Amount': invested_values,
            'Future Value': future_values
        })

        # Add traces to the plot
        fig1.add_trace(go.Scatter(x=df['Month'], y=df['Invested Amount'], name=f'Invested Amount - Plan {i+1}', line=dict(color=colors[i], dash='dash')))
        fig1.add_trace(go.Scatter(x=df['Month'], y=df['Future Value'], name=f'Future Value - Plan {i+1}', line=dict(color=colors[i])))
        
        # Yearly breakdown
        yearly_data = df.resample('Y', on='Month').last().reset_index() if investment_type in ["Monthly", "Quarterly"] else df.copy()
        yearly_data['Year'] = yearly_data['Month'].dt.year
        
        fig2.add_trace(go.Bar(
            x=yearly_data['Year'], 
            y=yearly_data['Invested Amount'], 
            name=f'Invested Amount - Plan {i+1}', 
            marker_color=colors[i]
        ))
        fig2.add_trace(go.Bar(
            x=yearly_data['Year'], 
            y=yearly_data['Future Value'], 
            name=f'Future Value - Plan {i+1}', 
            marker_color=colors[i]
        ))

    # Update layout of the plots
    st.write("")
    st.write("")
    st.subheader("SIP Growth Over Time")
    
    fig1.update_layout(
        
        xaxis_title='Month',
        yaxis_title='Amount (₹)',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig1, use_container_width=True)
    
   
    st.subheader("**Yearly Breakdown**")
    
    fig2.update_layout(
        
        xaxis_title='Year',
        yaxis_title='Amount (₹)',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group'
    )
    st.plotly_chart(fig2, use_container_width=True)

st.info("Note: This calculator assumes a constant rate of return. Actual returns may vary based on market conditions.")
