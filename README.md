# Options Sentiment Analyzer  A sleek, real-time Streamlit web app that pulls free options chain data via yfinance, calculates key sentiment metrics (Put/Call ratios, ATM volume skew, implied move), and uses Groq’s blazing-fast LLMs to deliver professional-grade analysis and trading ideas.App Screenshot
 FeaturesLive Options Data — Fetches full options chain for any ticker (SPY, AAPL, TSLA, etc.)
Key Sentiment MetricsPut/Call Volume & Open Interest ratios
ATM volume skew (puts vs calls near current price)
Estimated implied move from ATM straddle

Groq-Powered Analysis — Choose from top models (Llama 3.3 70B, GPT-OSS 120B, etc.) for concise, expert-level commentary
Beautiful Visuals — Interactive Plotly volume chart + sortable strike table
Mobile-Friendly — Wide layout with clean Streamlit UI

 Quick Start1. Clone the repobash

git clone https://github.com/Pyrodark/options-sentiment-app.git
cd options-sentiment-analyzer

2. Install dependenciesbash

pip install -r requirements.txt

3. Set up environment variablesCreate a .env file in the root:env

GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

Get your free API key at console.groq.com
4. Run the appbash

streamlit run app.py

 Requirements (requirements.txt)txt

streamlit
yfinance
pandas
plotly
groq
python-dotenv

 How It WorksUser selects ticker + expiration date
App pulls options chain via yfinance
Calculates:Put/Call volume & OI ratios
ATM volume skew
Approximate implied move from ATM straddle

Sends structured data to Groq LLM with a precise prompt
Displays metrics, charts, and LLM explanation

Example UsageSPY (nearest expiration) → Great for broad market sentiment
AAPL or NVDA before earnings → See implied move & skew
TSLA → High-volume meme stock behavior

 ConfigurationVariable
Description
Default
GROQ_API_KEY
Groq API key
Required
ticker
Default symbol
SPY
Model
LLM model selection
Llama 3.3 70B

 Supported Groq ModelsLlama 3.3 70B Versatile – Best reasoning (default)
GPT-OSS 120B – Highest quality
GPT-OSS 20B – Fast
Llama 3.1 8B Instant – Very fast

 Limitations & NotesRequires market hours or recent after-hours data for accurate pricing
Free yfinance data can occasionally be delayed or incomplete
Groq API usage is rate-limited on free tier
Best used as a sentiment gauge, not financial advice

 ContributingContributions are welcome! Feel free to:Add new metrics (IV rank, gamma exposure, etc.)
Improve LLM prompts
Add export to CSV/PDF
Support multiple expirations view

Just open a PR. LicenseMIT License — feel free to use, modify, and deploy commercially.Made with  for options traders who love data + AIStar the repo if you find it useful! 

