import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Options Sentiment Analyzer", layout="wide")
st.title("📊 Options Chain Sentiment Analyzer")
st.markdown("Pulls free data via **yfinance** • Analyzes put/call + volume skew • Groq LLM explains implied move")

# Sidebar
ticker = st.sidebar.text_input("Ticker Symbol", value="SPY", max_chars=10).upper()
expiry_date = st.sidebar.date_input("Options Expiration", value=None)

# Updated models - using current Groq production models
model_options = {
    "Llama 3.3 70B Versatile (strong reasoning)": "llama-3.3-70b-versatile",
    "GPT-OSS 120B (best quality)": "openai/gpt-oss-120b",
    "GPT-OSS 20B (fast)": "openai/gpt-oss-20b",
    "Llama 3.1 8B Instant (very fast)": "llama-3.1-8b-instant"
}
model = st.sidebar.selectbox("LLM Model", options=list(model_options.keys()), index=0)
selected_model_id = model_options[model]

if st.sidebar.button("Analyze", type="primary"):
    with st.spinner("Fetching options chain..."):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get options dates
            if not expiry_date:
                expirations = stock.options
                if not expirations:
                    st.error("No options data available.")
                    st.stop()
                expiry_str = expirations[0]  # nearest
            else:
                expiry_str = expiry_date.strftime("%Y-%m-%d")
            
            # Fetch chain
            opt = stock.option_chain(expiry_str)
            calls = opt.calls
            puts = opt.puts
            
            # Basic metrics
            total_call_vol = calls['volume'].sum() or 0
            total_put_vol = puts['volume'].sum() or 0
            total_call_oi = calls['openInterest'].sum() or 0
            total_put_oi = puts['openInterest'].sum() or 0
            
            put_call_vol_ratio = total_put_vol / total_call_vol if total_call_vol > 0 else 0
            put_call_oi_ratio = total_put_oi / total_call_oi if total_call_oi > 0 else 0
            
            # Volume skew (ATM-ish)
            atm_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            if not atm_price:
                st.error("Could not determine current price.")
                st.stop()
                
            calls_atm = calls[abs(calls['strike'] - atm_price) < atm_price * 0.02]
            puts_atm = puts[abs(puts['strike'] - atm_price) < atm_price * 0.02]
            
            skew = puts_atm['volume'].sum() / (calls_atm['volume'].sum() + 1)
            
            # Implied move (approx from ATM straddle)
            try:
                atm_call_idx = (calls['strike'] - atm_price).abs().argsort()[:1]
                atm_put_idx = (puts['strike'] - atm_price).abs().argsort()[:1]
                atm_call = calls.iloc[atm_call_idx]
                atm_put = puts.iloc[atm_put_idx]
                straddle = float(atm_call['lastPrice'].iloc[0] + atm_put['lastPrice'].iloc[0])
                implied_move_pct = (straddle / atm_price) * 100
            except:
                implied_move_pct = None
            
            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Put/Call Volume Ratio", f"{put_call_vol_ratio:.2f}", 
                       "Bearish > 1.0" if put_call_vol_ratio > 1 else "Bullish")
            col2.metric("Put/Call OI Ratio", f"{put_call_oi_ratio:.2f}")
            col3.metric("Volume Skew (ATM)", f"{skew:.2f}x puts")
            col4.metric("Est. Implied Move", f"{implied_move_pct:.1f}%" if implied_move_pct else "N/A")
            
            st.subheader(f"{ticker} @ ${atm_price:.2f} | Expiration: {expiry_str}")
            
            # Charts
            tab1, tab2 = st.tabs(["Volume & OI", "Strike Table"])
            
            with tab1:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=calls['strike'], y=calls['volume'], name='Call Volume', marker_color='green'))
                fig.add_trace(go.Bar(x=puts['strike'], y=puts['volume'], name='Put Volume', marker_color='red'))
                fig.update_layout(barmode='overlay', title="Volume by Strike", xaxis_title="Strike", yaxis_title="Volume")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.dataframe(
                    pd.concat([
                        calls[['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']].assign(type='CALL'),
                        puts[['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']].assign(type='PUT')
                    ]).sort_values('strike'),
                    use_container_width=True,
                    hide_index=True
                )
            
            # LLM Analysis
            st.subheader("🧠 Groq LLM Sentiment & Implied Move Explanation")
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            
            prompt = f"""You are an options trading expert. Analyze this data for {ticker} expiring {expiry_str}:

Current price: ${atm_price:.2f}
Put/Call Volume Ratio: {put_call_vol_ratio:.2f}
Put/Call OI Ratio: {put_call_oi_ratio:.2f}
ATM Volume Skew: {skew:.2f}x toward puts
Estimated implied move: ±{implied_move_pct:.1f}% (from straddle)

Provide a concise 3-4 paragraph explanation:
1. Overall sentiment (bullish/bearish/neutral)
2. Key insights from ratios and skew
3. What the implied move suggests for earnings/volatility
4. One clear trading idea (if any)"""

            response = client.chat.completions.create(
                model=selected_model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=800,
                stream=False
            )
            
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Tips: Try SPY, AAPL, TSLA. Market must be open or have recent data. Make sure your GROQ_API_KEY is set in .env")
