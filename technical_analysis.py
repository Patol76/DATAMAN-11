import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import plotly.graph_objs as go

# Function to load data
def load_data(stock, period):
    df = yf.Ticker(stock).history(period=period)[['Open', 'High', 'Low', 'Close', 'Volume']]
    df = df.reset_index()
    df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
    df['time'] = df['time'].dt.strftime('%Y-%m-%d')
    
    # Calculate technical indicators
    df['EMA_20'] = ta.ema(df['close'], length=20)
    df['EMA_200'] = ta.ema(df['close'], length=200)
    df['RSI_14'] = ta.rsi(df['close'], length=14)
    df['ADX_14'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']
    df['ATR_14'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    return df

# Functions to get emoji based on values
def get_returns_emoji(ret_val):
    return ":white_check_mark:" if ret_val >= 0 else ":red_circle:"

def get_ema_emoji(ltp, ema):
    return ":white_check_mark:" if ltp >= ema else ":red_circle:"

def get_rsi_emoji(rsi):
    return ":white_check_mark:" if 30 < rsi < 70 else ":red_circle:"

def get_adx_emoji(adx):
    return ":white_check_mark:" if adx > 25 else ":red_circle:"

# Function to create the candlestick chart
def create_chart(df, stock):
    candlestick_chart = go.Figure(data=[go.Candlestick(x=df['time'],
                                                       open=df['open'],
                                                       high=df['high'],
                                                       low=df['low'],
                                                       close=df['close'],
                                                       name='Candlestick')])
    
    if 'EMA_20' in df.columns:
        candlestick_chart.add_trace(go.Scatter(x=df['time'],
                                               y=df['EMA_20'],
                                               mode='lines',
                                               name='EMA 20',
                                               line=dict(color='blue')))
    
    if 'EMA_200' in df.columns:
        candlestick_chart.add_trace(go.Scatter(x=df['time'],
                                               y=df['EMA_200'],
                                               mode='lines',
                                               name='EMA 200',
                                               line=dict(color='red')))
    
    candlestick_chart.update_layout(title=f'{stock} Historical Candlestick Chart',
                                    xaxis_title='Date',
                                    yaxis_title='Price',
                                    xaxis_rangeslider_visible=True)
    return candlestick_chart

# Main function to render the page
def technical_analysis_page():
    st.subheader("Tech Nuggets' Stock Technical Analysis Dashboard")
    
    stock = st.sidebar.text_input("Stock Symbol e.g. AAPL", "AAPL")
    timeframe_option = st.sidebar.selectbox("Timeframe?", ('1y', '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'))
    show_data = st.sidebar.checkbox(label="Show Data")
    show_chart = st.sidebar.checkbox(label="Show Chart")

    df = load_data(stock, timeframe_option)
    reversed_df = df.iloc[::-1]

    # Extract values
    row1_val = reversed_df.iloc[0]['close']
    ema20_val = reversed_df.iloc[0]['EMA_20']
    ema200_val = reversed_df.iloc[0]['EMA_200']
    rsi_val = reversed_df.iloc[0]['RSI_14']
    adx = reversed_df.iloc[0]['ADX_14']
    dmp = reversed_df.iloc[0].get('DMP_14', None)  # 'DMP_14' may not be available
    dmn = reversed_df.iloc[0].get('DMN_14', None)  # 'DMN_14' may not be available
    
    # Handle cases where not enough rows exist
    def safe_get_close_value(index):
        return reversed_df.iloc[index]['close'] if index < len(reversed_df) else row1_val

    row20_val = safe_get_close_value(20)
    row60_val = safe_get_close_value(60)
    row120_val = safe_get_close_value(120)
    row240_val = safe_get_close_value(240)

    # Return percentage calculation
    day20_ret_percent = (row1_val - row20_val) / row20_val * 100
    day60_ret_percent = (row1_val - row60_val) / row60_val * 100
    day120_ret_percent = (row1_val - row120_val) / row120_val * 100
    day240_ret_percent = (row1_val - row240_val) / row240_val * 100

    # Column wise display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Returns")
        st.markdown(f"- 1 MONTH : {round(day20_ret_percent, 2)}% {get_returns_emoji(round(day20_ret_percent, 2))}")
        st.markdown(f"- 3 MONTHS : {round(day60_ret_percent, 2)}% {get_returns_emoji(round(day60_ret_percent, 2))}")
        st.markdown(f"- 6 MONTHS : {round(day120_ret_percent, 2)}% {get_returns_emoji(round(day120_ret_percent, 2))}")
        st.markdown(f"- 12 MONTHS : {round(day240_ret_percent, 2)}% {get_returns_emoji(round(day240_ret_percent, 2))}")
    with col2:
        st.subheader("Momentum")
        st.markdown(f"- LTP : {round(row1_val, 2)}")
        st.markdown(f"- EMA20 : {round(ema20_val, 2)} {get_ema_emoji(round(row1_val, 2), round(ema20_val, 2))}")
        st.markdown(f"- EMA200 : {round(ema200_val, 2)} {get_ema_emoji(round(row1_val, 2), round(ema200_val, 2))}")
        st.markdown(f"- RSI : {round(rsi_val, 2)} {get_rsi_emoji(round(rsi_val, 2))}")
    with col3:
        st.subheader("Trend Strength")
        st.markdown(f"- ADX : {round(adx, 2)} {get_adx_emoji(round(adx, 2))}")
        st.markdown(f"- DMP : {round(dmp, 2) if dmp is not None else 'N/A'}")
        st.markdown(f"- DMN : {round(dmn, 2) if dmn is not None else 'N/A'}")

    if show_data:
        st.write(reversed_df)

    if show_chart:
        st.plotly_chart(create_chart(df, stock))
