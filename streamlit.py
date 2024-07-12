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

# Sliders for input
monthly_investment = st.slider("Monthly Investment Amount (₹)", min_value=500, max_value=50000, value=2000, step=500)
investment_period = st.slider("Investment Period (Years)", min_value=2, max_value=30, value=4, step=1)
expected_return_rate = st.slider("Expected Annual Return Rate (%)", min_value=8.0, max_value=25.0, value=15.0, step=0.1)
adjust_for_inflation = st.checkbox("Adjust for Inflation (6% annually)")

# Calculate SIP returns with or without inflation adjustment
def calculate_sip_returns(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation):
    months = investment_period * 12
    monthly_rate = (expected_return_rate / 100) / 12
    
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        inflation_adjusted_rate = expected_return_rate - 5.0
        monthly_rate = (inflation_adjusted_rate / 100) / 12
    
    invested_amount = monthly_investment * months
    future_value = monthly_investment * ((((1 + monthly_rate) ** months) - 1) / monthly_rate) * (1 + monthly_rate)
    
    return invested_amount, future_value

# Calculate button
if st.button("Calculate", use_container_width=True):
    invested_amount, future_value = calculate_sip_returns(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)
    
    # Display results
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investment", f"₹{invested_amount:,.0f}")
    col2.metric("Expected Returns", f"₹{future_value - invested_amount:,.0f}")
    col3.metric("Total Value", f"₹{future_value:,.0f}")
       
    # Create DataFrame for plotting
    months = np.arange(1, investment_period * 12 + 1)
    invested_values = monthly_investment * months
    future_values = [calculate_sip_returns(monthly_investment, m/12, expected_return_rate, adjust_for_inflation)[1] for m in months]
    
    start_date = date.today()
    df = pd.DataFrame({
        'Month': pd.date_range(start=start_date, periods=len(months), freq='M'),
        'Invested Amount': invested_values,
        'Future Value': future_values
    })
    
    # Create Plotly figure for line chart
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df['Month'], y=df['Invested Amount'], name='Invested Amount', line=dict(color='#1f77b4')))
    fig1.add_trace(go.Scatter(x=df['Month'], y=df['Future Value'], name='Future Value', line=dict(color='#2ca02c')))
    
    fig1.update_layout(
        title='SIP Growth Over Time',
        xaxis_title='Month',
        yaxis_title='Amount (₹)',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Display the Plotly line chart
    st.plotly_chart(fig1, use_container_width=True)
    
    # Create yearly breakdown data
    yearly_data = df[df.index % 12 == 0].copy()
    yearly_data['Year'] = yearly_data.index // 12 + 1
    
    # Create Plotly figure for bar chart
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=yearly_data['Year'], y=yearly_data['Invested Amount'], name='Invested Amount', marker_color='#1f77b4'))
    fig2.add_trace(go.Bar(x=yearly_data['Year'], y=yearly_data['Future Value'], name='Future Value', marker_color='#2ca02c'))
    
    fig2.update_layout(
        title='Yearly Breakdown',
        xaxis_title='Year',
        yaxis_title='Amount (₹)',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode='group'
    )
    
    # Display the Plotly bar chart
    st.plotly_chart(fig2, use_container_width=True)
