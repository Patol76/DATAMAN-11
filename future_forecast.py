import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from keras.models import load_model  # type: ignore
import yfinance as yf
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler

def future_forecast_page():
    st.title("📉 Stock Price Prediction")

    # User input for stock ID
    stock = st.text_input("Enter the Stock ID", "GOOG")

    # Check if stock symbol is provided
    if not stock:
        st.error("Please enter a stock symbol.")
        return

    # Display a loading spinner while fetching data
    with st.spinner('Fetching data...'):
        # Define the date range for stock data (last 20 years)
        end = datetime.now()
        start = datetime(end.year - 20, end.month, end.day)

        # Fetch stock data
        try:
            google_data = yf.download(stock, start=start, end=end)
            if google_data.empty:
                st.error(f"No data found for stock symbol: {stock}")
                return
            st.subheader(f"Stock Data for {stock}")
            st.write(google_data)
        except Exception as e:
            st.error(f"Error fetching data for {stock}: {e}")
            return  # Exit the function if data fetch fails

        # Load the model
        try:
            model = load_model("Latest_stock_price_model.keras")
        except Exception as e:
            st.error(f"Error loading the model: {e}")
            return  # Exit the function if model loading fails

        # Prepare data for predictions
        if len(google_data) < 100:
            st.error("Not enough data to make predictions.")
            return

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(google_data[['Close']])

        # Create sequences for prediction
        x_data, y_data = [], []
        for i in range(100, len(scaled_data)):
            x_data.append(scaled_data[i-100:i])
            y_data.append(scaled_data[i])
        
        x_data, y_data = np.array(x_data), np.array(y_data)
        
        # Predict and inverse transform
        predictions = model.predict(x_data)
        inv_pre = scaler.inverse_transform(predictions)
        inv_y_test = scaler.inverse_transform(y_data)

        ploting_data = pd.DataFrame({
            'original_test_data': inv_y_test.reshape(-1),
            'predictions': inv_pre.reshape(-1)
        }, index=google_data.index[100:])

        st.subheader("Original values vs Predicted values")
        st.write(ploting_data)

        # Weekly aggregation
        weekly_data = ploting_data.resample('W').agg({
            'original_test_data': 'mean',
            'predictions': 'mean'
        })

        st.subheader("Weekly Aggregated Data")
        st.write(weekly_data)

        # Plot original vs predicted values as a line chart
        st.subheader('Original Close Price vs Predicted Close Price (Line Chart)')
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=google_data.index, y=google_data['Close'], mode='lines', name='Original Data', line=dict(color='blue')))
        fig_line.add_trace(go.Scatter(x=ploting_data.index, y=ploting_data['original_test_data'], mode='lines', name='Original Test Data', line=dict(color='green')))
        fig_line.add_trace(go.Scatter(x=ploting_data.index, y=ploting_data['predictions'], mode='lines', name='Predicted Test Data', line=dict(color='blue', dash='dash')))
        fig_line.update_layout(title='Original Close Price vs Predicted Close Price (Line Chart)', xaxis_title='Date', yaxis_title='Price', template='plotly_dark')
        st.plotly_chart(fig_line)

        # Plot original vs predicted values as a column chart
        st.subheader('Original Close Price vs Predicted Close Price (Column Chart)')
        fig_col = go.Figure()
        fig_col.add_trace(go.Bar(x=ploting_data.index, y=ploting_data['original_test_data'], name='Original Test Data', marker_color='green'))
        fig_col.add_trace(go.Bar(x=ploting_data.index, y=ploting_data['predictions'], name='Predicted Test Data', marker_color='blue'))
        fig_col.update_layout(title='Original Close Price vs Predicted Close Price (Column Chart)', xaxis_title='Date', yaxis_title='Price', barmode='group', template='plotly_dark')
        st.plotly_chart(fig_col)

        # Plot weekly aggregated data as a column chart
        st.subheader('Weekly Aggregated Data (Column Chart)')
        fig_weekly_col = go.Figure()
        fig_weekly_col.add_trace(go.Bar(x=weekly_data.index, y=weekly_data['original_test_data'], name='Weekly Aggregated Original Data', marker_color='green'))
        fig_weekly_col.add_trace(go.Bar(x=weekly_data.index, y=weekly_data['predictions'], name='Weekly Aggregated Predicted Data', marker_color='blue'))
        fig_weekly_col.update_layout(title='Weekly Aggregated Data (Column Chart)', xaxis_title='Date', yaxis_title='Price', barmode='group', template='plotly_dark')
        st.plotly_chart(fig_weekly_col)
