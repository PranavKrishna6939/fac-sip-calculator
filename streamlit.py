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
monthly_investment = st.slider("Investment Amount (₹)", min_value=500, max_value=50000, value=2000, step=500)
investment_period = st.slider("Investment Period (Years)", min_value=2, max_value=30, value=4, step=1)
expected_return_rate = st.slider("Expected Annual Return Rate (%)", min_value=6.0, max_value=25.0, value=12.0, step=0.1)
adjust_for_inflation = st.checkbox("Adjust for Inflation (5% annually)")

# Radio buttons for investment type
investment_type = st.radio("Choose Investment Type", ["Monthly", "Quarterly", "One-time"])

# Calculate SIP returns for Monthly Investment
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

# Calculate SIP returns for Quarterly Investment
def calculate_sip_quarterly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation):
    quarters = investment_period * 4
    quarterly_rate = (expected_return_rate / 100) / 4
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        inflation_adjusted_rate = expected_return_rate - 5.0
        quarterly_rate = (inflation_adjusted_rate / 100) / 4
    invested_amount = monthly_investment * quarters
    future_value = monthly_investment  * ((((1 + quarterly_rate) ** quarters) - 1) / quarterly_rate) * (1 + quarterly_rate)
    
    return invested_amount, future_value


# Calculate SIP returns for One-time Investment
def calculate_sip_one_time(one_time_investment, investment_period, expected_return_rate, adjust_for_inflation):
    annual_rate = expected_return_rate / 100
    
    if adjust_for_inflation:
        # Adjust expected return rate for inflation (5% annually)
        annual_rate -= 0.05
    
    future_value = one_time_investment * (1 + annual_rate) ** investment_period
    
    return one_time_investment, future_value


# Calculate button
if st.button("Calculate"):
    if investment_type == "Monthly":
        invested_amount, future_value = calculate_sip_monthly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)
    elif investment_type == "Quarterly":
        invested_amount, future_value = calculate_sip_quarterly(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)
    elif investment_type == "One-time":
        invested_amount, future_value = calculate_sip_one_time(monthly_investment, investment_period, expected_return_rate, adjust_for_inflation)

    
    # Display results
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investment", f"₹{invested_amount:,.0f}")
    col2.metric("Expected Returns", f"₹{future_value - invested_amount:,.0f}")
    col3.metric("Total Value", f"₹{future_value:,.0f}")
       
    # Create DataFrame for plotting
    periods_per_year = 12 if investment_type == "Monthly" else 4 if investment_type == "Quarterly" else 1
    if investment_type == "Monthly":
        months = np.arange(1, investment_period * periods_per_year + 1)
        invested_values = [monthly_investment * m / periods_per_year for m in months]
        future_values = [calculate_sip_monthly(monthly_investment, m / periods_per_year, expected_return_rate, adjust_for_inflation)[1] for m in months]
    elif investment_type == "Quarterly":
        quarters = np.arange(1, investment_period * periods_per_year + 1)
        invested_values = [monthly_investment * 3 * q / periods_per_year for q in quarters]
        future_values = [calculate_sip_quarterly(monthly_investment, q / periods_per_year, expected_return_rate, adjust_for_inflation)[1] for q in quarters]
    elif investment_type == "One-time":
        years = np.arange(1, investment_period + 1)
        invested_values = [monthly_investment * 12 * y for y in years]
        future_values = [calculate_sip_one_time(monthly_investment, y, expected_return_rate, adjust_for_inflation)[1] for y in years]

    
    start_date = date.today()
    df = pd.DataFrame({
        'Month': pd.date_range(start=start_date, periods=len(invested_values), freq='M'),
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
    if investment_type == "Monthly":
        yearly_data = df[df.index % periods_per_year == 0].copy()
    elif investment_type == "Quarterly":
        yearly_data = df[df.index % (periods_per_year * 3) == 0].copy()
    elif investment_type == "One-time":
        yearly_data = df.copy()
    if investment_type == "One-time":
        yearly_data['Year'] = pd.DatetimeIndex(yearly_data['Month']).year
    else:
        yearly_data['Year'] = yearly_data.index // periods_per_year + 1
    yearly_data = yearly_data[['Year', 'Invested Amount', 'Future Value']]
    yearly_data = yearly_data.melt('Year', var_name='Category', value_name='Amount')

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

#st.info("Note: This calculator assumes a constant rate of return. Actual returns may vary based on market conditions.")
