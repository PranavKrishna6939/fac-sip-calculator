import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date
from streamlit_extras.app_logo import add_logo

st.title(":green[SIP] Calculator :chart_with_upwards_trend:")
#add_logo("http://placekitten.com/120/120")
#st.divider()

# Remove Streamlit menu and footer
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# Sliders for input
monthly_investment = st.slider("Monthly Investment Amount (₹)", min_value=500, max_value=50000, value=2000, step=500)
investment_period = st.slider("Investment Period (Years)", min_value=2, max_value=30, value=4, step=1)
expected_return_rate = st.slider("Expected Annual Return Rate (%)", min_value=6.0, max_value=25.0, value=12.0, step=0.1)

# Calculate SIP returns
def calculate_sip_returns(monthly_investment, investment_period, expected_return_rate):
    months = investment_period * 12
    monthly_rate = (expected_return_rate / 100) / 12
    
    invested_amount = monthly_investment * months
    future_value = monthly_investment * ((((1 + monthly_rate) ** months) - 1) / monthly_rate) * (1 + monthly_rate)
    
    return invested_amount, future_value

# Calculate button
if st.button("Calculate"):
    invested_amount, future_value = calculate_sip_returns(monthly_investment, investment_period, expected_return_rate)
    
    # Display results
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Investment", f"₹{invested_amount:,.0f}")
    col2.metric("Expected Returns", f"₹{future_value - invested_amount:,.0f}")
    col3.metric("Total Value", f"₹{future_value:,.0f}")
       
    # Create DataFrame for plotting
    months = np.arange(1, investment_period * 12 + 1)
    invested_values = monthly_investment * months
    future_values = [calculate_sip_returns(monthly_investment, m/12, expected_return_rate)[1] for m in months]
    
    start_date = date.today()
    df = pd.DataFrame({
        'Month': pd.date_range(start=start_date, periods=len(months), freq='M'),
        'Invested Amount': invested_values,
        'Future Value': future_values
    })
    
    # Create Altair chart
    brush = alt.selection_interval(encodings=["x"])
    
    base = alt.Chart(df).encode(
        x='Month:T',
        y=alt.Y('Amount:Q', axis=alt.Axis(title='Amount (₹)', format=',.0f'))
    ).properties(
        width=600,
        height=400
    )

    lines = base.mark_line().encode(
        color=alt.Color('Variable:N', scale=alt.Scale(domain=['Invested Amount', 'Future Value'],
                                                      range=['#1f77b4', '#2ca02c']))
    ).transform_fold(
        ['Invested Amount', 'Future Value'],
        as_=['Variable', 'Amount']
    )

    points = lines.mark_point().encode(
        opacity=alt.condition(brush, alt.value(1), alt.value(0.2))
    ).add_selection(brush)

    chart = (lines + points).properties(
        title='SIP Growth Over Time'
    ).interactive()

    # Display the Altair chart with Streamlit theme
    st.altair_chart(chart, theme="streamlit", use_container_width=True)
    
    # Create yearly breakdown data
    yearly_data = df[df.index % 12 == 0].copy()
    yearly_data['Year'] = yearly_data.index // 12 + 1
    yearly_data = yearly_data[['Year', 'Invested Amount', 'Future Value']]
    yearly_data = yearly_data.melt('Year', var_name='Category', value_name='Amount')

    # Create Altair chart for bar plot
    click = alt.selection_multi(encodings=['color'])

    bars = alt.Chart(yearly_data).mark_bar().encode(
        x='Year:O',
        y='Amount:Q',
        color=alt.condition(click, 'Category:N', alt.value('lightgray')),
        tooltip=['Year', 'Category', 'Amount']
    ).properties(
        width=600,
        height=400,
        title='Yearly Breakdown'
    ).add_selection(click)

    # Display the bar chart
    st.altair_chart(bars, theme="streamlit", use_container_width=True)

#st.info("Note: This calculator assumes a constant rate of return. Actual returns may vary based on market conditions.")