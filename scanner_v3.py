"""
Trading Scanner Pro v3.4
- Kompakt PKScreener-inspireret design
- Forside: Market pulse, Buy kandidater, Top10 op/ned, Sektor overblik
- Scanner tab: Alle aktier kompakt
- 500+ aktier
- Råvarer, Børser, Sektorer
- Benchmark tab forbedret
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, time
import pytz
import json
import os

st.set_page_config(page_title="Trading Terminal Pro v3.6", page_icon="🟢",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Orbitron:wght@700;900&display=swap');

  /* ── BASE ── */
  .stApp,.main{background:#0a0a0a;color:#e0e0e0;font-family:'IBM Plex Mono',monospace;}
  section[data-testid="stSidebar"]{display:none!important;}
  [data-testid="collapsedControl"]{display:none!important;}
  .block-container{padding-top:0.3rem!important;padding-bottom:0!important;max-width:100%!important;}

  /* Hide Streamlit chrome */
  #MainMenu{visibility:hidden;}
  header[data-testid="stHeader"]{background:#000;height:0;min-height:0;padding:0;overflow:hidden;}
  footer{visibility:hidden;}
  .stDeployButton{display:none;}
  [data-testid="stToolbar"]{display:none;}
  .block-container{padding-top:0.5rem!important;padding-bottom:0!important;}
  div[data-testid="stDecoration"]{display:none;}
  h1{color:#ffffff!important;font-family:'Orbitron',monospace!important;font-size:1.1rem!important;letter-spacing:3px;margin:0!important;}
  h2,h3{color:#888!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.72rem!important;letter-spacing:2px;margin:3px 0!important;text-transform:uppercase;}
  p,li,label,.stMarkdown{color:#aaa!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.78rem!important;}

  /* ── METRICS ── */
  [data-testid="metric-container"]{background:#111;border:1px solid #222;padding:6px 10px;}
  [data-testid="metric-container"] label{color:#555!important;font-family:'IBM Plex Mono',monospace!important;font-size:0.58rem!important;text-transform:uppercase;letter-spacing:2px;}
  [data-testid="stMetricValue"]{color:#fff!important;font-family:'Orbitron',monospace!important;font-size:1.1rem!important;font-weight:700!important;}

  /* ── BUTTONS ── */
  .stButton button{background:#111;color:#00ff88;border:1px solid #333;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;text-transform:uppercase;padding:4px 12px;}
  .stButton button:hover{background:#00ff88;color:#000;border-color:#00ff88;}

  /* ── TABS ── */
  .stTabs [data-baseweb="tab-list"]{background:#000;border-bottom:1px solid #222;gap:0;}
  .stTabs [data-baseweb="tab"]{background:#000;color:#444;border:1px solid #1a1a1a;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;letter-spacing:1px;text-transform:uppercase;padding:5px 14px;}
  .stTabs [aria-selected="true"]{background:#00ff88!important;color:#000!important;font-weight:700!important;}

  /* ── INPUTS ── */
  .stSelectbox>div>div,.stMultiSelect>div>div,.stTextInput>div>div{background:#0d0d0d;border:1px solid #222;color:#ddd;font-family:'IBM Plex Mono',monospace;}
  hr{border-color:#1a1a1a;margin:6px 0;}
  ::-webkit-scrollbar{width:3px;height:3px;}
  ::-webkit-scrollbar-thumb{background:#333;}
  ::-webkit-scrollbar-track{background:#000;}
  .stDataFrame{border:1px solid #1e1e1e;}

  /* ── BLOOMBERG COMPONENTS ── */

  /* Header bar */
  .bb-header{background:#000;border-bottom:2px solid #00ff88;padding:6px 12px;display:flex;align-items:center;gap:16px;}
  .bb-title{color:#fff;font-family:'Orbitron',monospace;font-size:0.95rem;font-weight:900;letter-spacing:3px;}
  .bb-regime-on {color:#00ff88;font-family:'Orbitron',monospace;font-weight:700;font-size:0.8rem;border:1px solid #00ff88;padding:2px 10px;}
  .bb-regime-off{color:#ff3333;font-family:'Orbitron',monospace;font-weight:700;font-size:0.8rem;border:1px solid #ff3333;padding:2px 10px;}
  .bb-regime-neu{color:#ffaa00;font-family:'Orbitron',monospace;font-weight:700;font-size:0.8rem;border:1px solid #ffaa00;padding:2px 10px;}

  /* KPI strip */
  .kpi-strip{display:flex;gap:0;border-bottom:1px solid #1a1a1a;margin-bottom:8px;}
  .kpi-cell{flex:1;padding:5px 10px;border-right:1px solid #1a1a1a;background:#0d0d0d;}
  .kpi-cell:last-child{border-right:none;}
  .kpi-label{color:#555;font-size:0.58rem;text-transform:uppercase;letter-spacing:2px;font-family:'IBM Plex Mono',monospace;}
  .kpi-value{color:#fff;font-size:1.1rem;font-family:'Orbitron',monospace;font-weight:700;line-height:1.2;}
  .kpi-up{color:#00ff88;}
  .kpi-dn{color:#ff3333;}
  .kpi-neu{color:#ffaa00;}

  /* Panel */
  .bb-panel{background:#0d0d0d;border:1px solid #1e1e1e;margin-bottom:6px;}
  .bb-panel-hdr{background:#111;border-bottom:1px solid #1e1e1e;padding:3px 10px;font-family:'IBM Plex Mono',monospace;font-size:0.62rem;color:#555;text-transform:uppercase;letter-spacing:2px;display:flex;justify-content:space-between;}
  .bb-panel-hdr span{color:#00ff88;}

  /* Market row */
  .mkt-row{display:grid;grid-template-columns:72px 1fr 80px 70px 60px;gap:0;padding:2px 8px;border-bottom:1px solid #111;font-family:'IBM Plex Mono',monospace;font-size:0.74rem;align-items:center;}
  .mkt-row:hover{background:#141414;}
  .mkt-t{color:#fff;font-weight:600;}
  .mkt-n{color:#444;overflow:hidden;white-space:nowrap;font-size:0.68rem;}
  .mkt-p{color:#ccc;text-align:right;}
  .mkt-up{color:#00ff88;text-align:right;font-weight:600;}
  .mkt-dn{color:#ff3333;text-align:right;font-weight:600;}
  .mkt-neu{color:#666;text-align:right;}
  .mkt-grp{padding:2px 8px;background:#0a0a0a;font-family:'IBM Plex Mono',monospace;font-size:0.58rem;color:#333;text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid #111;}

  /* Signal blocks – Bloomberg style farveblokke */
  .sig-block{display:inline-block;padding:2px 8px;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;}
  .sig-buynow  {background:#00ff88;color:#000;}
  .sig-breakout{background:#00cc66;color:#000;}
  .sig-build   {background:#0066cc;color:#fff;}
  .sig-starter {background:#004499;color:#aad4ff;}
  .sig-extended{background:#cc8800;color:#000;}
  .sig-reduce  {background:#cc4400;color:#fff;}
  .sig-exit    {background:#cc0000;color:#fff;}
  .sig-watch   {background:#1a1a1a;color:#444;}

  /* Candidate row – Bloomberg style */
  .cand-row{display:grid;grid-template-columns:80px 130px 80px 55px 40px auto;gap:4px;padding:4px 8px;border-bottom:1px solid #111;font-family:'IBM Plex Mono',monospace;font-size:0.74rem;align-items:center;}
  .cand-row:hover{background:#141414;}
  .cand-t{color:#fff;font-weight:700;}
  .cand-n{color:#444;overflow:hidden;white-space:nowrap;font-size:0.67rem;}
  .cand-p{color:#ccc;text-align:right;}
  .cand-s{color:#fff;font-family:'Orbitron',monospace;font-size:0.7rem;text-align:right;font-weight:700;}

  /* Position row */
  .pos-row{display:grid;grid-template-columns:70px 110px 65px 65px 70px auto;gap:4px;padding:4px 8px;border-bottom:1px solid #111;font-family:'IBM Plex Mono',monospace;font-size:0.74rem;align-items:center;}
  .pos-row:hover{background:#141414;}

  /* Mover row */
  .mov-row{display:grid;grid-template-columns:72px 90px 75px auto auto;gap:4px;padding:3px 8px;border-bottom:1px solid #111;font-family:'IBM Plex Mono',monospace;font-size:0.72rem;align-items:center;}
  .mov-row:hover{background:#141414;}
  .mov-t-up{color:#00ff88;font-weight:700;}
  .mov-t-dn{color:#ff3333;font-weight:700;}
  .mov-sec{color:#333;font-size:0.64rem;}
  .mov-p{color:#999;text-align:right;}

  /* Sektor heatmap blokke */
  .sek-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:2px;margin-top:4px;}
  .sek-cell{padding:6px 8px;text-align:center;font-family:'IBM Plex Mono',monospace;}
  .sek-name{font-size:0.62rem;color:#999;text-transform:uppercase;letter-spacing:1px;}
  .sek-pct{font-size:0.9rem;font-weight:700;font-family:'Orbitron',monospace;margin-top:2px;}

  /* Trend badges */
  .tr-up {background:#003322;color:#00ff88;font-size:0.6rem;padding:1px 5px;font-family:'IBM Plex Mono',monospace;}
  .tr-dn {background:#220000;color:#ff3333;font-size:0.6rem;padding:1px 5px;font-family:'IBM Plex Mono',monospace;}
  .tr-mix{background:#1a1500;color:#ffaa00;font-size:0.6rem;padding:1px 5px;font-family:'IBM Plex Mono',monospace;}

  /* Sidebar */
  .sb-exch{display:flex;align-items:center;gap:6px;padding:2px 0;font-family:'IBM Plex Mono',monospace;font-size:0.7rem;border-bottom:1px solid #111;}
  .sb-open  {color:#00ff88;}
  .sb-closed{color:#ff3333;}
  .sb-pre   {color:#ffaa00;}

  /* Scanner table */
  .scan-row{display:grid;grid-template-columns:75px 120px 80px 55px 50px 50px 40px 50px 45px auto;gap:2px;padding:3px 6px;border-bottom:1px solid #0f0f0f;font-family:'IBM Plex Mono',monospace;font-size:0.71rem;align-items:center;}
  .scan-row:hover{background:#111;}
  .scan-hdr{background:#0a0a0a;color:#444;font-size:0.6rem;text-transform:uppercase;letter-spacing:1px;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
CONFIG = {
    'rsi_period': 14, 'sma_fast': 20, 'sma_mid': 60, 'sma_long': 200,
    'atr_fast': 5, 'atr_slow': 20, 'breakout_distance': 0.06,
    'squeeze_factor': 0.78, 'min_avg_vol': 200_000, 'min_dollar_vol': 8_000_000,
}
POSITIONS_FILE = 'positions.json'
WATCHLIST_FILE = 'watchlist.json'
CUSTOM_UNIVERSE_FILE = 'custom_universe.json'

EXCHANGES = {
    'NYSE':       {'tz':'America/New_York',  'open':time(9,30),'close':time(16,0), 'pre':time(4,0),  'flag':'🇺🇸'},
    'Copenhagen': {'tz':'Europe/Copenhagen', 'open':time(9,0), 'close':time(17,0), 'pre':time(8,30),'flag':'🇩🇰'},
    'Oslo':       {'tz':'Europe/Oslo',       'open':time(9,0), 'close':time(16,30),'pre':time(8,30),'flag':'🇳🇴'},
    'Stockholm':  {'tz':'Europe/Stockholm',  'open':time(9,0), 'close':time(17,30),'pre':time(8,30),'flag':'🇸🇪'},
    'Amsterdam':  {'tz':'Europe/Amsterdam',  'open':time(9,0), 'close':time(17,30),'pre':time(8,0), 'flag':'🇳🇱'},
    'Frankfurt':  {'tz':'Europe/Berlin',     'open':time(9,0), 'close':time(17,30),'pre':time(8,0), 'flag':'🇩🇪'},
    'London':     {'tz':'Europe/London',     'open':time(8,0), 'close':time(16,30),'pre':time(7,0), 'flag':'🇬🇧'},
    'Paris':      {'tz':'Europe/Paris',      'open':time(9,0), 'close':time(17,30),'pre':time(8,0), 'flag':'🇫🇷'},
    'Tokyo':      {'tz':'Asia/Tokyo',        'open':time(9,0), 'close':time(15,30),'pre':time(8,0), 'flag':'🇯🇵'},
    'HongKong':   {'tz':'Asia/Hong_Kong',    'open':time(9,30),'close':time(16,0), 'pre':time(9,0), 'flag':'🇭🇰'},
}

def get_exchange_status(info):
    tz=pytz.timezone(info['tz']); now=datetime.now(tz); t=now.time()
    if now.weekday()>=5: return 'LUKKET'
    if info['open']<=t<info['close']: return 'ÅBEN'
    if info['pre']<=t<info['open']:   return 'PRE'
    return 'LUKKET'

# ══════════════════════════════════════════════════════════════
# MARKET TICKERS
# ══════════════════════════════════════════════════════════════
MARKET_GROUPS = {
    '🇺🇸 US INDICES': [
        ('SPY',  'S&P 500'),
        ('QQQ',  'Nasdaq 100'),
        ('IWM',  'Russell 2000'),
        ('DIA',  'Dow Jones'),
        ('^VIX', 'VIX Fear'),
    ],
    '🌍 EUROPA INDICES': [
        ('^OMXC25', 'C25 København'),
        ('^GDAXI',  'DAX (Tyskland)'),
        ('^FCHI',   'CAC 40 (Frankrig)'),
        ('^FTSE',   'FTSE 100 (UK)'),
        ('^AEX',    'AEX (Holland)'),
        ('^OMXS30', 'OMX30 (Sverige)'),
        ('^OSEBX',  'OBX (Norge)'),
    ],
    '🌏 ASIA & EM': [
        ('EEM',   'Emerg. Markets'),
        ('EWJ',   'Japan'),
        ('MCHI',  'China'),
        ('EWY',   'South Korea'),
        ('EWT',   'Taiwan'),
    ],
    '🛢️ ENERGI': [
        ('CL=F',  'WTI Olie'),
        ('BZ=F',  'Brent Olie'),
        ('NG=F',  'Naturgas'),
        ('RB=F',  'Benzin'),
        ('HO=F',  'Fyringsolie'),
    ],
    '🥇 METALLER': [
        ('GLD',   'Guld ETF'),
        ('GC=F',  'Guld Futures'),
        ('SLV',   'Sølv ETF'),
        ('HG=F',  'Kobber'),
        ('PL=F',  'Platin'),
    ],
    '🌾 RÅVARER': [
        ('ZW=F',  'Hvede'),
        ('ZC=F',  'Majs'),
        ('ZS=F',  'Soja'),
        ('CC=F',  'Kakao'),
        ('KC=F',  'Kaffe'),
    ],
    '💱 MAKRO': [
        ('UUP',   'US Dollar'),
        ('^TNX',  '10Y Rente'),
        ('^TYX',  '30Y Rente'),
        ('TIP',   'TIPS Inflation'),
        ('BITO',  'Bitcoin ETF'),
    ],
}

MACRO_TICKERS = [t for grp in MARKET_GROUPS.values() for t,_ in grp]
MACRO_NAMES   = {t: n for grp in MARKET_GROUPS.values() for t,n in grp}

# ══════════════════════════════════════════════════════════════
# SEKTOR ETFS TIL HEATMAP
# ══════════════════════════════════════════════════════════════
SECTOR_ETFS = [
    ('XLK',  'Tech'),
    ('XLF',  'Financials'),
    ('XLE',  'Energy'),
    ('XLV',  'Healthcare'),
    ('XLI',  'Industrials'),
    ('XLB',  'Materials'),
    ('XLY',  'Consumer Disc'),
    ('XLP',  'Consumer Staples'),
    ('XLU',  'Utilities'),
    ('XLRE', 'Real Estate'),
    ('XLC',  'Comm. Services'),
    ('SOXX', 'Semiconductors'),
    ('IBB',  'Biotech'),
    ('ITA',  'Defense'),
    ('ICLN', 'Clean Energy'),
]

# ══════════════════════════════════════════════════════════════
# FULDT UNIVERS – 500+ AKTIER
# ══════════════════════════════════════════════════════════════
UNIVERSE = [
    # ── USA TECH / AI ──────────────────────────────────────
    ('AAPL','Apple','Tech','US','CORE'),('MSFT','Microsoft','Tech','US','CORE'),
    ('GOOGL','Alphabet','Tech','US','CORE'),('META','Meta','Tech','US','CORE'),
    ('NVDA','NVIDIA','AI','US','CORE'),('AMD','AMD','AI','US','CORE'),
    ('AVGO','Broadcom','AI','US','CORE'),('MU','Micron','AI','US','CORE'),
    ('INTC','Intel','AI','US','CORE'),('QCOM','Qualcomm','AI','US','CORE'),
    ('ARM','ARM Holdings','AI','US','CORE'),('SMCI','Super Micro','AI','US','CORE'),
    ('PLTR','Palantir','AI','US','CORE'),('TSM','TSMC','AI','US','CORE'),
    ('ADBE','Adobe','Tech','US','CORE'),('CRM','Salesforce','Tech','US','CORE'),
    ('NOW','ServiceNow','Tech','US','CORE'),('SNOW','Snowflake','Tech','US','CORE'),
    ('DDOG','Datadog','Tech','US','CORE'),('NET','Cloudflare','Tech','US','CORE'),
    ('CRWD','CrowdStrike','Tech','US','CORE'),('PANW','Palo Alto','Tech','US','CORE'),
    ('ORCL','Oracle','Tech','US','CORE'),('UBER','Uber','Tech','US','CORE'),
    ('SHOP','Shopify','Tech','US','CORE'),('INTU','Intuit','Tech','US','CORE'),
    ('IONQ','IonQ','AI','US','CORE'),('RKLB','Rocket Lab','Momentum','US','CORE'),
    ('GTLB','GitLab','Tech','US','EXTENDED'),('PATH','UiPath','AI','US','EXTENDED'),
    ('AI','C3.ai','AI','US','EXTENDED'),('SOUN','SoundHound','AI','US','EXTENDED'),
    ('BBAI','BigBear.ai','AI','US','EXTENDED'),('RXRX','Recursion','AI','US','EXTENDED'),
    ('ANET','Arista Networks','Tech','US','CORE'),('MRVL','Marvell','AI','US','CORE'),
    ('MPWR','Monolithic Power','AI','US','CORE'),('ON','ON Semi','AI','US','CORE'),
    ('TXN','Texas Instruments','AI','US','CORE'),('AMAT','Applied Materials','AI','US','CORE'),
    ('LRCX','Lam Research','AI','US','CORE'),('KLAC','KLA Corp','AI','US','CORE'),
    ('ASML','ASML US','AI','US','CORE'),
    # ── USA FINANCIALS ─────────────────────────────────────
    ('JPM','JPMorgan','Financials','US','CORE'),('GS','Goldman Sachs','Financials','US','CORE'),
    ('MS','Morgan Stanley','Financials','US','CORE'),('BAC','Bank of America','Financials','US','CORE'),
    ('WFC','Wells Fargo','Financials','US','CORE'),('C','Citigroup','Financials','US','CORE'),
    ('V','Visa','Financials','US','CORE'),('MA','Mastercard','Financials','US','CORE'),
    ('AXP','Amex','Financials','US','CORE'),('BLK','BlackRock','Financials','US','CORE'),
    ('SCHW','Schwab','Financials','US','CORE'),('COF','Capital One','Financials','US','CORE'),
    ('COIN','Coinbase','Financials','US','EXTENDED'),('HOOD','Robinhood','Financials','US','EXTENDED'),
    ('SOFI','SoFi','Financials','US','EXTENDED'),('AFRM','Affirm','Financials','US','EXTENDED'),
    ('SQ','Block','Financials','US','EXTENDED'),('PYPL','PayPal','Financials','US','EXTENDED'),
    # ── USA ENERGY ─────────────────────────────────────────
    ('XOM','Exxon Mobil','Energy','US','CORE'),('CVX','Chevron','Energy','US','CORE'),
    ('COP','ConocoPhillips','Energy','US','CORE'),('DVN','Devon Energy','Energy','US','LIVE'),
    ('EOG','EOG Resources','Energy','US','CORE'),('OXY','Occidental','Energy','US','CORE'),
    ('FANG','Diamondback','Energy','US','CORE'),('PSX','Phillips 66','Energy','US','CORE'),
    ('VLO','Valero','Energy','US','CORE'),('MPC','Marathon Petroleum','Energy','US','CORE'),
    ('SLB','Schlumberger','Energy','US','CORE'),('HAL','Halliburton','Energy','US','CORE'),
    ('CCJ','Cameco','Energy','US','EXTENDED'),('ENPH','Enphase','Energy','US','EXTENDED'),
    ('FSLR','First Solar','Energy','US','EXTENDED'),('BE','Bloom Energy','Energy','US','EXTENDED'),
    ('PLUG','Plug Power','Energy','US','EXTENDED'),('DINO','HF Sinclair','Energy','US','EXTENDED'),
    # ── USA HEALTHCARE ─────────────────────────────────────
    ('LLY','Eli Lilly','Healthcare','US','CORE'),('UNH','UnitedHealth','Healthcare','US','CORE'),
    ('REGN','Regeneron','Healthcare','US','CORE'),('VRTX','Vertex','Healthcare','US','CORE'),
    ('JNJ','J&J','Healthcare','US','CORE'),('MRK','Merck','Healthcare','US','CORE'),
    ('ABBV','AbbVie','Healthcare','US','CORE'),('BMY','Bristol-Myers','Healthcare','US','CORE'),
    ('AMGN','Amgen','Healthcare','US','CORE'),('GILD','Gilead','Healthcare','US','CORE'),
    ('PFE','Pfizer','Healthcare','US','CORE'),('MRNA','Moderna','Healthcare','US','EXTENDED'),
    ('BNTX','BioNTech','Healthcare','US','EXTENDED'),('ISRG','Intuitive Surg','Healthcare','US','CORE'),
    ('TMO','Thermo Fisher','Healthcare','US','EXTENDED'),('DHR','Danaher','Healthcare','US','EXTENDED'),
    ('SYK','Stryker','Healthcare','US','EXTENDED'),('EW','Edwards Life','Healthcare','US','EXTENDED'),
    ('IDXX','IDEXX Labs','Healthcare','US','EXTENDED'),('GEHC','GE HealthCare','Healthcare','US','EXTENDED'),
    ('HUM','Humana','Healthcare','US','EXTENDED'),('ELV','Elevance','Healthcare','US','EXTENDED'),
    ('CI','Cigna','Healthcare','US','EXTENDED'),('CRSP','CRISPR','Healthcare','US','EXTENDED'),
    # ── USA CONSUMER ───────────────────────────────────────
    ('AMZN','Amazon','Consumer','US','CORE'),('TSLA','Tesla','Consumer','US','CORE'),
    ('NFLX','Netflix','Consumer','US','CORE'),('COST','Costco','Consumer','US','CORE'),
    ('HD','Home Depot','Consumer','US','CORE'),('WMT','Walmart','Consumer','US','CORE'),
    ('TGT','Target','Consumer','US','CORE'),('NKE','Nike','Consumer','US','CORE'),
    ('SBUX','Starbucks','Consumer','US','CORE'),('MCD','McDonalds','Consumer','US','CORE'),
    ('YUM','Yum Brands','Consumer','US','CORE'),('CMG','Chipotle','Consumer','US','CORE'),
    ('LULU','Lululemon','Consumer','US','EXTENDED'),('CELH','Celsius','Consumer','US','EXTENDED'),
    ('BYDDY','BYD','Consumer','US','EXTENDED'),('RIVN','Rivian','Consumer','US','EXTENDED'),
    ('LCID','Lucid','Consumer','US','EXTENDED'),('NIO','NIO','Consumer','US','EXTENDED'),
    ('DKNG','DraftKings','Consumer','US','EXTENDED'),('ABNB','Airbnb','Consumer','US','EXTENDED'),
    ('DASH','DoorDash','Consumer','US','EXTENDED'),('MELI','MercadoLibre','Consumer','US','EXTENDED'),
    ('RCL','Royal Caribbean','Consumer','US','EXTENDED'),('CCL','Carnival','Consumer','US','EXTENDED'),
    ('MGM','MGM Resorts','Consumer','US','EXTENDED'),('LVS','Las Vegas Sands','Consumer','US','EXTENDED'),
    ('WYNN','Wynn Resorts','Consumer','US','EXTENDED'),('ETSY','Etsy','Consumer','US','EXTENDED'),
    # ── USA INDUSTRIALS ────────────────────────────────────
    ('CAT','Caterpillar','Industrials','US','CORE'),('GE','GE Aerospace','Industrials','US','CORE'),
    ('RTX','RTX','Industrials','US','CORE'),('LMT','Lockheed Martin','Industrials','US','CORE'),
    ('NOC','Northrop Grumman','Industrials','US','CORE'),('BA','Boeing','Industrials','US','CORE'),
    ('HON','Honeywell','Industrials','US','CORE'),('GEV','GE Vernova','Industrials','US','CORE'),
    ('PWR','Quanta Services','Industrials','US','EXTENDED'),('ALSN','Allison Trans','Industrials','US','EXTENDED'),
    ('HPE','HP Enterprise','Tech','US','EXTENDED'),('DAL','Delta Air','Industrials','US','EXTENDED'),
    ('UAL','United Airlines','Industrials','US','EXTENDED'),('AAL','American Air','Industrials','US','EXTENDED'),
    ('UPS','UPS','Industrials','US','EXTENDED'),('FDX','FedEx','Industrials','US','EXTENDED'),
    ('DE','John Deere','Industrials','US','EXTENDED'),('EMR','Emerson','Industrials','US','EXTENDED'),
    ('ETN','Eaton','Industrials','US','EXTENDED'),('HUBB','Hubbell','Industrials','US','EXTENDED'),
    ('AXON','Axon Enterprise','Industrials','US','EXTENDED'),
    # ── USA MATERIALS ──────────────────────────────────────
    ('FCX','Freeport-McMoRan','Materials','US','CORE'),('NUE','Nucor','Materials','US','CORE'),
    ('LIN','Linde','Materials','US','CORE'),('ALB','Albemarle','Materials','US','EXTENDED'),
    ('MP','MP Materials','Materials','US','EXTENDED'),('CF','CF Industries','Materials','US','EXTENDED'),
    ('MOS','Mosaic','Materials','US','EXTENDED'),('STLD','Steel Dynamics','Materials','US','EXTENDED'),
    ('RS','Reliance Steel','Materials','US','EXTENDED'),('X','US Steel','Materials','US','EXTENDED'),
    # ── USA UTILITIES ──────────────────────────────────────
    ('NEE','NextEra Energy','Utilities','US','CORE'),('DUK','Duke Energy','Utilities','US','CORE'),
    ('SO','Southern Co','Utilities','US','CORE'),('AEP','AEP','Utilities','US','EXTENDED'),
    ('EXC','Exelon','Utilities','US','EXTENDED'),('PCG','PG&E','Utilities','US','EXTENDED'),
    # ── USA MOMENTUM / CRYPTO ──────────────────────────────
    ('MARA','Marathon Digital','Momentum','US','CORE'),('RIOT','Riot Platforms','Momentum','US','CORE'),
    ('HUT','HUT 8 Mining','Momentum','US','EXTENDED'),('CLSK','CleanSpark','Momentum','US','EXTENDED'),

    # ── DANMARK ────────────────────────────────────────────
    ('NOVO-B.CO','Novo Nordisk','Healthcare','Denmark','CORE'),
    ('DSV.CO','DSV','Industrials','Denmark','EXTENDED'),
    ('DANSKE.CO','Danske Bank','Financials','Denmark','EXTENDED'),
    ('MAERSK-B.CO','AP Moeller Maersk','Industrials','Denmark','EXTENDED'),
    ('PNDORA.CO','Pandora','Consumer','Denmark','EXTENDED'),
    ('GMAB.CO','Genmab','Healthcare','Denmark','EXTENDED'),
    ('VWS.CO','Vestas','Industrials','Denmark','EXTENDED'),
    ('ORSTED.CO','Orsted','Utilities','Denmark','EXTENDED'),
    ('ALMB.CO','Alm. Brand','Financials','Denmark','EXTENDED'),
    ('JYSK.CO','Jyske Bank','Financials','Denmark','EXTENDED'),
    ('TRMD-A.CO','TORM','Energy','Denmark','EXTENDED'),
    ('SPG.CO','SP Group','Industrials','Denmark','EXTENDED'),
    ('AGF-B.CO','AGF','Consumer','Denmark','EXTENDED'),
    ('PARKEN.CO','PARKEN','Consumer','Denmark','EXTENDED'),
    ('ASTK.CO','Asetek','Tech','Denmark','EXTENDED'),
    ('BETCO.ST','Better Collective','Consumer','Denmark','EXTENDED'),

    # ── SVERIGE ────────────────────────────────────────────
    ('EVO.ST','Evolution','Tech','Sweden','CORE'),
    ('VOLV-B.ST','Volvo','Industrials','Sweden','EXTENDED'),
    ('ERIC-B.ST','Ericsson','Tech','Sweden','EXTENDED'),
    ('ATCO-A.ST','Atlas Copco','Industrials','Sweden','EXTENDED'),
    ('SAND.ST','Sandvik','Industrials','Sweden','EXTENDED'),
    ('INVE-B.ST','Investor AB','Financials','Sweden','EXTENDED'),
    ('NDA-SE.ST','Nordea','Financials','Sweden','EXTENDED'),
    ('SECU-B.ST','Securitas','Industrials','Sweden','EXTENDED'),
    ('SKA-B.ST','Skanska','Industrials','Sweden','EXTENDED'),
    ('MILDEF.ST','MilDef Group','Industrials','Sweden','EXTENDED'),
    ('CLAV.ST','Clavister','Tech','Sweden','EXTENDED'),
    ('VSURE.ST','Verisure','Tech','Sweden','EXTENDED'),
    ('SPRINT.ST','Sprint Bioscience','Healthcare','Sweden','EXTENDED'),
    ('NANEXA.ST','Nanexa','Healthcare','Sweden','EXTENDED'),
    ('SINCH.ST','Sinch','Tech','Sweden','EXTENDED'),
    ('EMBRAC-B.ST','Embracer','Tech','Sweden','EXTENDED'),

    # ── NORGE ──────────────────────────────────────────────
    ('EQNR.OL','Equinor','Energy','Norway','EXTENDED'),
    ('DNB.OL','DNB Bank','Financials','Norway','EXTENDED'),
    ('KOG.OL','Kongsberg Gruppen','Industrials','Norway','EXTENDED'),
    ('TEL.OL','Telenor','Tech','Norway','EXTENDED'),
    ('NAS.OL','Norwegian Air','Industrials','Norway','EXTENDED'),
    ('KIT.OL','Kitron','Industrials','Norway','EXTENDED'),
    ('KAHOT.OL','Kahoot','Tech','Norway','EXTENDED'),

    # ── NEDERLANDENE ───────────────────────────────────────
    ('ASML.AS','ASML','AI','Netherlands','CORE'),
    ('ASM.AS','ASM International','AI','Netherlands','CORE'),
    ('BESI.AS','BE Semiconductor','AI','Netherlands','CORE'),
    ('ADYEN.AS','Adyen','Tech','Netherlands','EXTENDED'),
    ('INGA.AS','ING','Financials','Netherlands','EXTENDED'),
    ('PHIA.AS','Philips','Healthcare','Netherlands','EXTENDED'),

    # ── TYSKLAND ───────────────────────────────────────────
    ('SAP.DE','SAP','Tech','Germany','CORE'),
    ('IFX.DE','Infineon','AI','Germany','CORE'),
    ('RHM.DE','Rheinmetall','Industrials','Germany','CORE'),
    ('SIE.DE','Siemens','Industrials','Germany','EXTENDED'),
    ('ALV.DE','Allianz','Financials','Germany','EXTENDED'),
    ('MBG.DE','Mercedes-Benz','Consumer','Germany','EXTENDED'),
    ('BMW.DE','BMW','Consumer','Germany','EXTENDED'),
    ('BAYN.DE','Bayer','Healthcare','Germany','EXTENDED'),
    ('MRK.DE','Merck KGaA','Healthcare','Germany','EXTENDED'),

    # ── UK ─────────────────────────────────────────────────
    ('SHEL.L','Shell','Energy','UK','EXTENDED'),
    ('BP.L','BP','Energy','UK','EXTENDED'),
    ('AZN.L','AstraZeneca','Healthcare','UK','EXTENDED'),
    ('GSK.L','GSK','Healthcare','UK','EXTENDED'),
    ('RR.L','Rolls-Royce','Industrials','UK','EXTENDED'),
    ('BA.L','BAE Systems','Industrials','UK','EXTENDED'),
    ('RIO.L','Rio Tinto','Materials','UK','EXTENDED'),
    ('GLEN.L','Glencore','Materials','UK','EXTENDED'),
    ('HSBA.L','HSBC','Financials','UK','EXTENDED'),
    ('REL.L','RELX','Tech','UK','EXTENDED'),
    ('EXPN.L','Experian','Tech','UK','EXTENDED'),

    # ── FRANKRIG ───────────────────────────────────────────
    ('MC.PA','LVMH','Consumer','France','EXTENDED'),
    ('RMS.PA','Hermes','Consumer','France','EXTENDED'),
    ('AIR.PA','Airbus','Industrials','France','EXTENDED'),
    ('HO.PA','Thales','Industrials','France','EXTENDED'),
    ('TTE.PA','TotalEnergies','Energy','France','EXTENDED'),
    ('BNP.PA','BNP Paribas','Financials','France','EXTENDED'),
    ('SAN.PA','Sanofi','Healthcare','France','EXTENDED'),
    ('CAP.PA','Capgemini','Tech','France','EXTENDED'),
    ('STMPA.PA','STMicro','AI','France','EXTENDED'),

    # ── SCHWEIZ ────────────────────────────────────────────
    ('ROG.SW','Roche','Healthcare','Switzerland','EXTENDED'),
    ('NOVN.SW','Novartis','Healthcare','Switzerland','EXTENDED'),
    ('UBSG.SW','UBS','Financials','Switzerland','EXTENDED'),
    ('ABBN.SW','ABB','Industrials','Switzerland','EXTENDED'),
    ('LOGN.SW','Logitech','Tech','Switzerland','EXTENDED'),
    ('NESN.SW','Nestle','Consumer','Switzerland','EXTENDED'),

    # ── SPANIEN / ITALIEN ──────────────────────────────────
    ('IBE.MC','Iberdrola','Utilities','Spain','EXTENDED'),
    ('SAN.MC','Banco Santander','Financials','Spain','EXTENDED'),
    ('ITX.MC','Inditex','Consumer','Spain','EXTENDED'),
    ('ENEL.MI','Enel','Utilities','Italy','EXTENDED'),
    ('ENI.MI','ENI','Energy','Italy','EXTENDED'),
    ('UCG.MI','UniCredit','Financials','Italy','EXTENDED'),

    # ── FINLAND ────────────────────────────────────────────
    ('NOKIA.HE','Nokia','Tech','Finland','EXTENDED'),
    ('KNEBV.HE','Kone','Industrials','Finland','EXTENDED'),

    # ── JAPAN ──────────────────────────────────────────────
    ('7203.T','Toyota','Consumer','Japan','EXTENDED'),
    ('6758.T','Sony','Tech','Japan','EXTENDED'),
    ('9984.T','SoftBank','Tech','Japan','EXTENDED'),
    ('6861.T','Keyence','AI','Japan','EXTENDED'),
    ('6501.T','Hitachi','Industrials','Japan','EXTENDED'),
    ('8306.T','Mitsubishi UFJ','Financials','Japan','EXTENDED'),
    ('7267.T','Honda','Consumer','Japan','EXTENDED'),
    ('6902.T','Denso','Industrials','Japan','EXTENDED'),

    # ── HONG KONG ──────────────────────────────────────────
    ('0700.HK','Tencent','Tech','HongKong','EXTENDED'),
    ('9988.HK','Alibaba','Consumer','HongKong','EXTENDED'),
    ('3690.HK','Meituan','Consumer','HongKong','EXTENDED'),
    ('1810.HK','Xiaomi','Tech','HongKong','EXTENDED'),

    # ── ASIEN ØVRIGE ───────────────────────────────────────
    ('005930.KS','Samsung','Tech','SouthKorea','EXTENDED'),
    ('000660.KS','SK Hynix','AI','SouthKorea','EXTENDED'),
    ('2330.TW','TSMC TW','AI','Taiwan','EXTENDED'),
    ('INFY.NS','Infosys','Tech','India','EXTENDED'),
    ('TCS.NS','Tata Consultancy','Tech','India','EXTENDED'),
    ('RELIANCE.NS','Reliance','Energy','India','EXTENDED'),

    # ── SEKTOR ETF'er ──────────────────────────────────────
    ('XLE','Energy SPDR','ETF','US','EXTENDED'),
    ('XLK','Tech SPDR','ETF','US','EXTENDED'),
    ('XLF','Financials SPDR','ETF','US','EXTENDED'),
    ('XLV','Healthcare SPDR','ETF','US','EXTENDED'),
    ('XLI','Industrials SPDR','ETF','US','EXTENDED'),
    ('XLB','Materials SPDR','ETF','US','EXTENDED'),
    ('XLY','Consumer Disc SPDR','ETF','US','EXTENDED'),
    ('XLP','Consumer Stap SPDR','ETF','US','EXTENDED'),
    ('XLU','Utilities SPDR','ETF','US','EXTENDED'),
    ('SOXX','Semiconductors','ETF','US','EXTENDED'),
    ('ARKK','ARK Innovation','ETF','US','EXTENDED'),
    ('BOTZ','Robotics AI','ETF','Global','EXTENDED'),
    ('CIBR','Cybersecurity','ETF','US','EXTENDED'),
    ('ITA','Defense','ETF','US','EXTENDED'),
    ('BITO','Bitcoin ETF','ETF','Crypto','EXTENDED'),
    ('GLD','Gold ETF','ETF','Commodities','EXTENDED'),
    ('SLV','Silver ETF','ETF','Commodities','EXTENDED'),
    ('COPX','Copper Miners','ETF','Commodities','EXTENDED'),
    ('VGK','Europe ETF','ETF','Europe','EXTENDED'),
    ('EEM','Emerging Markets','ETF','Global','EXTENDED'),

    # ── USA TECH EKSTRA ────────────────────────────────────
    ('DELL','Dell Technologies','Tech','US','EXTENDED'),
    ('HPQ','HP Inc','Tech','US','EXTENDED'),
    ('IBM','IBM','Tech','US','EXTENDED'),
    ('ACN','Accenture','Tech','US','EXTENDED'),
    ('CTSH','Cognizant','Tech','US','EXTENDED'),
    ('EPAM','EPAM Systems','Tech','US','EXTENDED'),
    ('GLOB','Globant','Tech','US','EXTENDED'),
    ('TWLO','Twilio','Tech','US','EXTENDED'),
    ('ZS','Zscaler','Tech','US','EXTENDED'),
    ('OKTA','Okta','Tech','US','EXTENDED'),
    ('HUBS','HubSpot','Tech','US','EXTENDED'),
    ('TEAM','Atlassian','Tech','US','EXTENDED'),
    ('MDB','MongoDB','Tech','US','EXTENDED'),
    ('ESTC','Elastic','Tech','US','EXTENDED'),
    ('PTC','PTC Inc','Tech','US','EXTENDED'),
    ('CDNS','Cadence Design','AI','US','EXTENDED'),
    ('SNPS','Synopsys','AI','US','EXTENDED'),
    ('ANSS','Ansys','AI','US','EXTENDED'),
    ('NXPI','NXP Semi','AI','US','EXTENDED'),
    ('MCHP','Microchip Tech','AI','US','EXTENDED'),
    ('ADI','Analog Devices','AI','US','EXTENDED'),
    ('SWKS','Skyworks','AI','US','EXTENDED'),
    ('QRVO','Qorvo','AI','US','EXTENDED'),
    ('LAM','Lam Research','AI','US','EXTENDED'),
    ('WOLF','Wolfspeed','AI','US','EXTENDED'),
    ('ACLS','Axcelis Tech','AI','US','EXTENDED'),
    ('ONTO','Onto Innovation','AI','US','EXTENDED'),
    ('ICHR','Ichor Holdings','AI','US','EXTENDED'),
    # ── USA FINANS EKSTRA ──────────────────────────────────
    ('USB','US Bancorp','Financials','US','EXTENDED'),
    ('TFC','Truist Financial','Financials','US','EXTENDED'),
    ('PNC','PNC Financial','Financials','US','EXTENDED'),
    ('MTB','M&T Bank','Financials','US','EXTENDED'),
    ('CFG','Citizens Financial','Financials','US','EXTENDED'),
    ('FITB','Fifth Third','Financials','US','EXTENDED'),
    ('HBAN','Huntington','Financials','US','EXTENDED'),
    ('KEY','KeyCorp','Financials','US','EXTENDED'),
    ('RF','Regions Financial','Financials','US','EXTENDED'),
    ('STT','State Street','Financials','US','EXTENDED'),
    ('BK','BNY Mellon','Financials','US','EXTENDED'),
    ('ICE','Intercontinental Exchange','Financials','US','EXTENDED'),
    ('CME','CME Group','Financials','US','EXTENDED'),
    ('CBOE','Cboe Global','Financials','US','EXTENDED'),
    ('NDAQ','Nasdaq Inc','Financials','US','EXTENDED'),
    ('MSCI','MSCI Inc','Financials','US','EXTENDED'),
    ('MCO','Moodys','Financials','US','EXTENDED'),
    ('SPGI','S&P Global','Financials','US','EXTENDED'),
    ('FIS','FIS','Financials','US','EXTENDED'),
    ('FI','Fiserv','Financials','US','EXTENDED'),
    ('GPN','Global Payments','Financials','US','EXTENDED'),
    ('WEX','WEX Inc','Financials','US','EXTENDED'),
    ('ALLY','Ally Financial','Financials','US','EXTENDED'),
    ('DFS','Discover Financial','Financials','US','EXTENDED'),
    ('SYF','Synchrony','Financials','US','EXTENDED'),
    # ── USA HEALTHCARE EKSTRA ──────────────────────────────
    ('ZBH','Zimmer Biomet','Healthcare','US','EXTENDED'),
    ('BSX','Boston Scientific','Healthcare','US','EXTENDED'),
    ('MDT','Medtronic','Healthcare','US','EXTENDED'),
    ('ABT','Abbott Labs','Healthcare','US','EXTENDED'),
    ('BDX','Becton Dickinson','Healthcare','US','EXTENDED'),
    ('IQV','IQVIA','Healthcare','US','EXTENDED'),
    ('CRL','Charles River','Healthcare','US','EXTENDED'),
    ('ILMN','Illumina','Healthcare','US','EXTENDED'),
    ('HOLX','Hologic','Healthcare','US','EXTENDED'),
    ('INCY','Incyte','Healthcare','US','EXTENDED'),
    ('BMRN','BioMarin','Healthcare','US','EXTENDED'),
    ('ALNY','Alnylam Pharma','Healthcare','US','EXTENDED'),
    ('RARE','Ultragenyx','Healthcare','US','EXTENDED'),
    ('EXEL','Exelixis','Healthcare','US','EXTENDED'),
    ('HZNP','Horizon Therapeutics','Healthcare','US','EXTENDED'),
    ('JAZZ','Jazz Pharma','Healthcare','US','EXTENDED'),
    ('VTRS','Viatris','Healthcare','US','EXTENDED'),
    ('AGN','Allergan','Healthcare','US','EXTENDED'),
    # ── USA CONSUMER EKSTRA ────────────────────────────────
    ('LOW','Lowes','Consumer','US','EXTENDED'),
    ('BBY','Best Buy','Consumer','US','EXTENDED'),
    ('DG','Dollar General','Consumer','US','EXTENDED'),
    ('DLTR','Dollar Tree','Consumer','US','EXTENDED'),
    ('KR','Kroger','Consumer','US','EXTENDED'),
    ('SFM','Sprouts Farmers','Consumer','US','EXTENDED'),
    ('FIVE','Five Below','Consumer','US','EXTENDED'),
    ('OLLI','Ollies Bargain','Consumer','US','EXTENDED'),
    ('BURL','Burlington','Consumer','US','EXTENDED'),
    ('TJX','TJX Companies','Consumer','US','EXTENDED'),
    ('ROST','Ross Stores','Consumer','US','EXTENDED'),
    ('GPS','Gap','Consumer','US','EXTENDED'),
    ('ANF','Abercrombie','Consumer','US','EXTENDED'),
    ('AEO','American Eagle','Consumer','US','EXTENDED'),
    ('URBN','Urban Outfitters','Consumer','US','EXTENDED'),
    ('TPR','Tapestry','Consumer','US','EXTENDED'),
    ('RL','Ralph Lauren','Consumer','US','EXTENDED'),
    ('PVH','PVH Corp','Consumer','US','EXTENDED'),
    ('HBI','Hanesbrands','Consumer','US','EXTENDED'),
    ('PG','Procter & Gamble','Consumer','US','EXTENDED'),
    ('KO','Coca-Cola','Consumer','US','EXTENDED'),
    ('PEP','PepsiCo','Consumer','US','EXTENDED'),
    ('MDLZ','Mondelez','Consumer','US','EXTENDED'),
    ('GIS','General Mills','Consumer','US','EXTENDED'),
    ('K','Kellanova','Consumer','US','EXTENDED'),
    ('CPB','Campbell Soup','Consumer','US','EXTENDED'),
    ('HRL','Hormel','Consumer','US','EXTENDED'),
    ('SJM','JM Smucker','Consumer','US','EXTENDED'),
    ('MKC','McCormick','Consumer','US','EXTENDED'),
    ('CLX','Clorox','Consumer','US','EXTENDED'),
    ('CHD','Church Dwight','Consumer','US','EXTENDED'),
    ('EL','Estee Lauder','Consumer','US','EXTENDED'),
    ('REYN','Reynolds Consumer','Consumer','US','EXTENDED'),
    ('PM','Philip Morris','Consumer','US','EXTENDED'),
    ('MO','Altria','Consumer','US','EXTENDED'),
    ('BTI','BAT','Consumer','US','EXTENDED'),
    ('DEO','Diageo','Consumer','US','EXTENDED'),
    ('STZ','Constellation Brands','Consumer','US','EXTENDED'),
    ('BF-B','Brown-Forman','Consumer','US','EXTENDED'),
    ('TAP','Molson Coors','Consumer','US','EXTENDED'),
    ('SAM','Boston Beer','Consumer','US','EXTENDED'),
    # ── USA INDUSTRIALS EKSTRA ─────────────────────────────
    ('ITW','Illinois Tool','Industrials','US','EXTENDED'),
    ('PH','Parker Hannifin','Industrials','US','EXTENDED'),
    ('ROK','Rockwell Auto','Industrials','US','EXTENDED'),
    ('AME','Ametek','Industrials','US','EXTENDED'),
    ('XYL','Xylem','Industrials','US','EXTENDED'),
    ('CARR','Carrier Global','Industrials','US','EXTENDED'),
    ('OTIS','Otis Worldwide','Industrials','US','EXTENDED'),
    ('TT','Trane Technologies','Industrials','US','EXTENDED'),
    ('JCI','Johnson Controls','Industrials','US','EXTENDED'),
    ('GNRC','Generac','Industrials','US','EXTENDED'),
    ('NDSN','Nordson','Industrials','US','EXTENDED'),
    ('GGG','Graco','Industrials','US','EXTENDED'),
    ('MIDD','Middleby','Industrials','US','EXTENDED'),
    ('WM','Waste Management','Industrials','US','EXTENDED'),
    ('RSG','Republic Services','Industrials','US','EXTENDED'),
    ('CSGP','CoStar Group','Industrials','US','EXTENDED'),
    ('VRSK','Verisk Analytics','Industrials','US','EXTENDED'),
    ('LDOS','Leidos','Industrials','US','EXTENDED'),
    ('SAIC','SAIC','Industrials','US','EXTENDED'),
    ('BAH','Booz Allen','Industrials','US','EXTENDED'),
    ('CACI','CACI International','Industrials','US','EXTENDED'),
    ('DRS','Leonardo DRS','Industrials','US','EXTENDED'),
    ('HII','Huntington Ingalls','Industrials','US','EXTENDED'),
    ('TDG','TransDigm','Industrials','US','EXTENDED'),
    ('HEI','HEICO','Industrials','US','EXTENDED'),
    ('TXT','Textron','Industrials','US','EXTENDED'),
    ('SPR','Spirit AeroSystems','Industrials','US','EXTENDED'),
    ('KTOS','Kratos Defense','Industrials','US','EXTENDED'),
    ('AVAV','AeroVironment','Industrials','US','EXTENDED'),
    # ── USA REAL ESTATE / REIT ─────────────────────────────
    ('PLD','Prologis','RealEstate','US','EXTENDED'),
    ('AMT','American Tower','RealEstate','US','EXTENDED'),
    ('CCI','Crown Castle','RealEstate','US','EXTENDED'),
    ('EQIX','Equinix','RealEstate','US','EXTENDED'),
    ('DLR','Digital Realty','RealEstate','US','EXTENDED'),
    ('SPG','Simon Property','RealEstate','US','EXTENDED'),
    ('O','Realty Income','RealEstate','US','EXTENDED'),
    ('VICI','VICI Properties','RealEstate','US','EXTENDED'),
    ('WPC','W P Carey','RealEstate','US','EXTENDED'),
    ('EXR','Extra Space Storage','RealEstate','US','EXTENDED'),
    # ── USA ENERGY EKSTRA ──────────────────────────────────
    ('MRO','Marathon Oil','Energy','US','EXTENDED'),
    ('APA','APA Corp','Energy','US','EXTENDED'),
    ('CTRA','Coterra Energy','Energy','US','EXTENDED'),
    ('SM','SM Energy','Energy','US','EXTENDED'),
    ('MTDR','Matador Resources','Energy','US','EXTENDED'),
    ('CHRD','Chord Energy','Energy','US','EXTENDED'),
    ('VTLE','Vital Energy','Energy','US','EXTENDED'),
    ('OVV','Ovintiv','Energy','US','EXTENDED'),
    ('BKR','Baker Hughes','Energy','US','EXTENDED'),
    ('NOV','NOV Inc','Energy','US','EXTENDED'),
    ('FTI','TechnipFMC','Energy','US','EXTENDED'),
    ('RIG','Transocean','Energy','US','EXTENDED'),
    ('VAL','Valaris','Energy','US','EXTENDED'),
    ('HP','Helmerich Payne','Energy','US','EXTENDED'),
    ('NR','Newpark Resources','Energy','US','EXTENDED'),
    ('NEP','NextEra Partners','Energy','US','EXTENDED'),
    ('ET','Energy Transfer','Energy','US','EXTENDED'),
    ('WMB','Williams Companies','Energy','US','EXTENDED'),
    ('KMI','Kinder Morgan','Energy','US','EXTENDED'),
    ('OKE','ONEOK','Energy','US','EXTENDED'),
    ('LNG','Cheniere Energy','Energy','US','EXTENDED'),
    ('NFE','New Fortress Energy','Energy','US','EXTENDED'),
    # ── USA MATERIALS EKSTRA ───────────────────────────────
    ('AA','Alcoa','Materials','US','EXTENDED'),
    ('CENX','Century Aluminum','Materials','US','EXTENDED'),
    ('CMC','Commercial Metals','Materials','US','EXTENDED'),
    ('WOR','Worthington Ind','Materials','US','EXTENDED'),
    ('ATI','ATI Inc','Materials','US','EXTENDED'),
    ('HCC','Warrior Met Coal','Materials','US','EXTENDED'),
    ('ARCH','Arch Resources','Materials','US','EXTENDED'),
    ('AMR','Alpha Met Resources','Materials','US','EXTENDED'),
    ('CSTM','Constellium','Materials','US','EXTENDED'),
    ('HL','Hecla Mining','Materials','US','EXTENDED'),
    ('PAAS','Pan American Silver','Materials','US','EXTENDED'),
    ('WPM','Wheaton Precious','Materials','US','EXTENDED'),
    ('FNV','Franco-Nevada','Materials','US','EXTENDED'),
    ('GOLD','Barrick Gold','Materials','US','EXTENDED'),
    ('NEM','Newmont','Materials','US','EXTENDED'),
    ('AEM','Agnico Eagle','Materials','US','EXTENDED'),
    ('KGC','Kinross Gold','Materials','US','EXTENDED'),
    # ── AUSTRALIEN / NZ ────────────────────────────────────
    ('BHP','BHP Group','Materials','Australia','EXTENDED'),
    ('RIO','Rio Tinto US','Materials','Australia','EXTENDED'),
    ('VALE','Vale SA','Materials','Brazil','EXTENDED'),
    # ── CANADA ─────────────────────────────────────────────
    ('CNQ','Canadian Natural','Energy','Canada','EXTENDED'),
    ('SU','Suncor Energy','Energy','Canada','EXTENDED'),
    ('CVE','Cenovus Energy','Energy','Canada','EXTENDED'),
    ('IMO','Imperial Oil','Energy','Canada','EXTENDED'),
    ('TRP','TC Energy','Energy','Canada','EXTENDED'),
    ('ENB','Enbridge','Energy','Canada','EXTENDED'),
    ('CP','CP Railway','Industrials','Canada','EXTENDED'),
    ('CNR','CN Railway','Industrials','Canada','EXTENDED'),
    ('BAM','Brookfield Asset','Financials','Canada','EXTENDED'),
    ('MFC','Manulife','Financials','Canada','EXTENDED'),
    ('SLF','Sun Life','Financials','Canada','EXTENDED'),
    ('TD','TD Bank','Financials','Canada','EXTENDED'),
    ('RY','Royal Bank Canada','Financials','Canada','EXTENDED'),
    ('BNS','Bank of Nova Scotia','Financials','Canada','EXTENDED'),
    ('BMO','Bank of Montreal','Financials','Canada','EXTENDED'),
    ('CM','CIBC','Financials','Canada','EXTENDED'),
    ('SHOP','Shopify CA','Tech','Canada','EXTENDED'),
    ('CSU','Constellation Soft','Tech','Canada','EXTENDED'),
    ('OTEX','OpenText','Tech','Canada','EXTENDED'),
    # ── ISRAEL / ANDRE ─────────────────────────────────────
    ('NICE','NICE Systems','Tech','Israel','EXTENDED'),
    ('CHKP','Check Point','Tech','Israel','EXTENDED'),
    ('CYBR','CyberArk','Tech','Israel','EXTENDED'),
    ('MNDY','Monday.com','Tech','Israel','EXTENDED'),
    ('WIX','Wix.com','Tech','Israel','EXTENDED'),
    ('GLBE','Global-E Online','Tech','Israel','EXTENDED'),
    # ── SCHWEIZ EKSTRA ─────────────────────────────────────
    ('GIVN.SW','Givaudan','Consumer','Switzerland','EXTENDED'),
    ('SREN.SW','Swiss Re','Financials','Switzerland','EXTENDED'),
    ('ZURN.SW','Zurich Insurance','Financials','Switzerland','EXTENDED'),
    ('ALC.SW','Alcon','Healthcare','Switzerland','EXTENDED'),
    ('STMN.SW','Straumann','Healthcare','Switzerland','EXTENDED'),
    # ── FRANKRIG EKSTRA ────────────────────────────────────
    ('OR.PA','LOreal','Consumer','France','EXTENDED'),
    ('KER.PA','Kering','Consumer','France','EXTENDED'),
    ('RI.PA','Pernod Ricard','Consumer','France','EXTENDED'),
    ('DSY.PA','Dassault Systemes','Tech','France','EXTENDED'),
    ('ATO.PA','Atos','Tech','France','EXTENDED'),
    ('ORA.PA','Orange','Tech','France','EXTENDED'),
    ('VIE.PA','Veolia','Industrials','France','EXTENDED'),
    ('SGO.PA','Saint-Gobain','Materials','France','EXTENDED'),
    ('LR.PA','Legrand','Industrials','France','EXTENDED'),
    # ── NEDERLAND EKSTRA ───────────────────────────────────
    ('HEIA.AS','Heineken','Consumer','Netherlands','EXTENDED'),
    ('AKZA.AS','Akzo Nobel','Materials','Netherlands','EXTENDED'),
    ('UNA.AS','Unilever NL','Consumer','Netherlands','EXTENDED'),
    ('WKL.AS','Wolters Kluwer','Tech','Netherlands','EXTENDED'),
    # ── TYSKLAND EKSTRA ────────────────────────────────────
    ('DTE.DE','Deutsche Telekom','Tech','Germany','EXTENDED'),
    ('DPW.DE','Deutsche Post','Industrials','Germany','EXTENDED'),
    ('MUV2.DE','Munich Re','Financials','Germany','EXTENDED'),
    ('HEN3.DE','Henkel','Consumer','Germany','EXTENDED'),
    ('VOW3.DE','Volkswagen','Consumer','Germany','EXTENDED'),
    ('ADS.DE','Adidas','Consumer','Germany','EXTENDED'),
    ('PUM.DE','Puma','Consumer','Germany','EXTENDED'),
    ('BAS.DE','BASF','Materials','Germany','EXTENDED'),
    ('1COV.DE','Covestro','Materials','Germany','EXTENDED'),
    ('LHA.DE','Lufthansa','Industrials','Germany','EXTENDED'),
    # ── UK EKSTRA ──────────────────────────────────────────
    ('ULVR.L','Unilever','Consumer','UK','EXTENDED'),
    ('DGE.L','Diageo','Consumer','UK','EXTENDED'),
    ('BATS.L','BAT UK','Consumer','UK','EXTENDED'),
    ('IMB.L','Imperial Brands','Consumer','UK','EXTENDED'),
    ('VOD.L','Vodafone','Tech','UK','EXTENDED'),
    ('BT-A.L','BT Group','Tech','UK','EXTENDED'),
    ('LLOY.L','Lloyds Banking','Financials','UK','EXTENDED'),
    ('BARC.L','Barclays','Financials','UK','EXTENDED'),
    ('NWG.L','NatWest','Financials','UK','EXTENDED'),
    ('STAN.L','Standard Chartered','Financials','UK','EXTENDED'),
    ('PRU.L','Prudential','Financials','UK','EXTENDED'),
    ('LGEN.L','Legal & General','Financials','UK','EXTENDED'),
    ('CPG.L','Compass Group','Consumer','UK','EXTENDED'),
    ('SGE.L','Sage Group','Tech','UK','EXTENDED'),
    ('AUTO.L','Auto Trader','Tech','UK','EXTENDED'),
    ('III.L','3i Group','Financials','UK','EXTENDED'),
    ('WEIR.L','Weir Group','Industrials','UK','EXTENDED'),
    ('SMT.L','Scottish Mortgage','Financials','UK','EXTENDED'),
    # ── SCANDINAVIEN EKSTRA ────────────────────────────────
    ('STERV.HE','Stora Enso','Materials','Finland','EXTENDED'),
    ('UPM.HE','UPM-Kymmene','Materials','Finland','EXTENDED'),
    ('METSO.HE','Metso','Industrials','Finland','EXTENDED'),
    ('NESTE.HE','Neste','Energy','Finland','EXTENDED'),
    ('SAMPO.HE','Sampo','Financials','Finland','EXTENDED'),
    ('OUT1V.HE','Outokumpu','Materials','Finland','EXTENDED'),
    ('FORTUM.HE','Fortum','Utilities','Finland','EXTENDED'),
    ('ELISA.HE','Elisa','Tech','Finland','EXTENDED'),
    ('TEM1V.HE','Telia Finland','Tech','Finland','EXTENDED'),
    ('TDC.CO','TDC Net','Tech','Denmark','EXTENDED'),
    ('NETC.CO','Netcompany','Tech','Denmark','EXTENDED'),
    ('RBREW.CO','Royal Unibrew','Consumer','Denmark','EXTENDED'),
    ('CARL-B.CO','Carlsberg','Consumer','Denmark','EXTENDED'),
    ('FLS.CO','FLSmidth','Industrials','Denmark','EXTENDED'),
    ('GN.CO','GN Audio','Tech','Denmark','EXTENDED'),
    ('AMBU-B.CO','Ambu','Healthcare','Denmark','EXTENDED'),
    ('CHR.CO','Chr. Hansen','Healthcare','Denmark','EXTENDED'),
    ('COLO-B.CO','Coloplast','Healthcare','Denmark','EXTENDED'),
    ('NZYM-B.CO','Novozymes','Healthcare','Denmark','EXTENDED'),
    ('SYDB.CO','Sydbank','Financials','Denmark','EXTENDED'),
    ('DEMANT.CO','Demant','Healthcare','Denmark','EXTENDED'),
    ('NTG.CO','NTG Nordic','Industrials','Denmark','EXTENDED'),
    ('ROCK-B.CO','Rockwool','Materials','Denmark','EXTENDED'),
    ('DFDS.CO','DFDS','Industrials','Denmark','EXTENDED'),
    ('MAB.CO','Matas','Consumer','Denmark','EXTENDED'),
    ('AOJ-P.CO','Alm. Brand Forsikring','Financials','Denmark','EXTENDED'),
    ('NNIT.CO','NNIT','Tech','Denmark','EXTENDED'),
    ('BOUV.CO','Bouygues','Industrials','Denmark','EXTENDED'),
    ('SPNO.CO','Sparekassen Nord','Financials','Denmark','EXTENDED'),
    ('NKT.CO','NKT','Industrials','Denmark','EXTENDED'),
    ('VICTOR-B.CO','Victoria Properties','RealEstate','Denmark','EXTENDED'),
    ('HEM.CO','Hemonto','Financials','Denmark','EXTENDED'),
    # ── NORGE EKSTRA ───────────────────────────────────────
    ('MOWI.OL','Mowi','Consumer','Norway','EXTENDED'),
    ('SALM.OL','SalMar','Consumer','Norway','EXTENDED'),
    ('LSG.OL','Leroy Seafood','Consumer','Norway','EXTENDED'),
    ('AUSS.OL','Austevoll Seafood','Consumer','Norway','EXTENDED'),
    ('AKSO.OL','Aker Solutions','Energy','Norway','EXTENDED'),
    ('SUBC.OL','Subsea 7','Energy','Norway','EXTENDED'),
    ('TGS.OL','TGS','Energy','Norway','EXTENDED'),
    ('PGS.OL','PGS','Energy','Norway','EXTENDED'),
    ('AKERBP.OL','Aker BP','Energy','Norway','EXTENDED'),
    ('VAR.OL','Vår Energi','Energy','Norway','EXTENDED'),
    ('RECSI.OL','REC Silicon','Energy','Norway','EXTENDED'),
    ('NEL.OL','Nel ASA','Energy','Norway','EXTENDED'),
    ('SCATC.OL','Scatec','Energy','Norway','EXTENDED'),
    ('BAKKA.OL','Bakkafrost','Consumer','Norway','EXTENDED'),
    ('GRIEG.OL','Grieg Seafood','Consumer','Norway','EXTENDED'),
    ('AKER.OL','Aker ASA','Industrials','Norway','EXTENDED'),
    ('YAR.OL','Yara International','Materials','Norway','EXTENDED'),
    ('ORK.OL','Orkla','Consumer','Norway','EXTENDED'),
    ('SRBANK.OL','SR-Bank','Financials','Norway','EXTENDED'),
    ('SBANKEN.OL','SpareBank 1','Financials','Norway','EXTENDED'),
    ('GJF.OL','Gjensidige','Financials','Norway','EXTENDED'),
    ('STRO.OL','Strongpoint','Tech','Norway','EXTENDED'),
    ('ZAL.OL','Zalaris','Tech','Norway','EXTENDED'),
    # ── SVERIGE EKSTRA ─────────────────────────────────────
    ('HM-B.ST','H&M','Consumer','Sweden','EXTENDED'),
    ('ESSITY-B.ST','Essity','Consumer','Sweden','EXTENDED'),
    ('HUSQ-B.ST','Husqvarna','Consumer','Sweden','EXTENDED'),
    ('SWED-A.ST','Swedbank','Financials','Sweden','EXTENDED'),
    ('SHB-A.ST','Handelsbanken','Financials','Sweden','EXTENDED'),
    ('SEB-A.ST','SEB Bank','Financials','Sweden','EXTENDED'),
    ('LUNE.ST','Lundin Energy','Energy','Sweden','EXTENDED'),
    ('ASSA-B.ST','ASSA ABLOY','Industrials','Sweden','EXTENDED'),
    ('ALFA.ST','Alfa Laval','Industrials','Sweden','EXTENDED'),
    ('NIBE-B.ST','NIBE Industrier','Industrials','Sweden','EXTENDED'),
    ('HEXA-B.ST','Hexagon','Tech','Sweden','EXTENDED'),
    ('TEL2-B.ST','Tele2','Tech','Sweden','EXTENDED'),
    ('TELIA.ST','Telia','Tech','Sweden','EXTENDED'),
    ('BOLL.ST','Boliden','Materials','Sweden','EXTENDED'),
    ('SSAB-A.ST','SSAB','Materials','Sweden','EXTENDED'),
    ('SKF-B.ST','SKF','Industrials','Sweden','EXTENDED'),
    ('INDT.ST','Indutrade','Industrials','Sweden','EXTENDED'),
    ('LIAB.ST','Lifco','Industrials','Sweden','EXTENDED'),
    ('CAST.ST','Castellum','RealEstate','Sweden','EXTENDED'),
    ('FABG.ST','Fabege','RealEstate','Sweden','EXTENDED'),

    # ── REFERENCE INDEKS – hentes automatisk til RS Trend ──
    ('^OMXC25',  'C25 Ref',    'REF','Denmark',     'EXTENDED'),
    ('^OMXS30',  'OMX30 Ref',  'REF','Sweden',      'EXTENDED'),
    ('^OSEBX',   'OBX Ref',    'REF','Norway',       'EXTENDED'),
    ('^GDAXI',   'DAX Ref',    'REF','Germany',      'EXTENDED'),
    ('^FTSE',    'FTSE Ref',   'REF','UK',            'EXTENDED'),
    ('^FCHI',    'CAC Ref',    'REF','France',        'EXTENDED'),
    ('^AEX',     'AEX Ref',    'REF','Netherlands',   'EXTENDED'),
    ('^SSMI',    'SMI Ref',    'REF','Switzerland',   'EXTENDED'),
    ('^N225',    'Nikkei Ref', 'REF','Japan',         'EXTENDED'),
    ('^HSI',     'HSI Ref',    'REF','HongKong',      'EXTENDED'),
    ('^KS11',    'KOSPI Ref',  'REF','SouthKorea',    'EXTENDED'),
    ('^GSPTSE',  'TSX Ref',    'REF','Canada',        'EXTENDED'),
    ('^BSESN',   'BSE Ref',    'REF','India',         'EXTENDED'),
]

# ══════════════════════════════════════════════════════════════
# INDIKATORER
# ══════════════════════════════════════════════════════════════
def safe_col(df, col):
    """Håndterer både normal og MultiIndex DataFrame fra yfinance"""
    if isinstance(df.columns, pd.MultiIndex):
        # MultiIndex: (kolonne, ticker) – tag første ticker
        return df[col].iloc[:, 0].squeeze().values
    return df[col].squeeze().values

def sma(arr, n):
    if arr is None or len(arr)<n: return None
    return float(np.mean(arr[-n:]))

def calc_rsi(closes, period=14):
    if closes is None or len(closes)<period+1: return None
    gains=losses=0.0
    for i in range(len(closes)-period,len(closes)):
        d=closes[i]-closes[i-1]
        if d>=0: gains+=d
        else: losses+=abs(d)
    ag=gains/period; al=losses/period
    if al==0 and ag==0: return 50.0
    if al==0: return 100.0
    return 100.0-(100.0/(1.0+ag/al))

def calc_atr(highs,lows,closes,period=20):
    if highs is None or len(highs)<period+1: return None
    trs=[max(highs[i]-lows[i],abs(highs[i]-closes[i-1]),abs(lows[i]-closes[i-1])) for i in range(1,len(highs))]
    if len(trs)<period: return None
    return float(np.mean(trs[-period:]))

def calc_ibd_rs_raw(c):
    n=len(c)
    if n<252: return None
    try:
        q4=c[-1]/c[-64]-1 if n>=64 else 0
        q3=c[-64]/c[-127]-1 if n>=127 else 0
        q2=c[-127]/c[-189]-1 if n>=189 else 0
        q1=c[-189]/c[-252]-1 if n>=252 else 0
        return q4*0.40+q3*0.20+q2*0.20+q1*0.20
    except: return None

def weinstein_stage(c,s200):
    if len(c)<210: return 0,'?'
    p=c[-1]; s=s200[-1]; s4w=s200[-20] if len(s200)>=20 else s
    r=s>s4w
    if p>s and r: return 2,'S2✅'
    if p>s and not r: return 3,'S3⚠️'
    if p<s and not r: return 4,'S4❌'
    return 1,'S1🔄'

# ══════════════════════════════════════════════════════════════
# SIGNALLOGIK – EKSAKT SHEETS v5.2
# ══════════════════════════════════════════════════════════════
def derive_states(price,sma20,sma60,sma200,rsi,rsi_trend,low5,dist_h20,
                  vol_ratio,liq_pass,atr20,squeeze,rs_trend,higher_low,
                  inst_accum,cap_risk,trend,trend200,market_regime,ifs,ls):
    ts=0
    if price>sma200: ts+=24
    if sma20>sma60:  ts+=18
    if price>sma20:  ts+=10
    if rs_trend=='UP': ts+=12
    if higher_low: ts+=8
    ts+=min(10,int((ifs or 0)/10))

    tight=(atr20/price)<=0.045 if(atr20 and price>0) else False
    accum=(trend=='BUY' and trend200=='LONG TREND' and rsi is not None
           and 38<=rsi<=64 and vol_ratio is not None and vol_ratio>=0.90
           and abs((price-sma20)/sma20)<=0.06 and rs_trend in('UP','FLAT',''))
    ib=accum and(inst_accum or(ifs or 0)>=65)
    br=(trend=='BUY' and trend200=='LONG TREND' and rs_trend in('UP','FLAT','')
        and dist_h20 is not None and 0<=dist_h20<=CONFIG['breakout_distance']
        and vol_ratio is not None and 0.95<=vol_ratio<=3.0
        and rsi is not None and 44<=rsi<=78
        and(squeeze or(dist_h20 is not None and dist_h20<=0.03)))
    ma=(br and vol_ratio is not None and vol_ratio>=1.10
        and rsi is not None and 50<=rsi<=80 and liq_pass and market_regime!='RISK_OFF')
    ext=(rsi is not None and rsi>84) or price>sma20*1.14

    # ── MOMENTUM-KORREKT SVAGHEDSLOGIK ──
    rsi_recovering = rsi_trend == 'UP' and rsi is not None and rsi > 36
    fs = (rs_trend == 'DOWN'
          and price < sma200
          and (sma20 < sma60 or (rsi is not None and rsi < 36))
          and not rsi_recovering)

    # WEAKENING: RS svækkes + under SMA20 (men ikke nødvendigvis under SMA200)
    wk = (rs_trend == 'DOWN' and price < sma20
          and not fs)

    ss=0
    if accum: ss+=20
    if tight: ss+=6
    if ib:    ss+=18
    if br:    ss+=22
    if ma:    ss+=16
    if squeeze: ss+=6
    if rsi is not None and 46<=rsi<=72: ss+=6
    if dist_h20 is not None and dist_h20<=0.07: ss+=6
    if vol_ratio is not None and vol_ratio>=0.95: ss+=6
    ss+=min(10,int((ls or 0)/10))

    rp=0
    if not liq_pass: rp+=14
    if market_regime=='RISK_OFF': rp+=10
    if rs_trend=='DOWN': rp+=6
    if ext: rp+=8
    if cap_risk: rp+=6
    if wk: rp+=8
    if fs: rp+=14

    pri=max(0,min(100,ts+ss-rp))

    if fs:      st_='FAILED_SETUP'
    elif ext:   st_='EXTENDED'
    elif ma:    st_='MOMENTUM_ACTIVE'
    elif br:    st_='BREAKOUT_READY'
    elif ib:    st_='INSTITUTIONAL_BUILD'
    elif accum: st_='ACCUMULATION'
    elif wk:    st_='WEAKENING'
    else:       st_='NO_SETUP'

    am={'ACCUMULATION':'STARTER','INSTITUTIONAL_BUILD':'BUILD',
        'BREAKOUT_READY':'BREAKOUT_ENTRY','MOMENTUM_ACTIVE':'MOMENTUM_ENTRY',
        'EXTENDED':'EXTENDED','WEAKENING':'REDUCE','FAILED_SETUP':'EXIT'}
    ac=am.get(st_,'WATCHLIST')

    # I NEUTRAL/RISK_ON: downgrade EXIT → REDUCE hvis RSI ikke i frit fald
    if ac=='EXIT' and market_regime!='RISK_OFF' and rsi is not None and rsi>30:
        ac='REDUCE'
    if market_regime=='RISK_OFF' and ac in('BUILD','BREAKOUT_ENTRY','MOMENTUM_ENTRY'):
        ac='STARTER'

    bm={'STARTER':'STARTER BUY','BUILD':'BUILD POSITION',
        'BREAKOUT_ENTRY':'BUY BREAKOUT','MOMENTUM_ENTRY':'BUY NOW','EXTENDED':'EXTENDED — WAIT'}
    buy=bm.get(ac,'WATCHLIST')
    sell='EXIT' if ac=='EXIT' else('REDUCE' if ac=='REDUCE' else 'HOLD')

    stop=round(sma20,2)
    if st_=='MOMENTUM_ACTIVE' and atr20: stop=round(max(low5,price-1.5*atr20),2)
    elif st_=='INSTITUTIONAL_BUILD' and atr20: stop=round(max(low5,sma20-0.5*atr20),2)

    return {'ts':ts,'ss':ss,'rp':rp,'score':pri,'setup':st_,'action':ac,
            'buy':buy,'sell':sell,'stop':stop}

# ══════════════════════════════════════════════════════════════
# LOKALE REFERENCE INDEKS PR. REGION
# ══════════════════════════════════════════════════════════════
REGION_INDEX = {
    'US':          'SPY',
    'Denmark':     '^OMXC25',
    'Sweden':      '^OMXS30',
    'Norway':      '^OSEBX',
    'Finland':     '^OMXH25',
    'Germany':     '^GDAXI',
    'UK':          '^FTSE',
    'France':      '^FCHI',
    'Netherlands': '^AEX',
    'Switzerland': '^SSMI',
    'Spain':       '^IBEX',
    'Italy':       'FTSEMIB.MI',
    'Japan':       '^N225',
    'HongKong':    '^HSI',
    'SouthKorea':  '^KS11',
    'Taiwan':      '^TWII',
    'India':       '^BSESN',
    'Canada':      '^GSPTSE',
    'Australia':   '^AXJO',
    'Brazil':      '^BVSP',
    'Israel':      '^TA125.TA',
    'Global':      'SPY',
    'Europe':      'VGK',
    'Commodities': 'GLD',
    'Crypto':      'BITO',
}

@st.cache_data(ttl=900, show_spinner=False)
def fetch_reference_indices():
    """Hent alle lokale reference indeks til RS Trend beregning"""
    unique_indices = list(set(REGION_INDEX.values()))
    closes = {}
    # Hent i én batch – de er få nok
    try:
        raw = yf.download(unique_indices, period='3mo', interval='1d',
                         group_by='ticker', auto_adjust=True, progress=False, threads=True)
        for idx in unique_indices:
            try:
                df = (raw[idx] if len(unique_indices)>1 else raw).dropna()
                if len(df) >= 25:
                    closes[idx] = safe_col(df,'Close')
            except: pass
    except: pass
    return closes

@st.cache_data(ttl=600, show_spinner=False)
def fetch_market_data():
    all_tickers=list(set(MACRO_TICKERS+[t for t,_ in SECTOR_ETFS]))
    rows={}
    try:
        raw=yf.download(all_tickers,period='6mo',interval='1d',
                        group_by='ticker',auto_adjust=True,progress=False)
        for t in all_tickers:
            try:
                df=(raw[t] if len(all_tickers)>1 else raw).dropna()
                if len(df)<5: continue
                c=safe_col(df,'Close')
                p=float(c[-1]); prev=float(c[-2])
                d5=float(c[-6]) if len(c)>5 else prev
                d30=float(c[-31]) if len(c)>30 else prev
                pct1=round((p/prev-1)*100,1) if prev>0 else 0
                pct5=round((p/d5-1)*100,1) if d5>0 else 0
                pct30=round((p/d30-1)*100,1) if d30>0 else 0
                s20=float(np.mean(c[-20:])) if len(c)>=20 else p
                s60=float(np.mean(c[-60:])) if len(c)>=60 else p
                trend='UP' if p>s20>s60 else('DOWN' if p<s20<s60 else 'MIX')
                rows[t]={'price':round(p,2),'pct1':pct1,'pct5':pct5,'pct30':pct30,'trend':trend,
                         'closes': c[-60:].tolist()}  # gem til sparklines
            except: pass
    except: pass
    return rows

@st.cache_data(ttl=900, show_spinner=False)
def fetch_scanner_data(universe_tuple, market_regime='NEUTRAL'):
    universe=list(universe_tuple)
    tickers=[t[0] for t in universe]
    info_map={t[0]:t for t in universe}
    results=[]
    all_raw={}

    # Hent alle aktier i chunks af 50 – identisk med hvad der virkede
    for i in range(0,len(tickers),50):
        chunk=tickers[i:i+50]
        try:
            raw=yf.download(chunk,period='1y',interval='1d',
                            group_by='ticker',auto_adjust=True,progress=False,threads=True)
            for t in chunk:
                try:
                    df=(raw[t] if len(chunk)>1 else raw).dropna()
                    if len(df)>=210: all_raw[t]=df
                except: pass
        except: pass

    rs_raws={t:calc_ibd_rs_raw(safe_col(df,'Close')) for t,df in all_raw.items()}
    valid_rs={k:v for k,v in rs_raws.items() if v is not None}
    rs_ranks=pd.Series(valid_rs).rank(pct=True).multiply(99).round(0).astype(int) if valid_rs else pd.Series()

    for ticker,df in all_raw.items():
        try:
            info=info_map.get(ticker,(ticker,ticker,'Unknown','Unknown','CORE'))
            c=safe_col(df,'Close'); h=safe_col(df,'High')
            l=safe_col(df,'Low');   v=safe_col(df,'Volume')
            n=len(c)
            if n<210: continue
            price=float(c[-1])
            if price<=0 or price>1_000_000: continue
            prev=float(c[-2])
            dpct=(price/prev-1)*100 if prev>0 else 0
            if abs(dpct)>50: dpct=0

            sma20v=sma(c,20); sma60v=sma(c,60); sma200v=sma(c,200)
            if any(x is None for x in [sma20v,sma60v,sma200v]): continue
            rsiv=calc_rsi(c,14)
            atr5v=calc_atr(h,l,c,5); atr20v=calc_atr(h,l,c,20)
            high20=float(np.max(c[-20:]))
            low5v=float(np.min(l[-5:])); low20v=float(np.min(l[-20:]))
            avg_v20=float(np.mean(v[-20:])); avg_v50=float(np.mean(v[-50:])) if n>=50 else avg_v20
            last_vol=float(v[-1])
            volr=last_vol/avg_v20 if avg_v20>0 else None
            rvol50=last_vol/avg_v50 if avg_v50>0 else None
            dolvol=avg_v20*price
            dist_h20=(high20-price)/high20 if high20>0 else None
            hl=low5v>low20v
            lp=avg_v20>=CONFIG['min_avg_vol'] and dolvol>=CONFIG['min_dollar_vol']
            cap_r=dolvol<25_000_000
            sqz=bool(atr5v and atr20v and atr5v<atr20v*CONFIG['squeeze_factor'])
            rsi_prev5=calc_rsi(c[:-5],14) if n>19 else rsiv
            rsi_t='UP' if(rsiv and rsi_prev5 and rsiv>rsi_prev5) else('DOWN' if(rsiv and rsi_prev5 and rsiv<rsi_prev5) else 'FLAT')

            # ── RS TREND MOD LOKALT INDEKS ──
            region = info[3] if len(info)>3 else 'US'
            local_idx = REGION_INDEX.get(region, 'SPY')
            # Brug lokalt indeks hvis det er i all_raw, ellers SPY, ellers FLAT
            ref_df = all_raw.get(local_idx) or all_raw.get('SPY')
            if ref_df is not None:
                ref_closes = ref_safe_col(df,'Close')
                if len(ref_closes)>=21 and n>=21:
                    ref_now  = float(ref_closes[-1])
                    ref_past = float(ref_closes[-21])
                    if ref_now>0 and ref_past>0:
                        rs_now  = price / ref_now
                        rs_past = float(c[-21]) / ref_past
                        rs_t = 'UP' if rs_now>rs_past else('DOWN' if rs_now<rs_past else 'FLAT')
                    else: rs_t='FLAT'
                else: rs_t='FLAT'
            else: rs_t='FLAT'

            trend='BUY' if sma20v>sma60v else('SELL' if sma20v<sma60v else 'HOLD')
            trend200='LONG TREND' if price>sma200v else 'WEAK LONG TREND'

            ia=(trend=='BUY' and trend200=='LONG TREND' and rsiv is not None
                and 40<=rsiv<=64 and rs_t in('UP','FLAT') and rsi_t in('UP','FLAT')
                and volr is not None and volr>=0.95 and hl and dist_h20 is not None and dist_h20<=0.10)

            ifs=0
            if volr and volr>1.15: ifs+=20
            if hl: ifs+=20
            if rs_t=='UP': ifs+=20
            if price>sma20v: ifs+=20
            if rsiv and 42<=rsiv<=68: ifs+=20
            if trend200=='LONG TREND': ifs+=10
            if ia: ifs+=10
            ifs=min(ifs,100)

            ls=0
            if avg_v20>=5_000_000: ls+=40
            elif avg_v20>=1_000_000: ls+=25
            elif avg_v20>=200_000: ls+=12
            if dolvol>=100_000_000: ls+=30
            elif dolvol>=30_000_000: ls+=20
            elif dolvol>=8_000_000: ls+=10
            if volr and volr>=1.0: ls+=20
            if not cap_r: ls+=10
            ls=min(ls,100)

            s200arr=np.array([sma(c[:i+1],200) or 0 for i in range(len(c))])
            stn,stl=weinstein_stage(c,s200arr)
            rs_rank=int(rs_ranks.get(ticker,0)) if ticker in rs_ranks.index else 0
            w52h=float(np.max(c[-252:])) if n>=252 else float(np.max(c))
            w52l=float(np.min(c[-252:])) if n>=252 else float(np.min(c))
            atr_pct=atr20v/price*100 if(atr20v and price>0) else 0

            st=derive_states(price,sma20v,sma60v,sma200v,rsiv,rsi_t,low5v,dist_h20,
                             volr,lp,atr20v,sqz,rs_t,hl,ia,cap_r,trend,trend200,
                             market_regime,ifs,ls)
            results.append({
                'ticker':ticker,'name':info[1],'sector':info[2],'region':info[3],'tier':info[4] if len(info)>4 else 'CORE',
                'price':round(price,2),'dpct':round(dpct,1),
                'rsi':round(rsiv,1) if rsiv else None,'rsi_t':rsi_t,
                'sma20':round(sma20v,2),'sma60':round(sma60v,2),'sma200':round(sma200v,2),
                'trend':trend,'trend200':trend200,
                'high20':round(high20,2),'low5':round(low5v,2),
                'dh20':round(dist_h20*100,1) if dist_h20 is not None else None,
                'volr':round(volr,2) if volr else None,'rvol50':round(rvol50,2) if rvol50 else None,
                'avgvol':round(avg_v20,0),'dolvol_m':round(dolvol/1e6,1),
                'liq':'✅' if lp else '❌','lp':lp,
                'atr20':round(atr20v,2) if atr20v else None,'atr_pct':round(atr_pct,1),
                'sqz':'⚡' if sqz else '—','sqz_b':sqz,
                'rs_t':rs_t,'hl':'✅' if hl else '—','ia':'✅' if ia else '—','cap':'⚠️' if cap_r else '—',
                'ifs':ifs,'ls':ls,'stn':stn,'stage':stl,'rs_rank':rs_rank,
                'w52h':round(w52h,2),'w52l':round(w52l,2),
                'dist52':round((w52h-price)/w52h*100,1) if w52h>0 else 0,
                'ts':st['ts'],'ss':st['ss'],'rp':st['rp'],'score':st['score'],
                'setup':st['setup'],'buy':st['buy'],'sell':st['sell'],'stop':st['stop'],
            })
        except: continue

    df_out=pd.DataFrame(results)
    if not df_out.empty:
        df_out=df_out.sort_values('score',ascending=False).reset_index(drop=True)
    return df_out

def derive_regime(mkt,scan):
    """
    Forbedret regime-beregning:
    - Bruger BÅDE 6M trend OG daglig bevægelse
    - VIX niveau + VIX retning (faldende VIX = bullish)
    - Breadth fra scanneren
    - Kortsigtede momentum signaler
    """
    score=0
    if mkt:
        # Index trend (6M) – men vægter lavere nu
        for t,pts in [('SPY',1),('QQQ',1),('IWM',1)]:
            if t in mkt:
                tr=mkt[t]['trend']
                score+=pts if tr=='UP' else(-pts if tr=='DOWN' else 0)

        # Daglig bevægelse – er markedet grønt I DAG?
        for t,pts in [('SPY',2),('QQQ',1),('IWM',1)]:
            if t in mkt:
                pct=mkt[t].get('pct1',0) or 0
                score+=pts if pct>0.5 else(-pts if pct<-0.5 else 0)

        # 5-dages momentum
        for t,pts in [('SPY',1),('QQQ',1)]:
            if t in mkt:
                pct5=mkt[t].get('pct5',0) or 0
                score+=pts if pct5>1.0 else(-pts if pct5<-2.0 else 0)

        # VIX niveau
        if '^VIX' in mkt:
            v=mkt['^VIX']['price']
            score+=-3 if v>35 else(-2 if v>28 else(-1 if v>22 else(1 if v<18 else(2 if v<15 else 0))))

        # VIX retning – faldende VIX er bullish
        if '^VIX' in mkt:
            vix_pct=mkt['^VIX'].get('pct1',0) or 0
            score+=2 if vix_pct<-5 else(1 if vix_pct<-2 else(-1 if vix_pct>5 else 0))

    if not scan.empty:
        total=max(len(scan),1)
        a20=(scan['price']>scan['sma20']).sum()/total
        a200=(scan['price']>scan['sma200']).sum()/total
        score+=2 if a20>=0.55 else(-2 if a20<0.40 else 0)
        score+=2 if a200>=0.50 else(-2 if a200<0.35 else 0)
        buys=scan['buy'].isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION']).sum()
        score+=1 if buys>=5 else(-1 if buys==0 else 0)

    if score>=6: return 'RISK_ON'
    if score<=0: return 'RISK_OFF'
    return 'NEUTRAL'

# ══════════════════════════════════════════════════════════════
# POSITIONER
# ══════════════════════════════════════════════════════════════
def load_json(f): return json.load(open(f)) if os.path.exists(f) else []
def save_json(f,d): json.dump(d,open(f,'w'),indent=2,default=str)

# ══════════════════════════════════════════════════════════════
# CUSTOM UNIVERSE – tilføj aktier via UI
# ══════════════════════════════════════════════════════════════
def load_custom_universe():
    raw = load_json(CUSTOM_UNIVERSE_FILE)
    return [tuple(r) for r in raw]

def save_custom_universe(entries):
    save_json(CUSTOM_UNIVERSE_FILE, [list(e) for e in entries])

@st.cache_data(ttl=60, show_spinner=False)
def lookup_ticker(ticker):
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        name   = info.get('longName') or info.get('shortName') or ticker
        sector = info.get('sector') or 'Unknown'
        country = info.get('country') or 'Unknown'
        country_map = {
            'United States':'US','Denmark':'Denmark','Sweden':'Sweden',
            'Norway':'Norway','Finland':'Finland','Germany':'Germany',
            'United Kingdom':'UK','France':'France','Netherlands':'Netherlands',
            'Switzerland':'Switzerland','Spain':'Spain','Italy':'Italy',
            'Japan':'Japan','Hong Kong':'HongKong','South Korea':'SouthKorea',
            'Taiwan':'Taiwan','Canada':'Canada','Israel':'Israel',
            'India':'India','Australia':'Australia','Brazil':'Brazil',
        }
        region = country_map.get(country, country)
        return (ticker.upper(), name, sector, region, 'EXTENDED'), None
    except Exception as e:
        return None, str(e)

# ══════════════════════════════════════════════════════════════
# EARNINGS LAYER – on-demand
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_earnings_dates(tickers_tuple):
    tickers = list(tickers_tuple)
    earnings_map = {}
    today = pd.Timestamp.now(tz='UTC').normalize()
    for ticker in tickers:
        ed = None
        try:
            tk = yf.Ticker(ticker)
            try:
                edf = tk.earnings_dates
                if edf is not None and not edf.empty:
                    edf.index = pd.to_datetime(edf.index, utc=True)
                    future = edf[edf.index.normalize() >= today]
                    if not future.empty:
                        ed = future.index.min()
            except: pass
            if ed is None:
                try:
                    cal = tk.calendar
                    if cal is not None:
                        if isinstance(cal, dict):
                            val = cal.get('Earnings Date') or cal.get('earningsDate')
                            if val:
                                dates = val if isinstance(val,(list,tuple)) else [val]
                                dates = [pd.Timestamp(d,tz='UTC') for d in dates if pd.notna(d)]
                                future = [d for d in dates if d.normalize()>=today]
                                ed = min(future) if future else None
                        elif hasattr(cal,'index') and 'Earnings Date' in cal.index:
                            val = cal.loc['Earnings Date']
                            if hasattr(val,'__iter__') and not isinstance(val,str):
                                dates = [pd.Timestamp(d,tz='UTC') for d in val if pd.notna(d)]
                                future = [d for d in dates if d.normalize()>=today]
                                ed = min(future) if future else None
                            else:
                                d = pd.Timestamp(val,tz='UTC')
                                ed = d if d.normalize()>=today else None
                except: pass
        except: pass
        earnings_map[ticker] = ed
    return earnings_map

def calc_earnings_fields(ticker, earnings_map):
    today = pd.Timestamp.now(tz='UTC').normalize()
    ed = earnings_map.get(ticker)
    if ed is None:
        return {'earnings_date':'N/A','days_to_earnings':None,'earnings_flag':'N/A','has_earnings':False}
    days = (ed.normalize()-today).days
    if days < 0:   flag = 'N/A'
    elif days <= 2: flag = 'RISK'
    elif days <= 7: flag = 'SOON'
    elif days <= 20: flag = 'UPCOMING'
    else:           flag = 'LATER'
    return {'earnings_date':ed.strftime('%Y-%m-%d'),'days_to_earnings':int(days) if days>=0 else None,
            'earnings_flag':flag,'has_earnings':True}

def enrich_earnings(df, earnings_map):
    if df.empty: return df
    rows = [calc_earnings_fields(t, earnings_map) for t in df['ticker']]
    return pd.concat([df, pd.DataFrame(rows, index=df.index)], axis=1)

# ══════════════════════════════════════════════════════════════
# ROTATION LAYER
# ══════════════════════════════════════════════════════════════
SECTOR_PEERS = {
    'Tech':        ['AAPL','MSFT','NVDA','AMD','GOOGL','META','ORCL','CRM','NOW','ADBE'],
    'AI':          ['NVDA','AMD','PLTR','AVGO','MRVL','SMCI','ARM','TSM','CDNS','SNPS'],
    'Financials':  ['JPM','GS','MS','V','MA','BAC','BLK','AXP','SCHW','COF'],
    'Energy':      ['XOM','CVX','COP','EOG','DVN','OXY','FANG','SLB','HAL','PSX'],
    'Healthcare':  ['LLY','UNH','REGN','VRTX','JNJ','MRK','ABBV','AMGN','GILD','BMY'],
    'Consumer':    ['AMZN','TSLA','NFLX','COST','HD','WMT','NKE','SBUX','MCD','CMG'],
    'Industrials': ['CAT','GE','RTX','LMT','NOC','BA','HON','GEV','PWR','ETN'],
    'Materials':   ['FCX','NUE','LIN','ALB','NEM','GOLD','WPM','FNV','FCX','MP'],
    'Utilities':   ['NEE','DUK','SO','AEP','EXC','PCG'],
    'RealEstate':  ['PLD','AMT','EQIX','DLR','CCI','SPG','O'],
    'Momentum':    ['MARA','RIOT','PLTR','RKLB','IONQ','CRWD','NET'],
    'ETF':         ['SPY','QQQ','IWM','XLK','XLE','XLF','XLV','XLI'],
}

def calc_rotation(df, positions):
    if df.empty or not positions:
        df['is_in_portfolio'] = False
        df['best_peer'] = None
        df['best_peer_score'] = None
        df['rotation_score'] = None
        df['rotation_action'] = None
        return df
    portfolio_tickers = {p['ticker'] for p in positions}
    score_map = dict(zip(df['ticker'], df['score']))
    sector_map = dict(zip(df['ticker'], df['sector']))
    rotation_rows = {}
    for ticker in portfolio_tickers:
        if ticker not in score_map: continue
        sector = sector_map.get(ticker, 'Tech')
        peers = SECTOR_PEERS.get(sector, [])
        peer_scores = {p: score_map[p] for p in peers if p in score_map and p != ticker}
        if not peer_scores:
            rotation_rows[ticker] = {'best_peer':None,'best_peer_score':None,'rotation_score':0,'rotation_action':'HOLD'}
            continue
        best_peer = max(peer_scores, key=peer_scores.get)
        best_score = peer_scores[best_peer]
        rot_score = round(best_score - score_map[ticker], 1)
        action = 'ROTATE' if rot_score>10 else ('TRIM' if rot_score>=5 else 'HOLD')
        rotation_rows[ticker] = {'best_peer':best_peer,'best_peer_score':best_score,
                                  'rotation_score':rot_score,'rotation_action':action}
    df['is_in_portfolio'] = df['ticker'].isin(portfolio_tickers)
    df['best_peer']       = df['ticker'].map(lambda t: rotation_rows.get(t,{}).get('best_peer'))
    df['best_peer_score'] = df['ticker'].map(lambda t: rotation_rows.get(t,{}).get('best_peer_score'))
    df['rotation_score']  = df['ticker'].map(lambda t: rotation_rows.get(t,{}).get('rotation_score'))
    df['rotation_action'] = df['ticker'].map(lambda t: rotation_rows.get(t,{}).get('rotation_action'))
    return df

def enrich_positions(positions,scan):
    if not positions: return pd.DataFrame()
    rows=[]
    for p in positions:
        t=p['ticker']; m=scan[scan['ticker']==t] if not scan.empty else pd.DataFrame()
        cp=float(m.iloc[0]['price']) if not m.empty else p['entry_price']
        rows.append({'TICKER':t,'NAVN':p.get('name',t),'ENTRY':p['entry_price'],'NU':round(cp,2),
                     'PnL%':round((cp/p['entry_price']-1)*100,2),
                     'PnLkr':round((cp-p['entry_price'])*p['shares'],2),
                     'AKTIER':p['shares'],
                     'STOP':m.iloc[0]['stop'] if not m.empty else '—',
                     'SIGNAL':m.iloc[0]['buy'] if not m.empty else '—',
                     'RS':m.iloc[0]['rs_rank'] if not m.empty else '—',
                     'SCORE':m.iloc[0]['score'] if not m.empty else '—',
                     'DATO':p.get('date','—')})
    df=pd.DataFrame(rows)
    return df.sort_values('PnL%',ascending=False) if not df.empty else df

# ══════════════════════════════════════════════════════════════
# CHART
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def get_chart_data(ticker):
    return yf.download(ticker,period='1y',interval='1d',auto_adjust=True,progress=False).dropna()

def make_sparkline(values, color='#00ff88', height=40):
    """Mini sparkline chart til market pulse"""
    if values is None or len(values) < 2: return None
    v = list(values[-30:])  # seneste 30 dage
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=v, mode='lines',
        line=dict(color=color, width=1.5),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.08)',
        hoverinfo='skip'
    ))
    fig.update_layout(
        height=height, margin=dict(l=0,r=0,t=0,b=0),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False
    )
    return fig

def make_vix_gauge(vix_val):
    """VIX Fear/Greed gauge"""
    if vix_val is None: vix_val = 20
    color = '#ff3333' if vix_val>28 else ('#ffaa00' if vix_val>20 else '#00ff88')
    label = 'EKSTREM FRYGT' if vix_val>35 else ('FRYGT' if vix_val>25 else ('NEUTRAL' if vix_val>18 else ('GRÅDIGHED' if vix_val>15 else 'EKSTREM GRÅDIGHED')))
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=vix_val,
        number={'font':{'color':color,'family':'Orbitron','size':22},'suffix':''},
        gauge={
            'axis':{'range':[10,50],'tickcolor':'#333','tickfont':{'color':'#333','size':8},'tickvals':[15,20,25,30,40]},
            'bar':{'color':color,'thickness':0.6},
            'bgcolor':'#0d0d0d','bordercolor':'#1a1a1a','borderwidth':1,
            'steps':[
                {'range':[10,18],'color':'#002210'},
                {'range':[18,25],'color':'#111'},
                {'range':[25,35],'color':'#1a0a00'},
                {'range':[35,50],'color':'#1a0000'},
            ],
            'threshold':{'line':{'color':color,'width':2},'thickness':0.8,'value':vix_val}
        },
        title={'text':f'VIX FEAR/GREED<br><span style="font-size:0.65rem;color:#555">{label}</span>',
               'font':{'color':'#555','family':'IBM Plex Mono','size':9}},
    ))
    fig.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        height=150, margin=dict(l=10,r=10,t=35,b=5),
        font=dict(color='#aaa')
    )
    return fig

def make_breadth_chart(scan_df):
    """Markedsbreadth donut – fordeling af signaler"""
    if scan_df.empty: return None
    clean = scan_df[scan_df['sector']!='REF']
    counts = {
        'BUY NOW':    (clean['buy']=='BUY NOW').sum(),
        'BREAKOUT':   (clean['buy']=='BUY BREAKOUT').sum(),
        'BUILD':      clean['buy'].isin(['BUILD POSITION','STARTER BUY']).sum(),
        'WATCHLIST':  (clean['buy']=='WATCHLIST').sum(),
        'REDUCE':     (clean['sell']=='REDUCE').sum(),
        'EXIT':       (clean['sell']=='EXIT').sum(),
    }
    labels = list(counts.keys())
    values = list(counts.values())
    colors = ['#00ff88','#00cc66','#0066cc','#222','#cc4400','#cc0000']
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.65,
        marker=dict(colors=colors, line=dict(color='#0d0d0d',width=1)),
        textfont=dict(size=9, family='IBM Plex Mono', color='#888'),
        textposition='outside',
        hovertemplate='<b>%{label}</b>: %{value}<extra></extra>',
    ))
    total = sum(values)
    buy_total = counts['BUY NOW']+counts['BREAKOUT']+counts['BUILD']
    fig.add_annotation(
        text=f'<b style="font-size:16px">{buy_total}</b><br><span style="font-size:8px;color:#555">BUY</span>',
        x=0.5, y=0.5, showarrow=False,
        font=dict(color='#00ff88', family='Orbitron', size=14)
    )
    fig.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        height=160, margin=dict(l=10,r=10,t=10,b=10),
        showlegend=False, font=dict(color='#aaa')
    )
    return fig

def make_score_histogram(scan_df):
    """Score distribution histogram"""
    if scan_df.empty: return None
    clean = scan_df[scan_df['sector']!='REF']['score'].dropna()
    fig = go.Figure(go.Histogram(
        x=clean, nbinsx=20,
        marker=dict(
            color=clean,
            colorscale=[[0,'#cc0000'],[0.5,'#ffaa00'],[1,'#00ff88']],
            line=dict(color='#0d0d0d',width=0.5)
        ),
    ))
    fig.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        height=100, margin=dict(l=5,r=5,t=5,b=20),
        xaxis=dict(gridcolor='#111',color='#333',tickfont=dict(color='#333',size=8),title=''),
        yaxis=dict(gridcolor='#111',color='#333',tickfont=dict(color='#333',size=8)),
        bargap=0.1, font=dict(color='#aaa'),
        showlegend=False
    )
    return fig

def plot_chart(ticker,df,signal=''):
    if df.empty: return go.Figure()
    c=safe_col(df,'Close'); h=safe_col(df,'High')
    l=safe_col(df,'Low');   o=safe_col(df,'Open')
    v=safe_col(df,'Volume'); idx=df.index
    s20=pd.Series(c).rolling(20).mean().values
    s60=pd.Series(c).rolling(60).mean().values
    s200=pd.Series(c).rolling(200).mean().values
    d=pd.Series(c).diff(); g=d.clip(lower=0).rolling(14).mean(); ls_=(-d.clip(upper=0)).rolling(14).mean()
    rsi=(100-100/(1+g/ls_.replace(0,np.nan))).values
    fig=make_subplots(rows=3,cols=1,row_heights=[0.55,0.2,0.25],shared_xaxes=True,vertical_spacing=0.02)
    fig.add_trace(go.Candlestick(x=idx,open=o,high=h,low=l,close=c,name=ticker,
        increasing_line_color='#00ff41',decreasing_line_color='#ff3333',
        increasing_fillcolor='rgba(0,255,65,0.15)',decreasing_fillcolor='rgba(255,51,51,0.15)'),row=1,col=1)
    for arr,n,col,w in [(s20,'SMA20','#ffaa00',1.5),(s60,'SMA60','#0088ff',1.5),(s200,'SMA200','#cc44ff',2)]:
        fig.add_trace(go.Scatter(x=idx,y=arr,name=n,line=dict(color=col,width=w)),row=1,col=1)
    vc=['rgba(0,255,65,0.5)' if c[i]>=o[i] else 'rgba(255,51,51,0.5)' for i in range(len(c))]
    fig.add_trace(go.Bar(x=idx,y=v,marker_color=vc,showlegend=False),row=2,col=1)
    fig.add_trace(go.Scatter(x=idx,y=rsi,line=dict(color='#ffaa00',width=2),name='RSI'),row=3,col=1)
    fig.add_hline(y=70,line_dash='dash',line_color='rgba(255,51,51,0.5)',row=3,col=1)
    fig.add_hline(y=30,line_dash='dash',line_color='rgba(0,255,65,0.5)',row=3,col=1)
    fig.add_hline(y=50,line_dash='dot',line_color='rgba(255,255,255,0.15)',row=3,col=1)
    ax=dict(gridcolor='rgba(0,255,65,0.08)',zerolinecolor='rgba(0,255,65,0.08)',color='#008f23',tickfont=dict(color='#008f23'))
    fig.update_layout(plot_bgcolor='#000000',paper_bgcolor='#000a00',
        font=dict(color='#00ff41',family='Share Tech Mono',size=11),
        legend=dict(bgcolor='#000a00',bordercolor='rgba(0,255,65,0.2)',orientation='h',y=1.02,font=dict(size=9)),
        height=600,margin=dict(l=55,r=15,t=25,b=15),xaxis_rangeslider_visible=False,
        title=dict(text=f'[ {ticker} ] {signal}',font=dict(color='#00ff41',family='Orbitron',size=11)),
        xaxis=ax,xaxis2=ax,xaxis3=ax,yaxis=ax,yaxis2=ax,yaxis3={**ax,'range':[0,100]})
    return fig

def plot_sector_etf_chart(mkt):
    if not mkt: return go.Figure()
    sectors=[]; scores=[]; colors_=[]
    for etf,name in SECTOR_ETFS:
        if etf in mkt:
            d=mkt[etf]; pct=d['pct1']
            sectors.append(name); scores.append(pct)
            colors_.append('#00ff41' if pct>0 else '#ff3333')
    if not sectors: return go.Figure()
    order=sorted(range(len(scores)),key=lambda i:scores[i])
    fig=go.Figure(go.Bar(
        x=[scores[i] for i in order],
        y=[sectors[i] for i in order],
        orientation='h',
        marker_color=[colors_[i] for i in order],
        text=[f"{scores[i]:+.1f}%" for i in order],
        textposition='outside',textfont=dict(color='#00ff41',family='Share Tech Mono',size=10),
    ))
    fig.update_layout(plot_bgcolor='#000000',paper_bgcolor='#000a00',
        font=dict(color='#00ff41',family='Share Tech Mono',size=10),
        xaxis=dict(gridcolor='rgba(0,255,65,0.1)',zerolinecolor='rgba(0,255,65,0.3)',title='1D %'),
        yaxis=dict(gridcolor='rgba(0,255,65,0.08)'),
        height=max(350,len(sectors)*28),margin=dict(l=130,r=60,t=20,b=30),
        title=dict(text='SEKTOR PERFORMANCE 1D',font=dict(color='#00ff41',family='Orbitron',size=11)))
    return fig

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def pct_html(v, large=False):
    sz = '0.95rem' if large else '0.74rem'
    fw = '700' if large else '600'
    if v is None: return f'<span style="color:#444;font-size:{sz}">—</span>'
    if v>0: return f'<span style="color:#00ff88;font-size:{sz};font-weight:{fw};font-family:IBM Plex Mono,monospace">+{v:.1f}%</span>'
    if v<0: return f'<span style="color:#ff3333;font-size:{sz};font-weight:{fw};font-family:IBM Plex Mono,monospace">{v:.1f}%</span>'
    return f'<span style="color:#666;font-size:{sz};font-family:IBM Plex Mono,monospace">{v:.1f}%</span>'

def trend_badge(t):
    if t=='UP':   return '<span class="tr-up">▲UP</span>'
    if t=='DOWN': return '<span class="tr-dn">▼DN</span>'
    return '<span class="tr-mix">◆</span>'

def sig_block(val):
    """Bloomberg-style farveblok for signal"""
    m = {
        'BUY NOW':         'sig-buynow',
        'BUY BREAKOUT':    'sig-breakout',
        'BUILD POSITION':  'sig-build',
        'STARTER BUY':     'sig-starter',
        'EXTENDED — WAIT': 'sig-extended',
        'REDUCE':          'sig-reduce',
        'EXIT':            'sig-exit',
        'HOLD':            'sig-watch',
        'WATCHLIST':       'sig-watch',
    }
    cls = m.get(val,'sig-watch')
    short = {
        'BUY NOW':'BUY NOW','BUY BREAKOUT':'BREAKOUT',
        'BUILD POSITION':'BUILD','STARTER BUY':'STARTER',
        'EXTENDED — WAIT':'EXTENDED','REDUCE':'REDUCE',
        'EXIT':'EXIT','HOLD':'HOLD','WATCHLIST':'WATCH',
    }.get(val, val[:8])
    return f'<span class="sig-block {cls}">{short}</span>'

def sig_style(val):
    """For dataframe styling"""
    return {
        'BUY NOW':         'background:#00ff88;color:#000;font-weight:700',
        'BUY BREAKOUT':    'background:#00cc66;color:#000;font-weight:700',
        'BUILD POSITION':  'background:#0066cc;color:#fff',
        'STARTER BUY':     'background:#004499;color:#aad4ff',
        'EXTENDED — WAIT': 'background:#cc8800;color:#000',
        'REDUCE':          'background:#cc4400;color:#fff;font-weight:600',
        'EXIT':            'background:#cc0000;color:#fff;font-weight:700',
        'HOLD':            'background:#1a1a1a;color:#444',
        'WATCHLIST':       'background:#111;color:#333',
    }.get(val,'')

def pnl_style(val):
    if isinstance(val,(int,float)):
        return 'color:#00ff88;font-weight:700' if val>0 else('color:#ff3333;font-weight:700' if val<0 else '')
    return ''

def regime_html(r):
    cls={'RISK_ON':'bb-regime-on','RISK_OFF':'bb-regime-off','NEUTRAL':'bb-regime-neu'}.get(r,'bb-regime-neu')
    txt={'RISK_ON':'▲ RISK ON','RISK_OFF':'▼ RISK OFF','NEUTRAL':'◆ NEUTRAL'}.get(r,r)
    return f'<span class="{cls}">{txt}</span>'

def sek_color(pct):
    """Sektor heatmap bagfarve baseret på %"""
    if pct is None: return '#111','#444'
    if pct >= 2.0:  return '#003322','#00ff88'
    if pct >= 1.0:  return '#002218','#00cc66'
    if pct >= 0.3:  return '#001510','#009944'
    if pct >= 0.0:  return '#0d0d0d','#446644'
    if pct >= -0.3: return '#150a0a','#884444'
    if pct >= -1.0: return '#1a0000','#cc3333'
    if pct >= -2.0: return '#220000','#ff3333'
    return '#2a0000','#ff0000'

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════
def main():
    positions=load_json(POSITIONS_FILE)
    watchlist=load_json(WATCHLIST_FILE)

    # Merge custom aktier ind i UNIVERSE
    custom_entries = load_custom_universe()
    existing_tickers = {t[0] for t in UNIVERSE}
    full_universe = UNIVERSE + [e for e in custom_entries if e[0] not in existing_tickers]

    # SIDEBAR – skjult, opdater-knap i header
    show_wl = False
    only_s2 = False

    # LOAD DATA
    prog=st.progress(0,text="`[ INIT ] Henter markedsdata...`")
    mkt=fetch_market_data()
    prog.progress(18,text="`[ CALC ] Regime...`")
    regime=derive_regime(mkt,pd.DataFrame())
    prog.progress(22,text="`[ SCAN ] Scanner univers...`")
    scan=fetch_scanner_data(tuple(full_universe),regime)
    regime=derive_regime(mkt,scan)
    if not scan.empty:
        scan = calc_rotation(scan, positions)
    prog.progress(100,text="`[ OK ] Klar`")
    prog.empty()

    vix_price=mkt.get('^VIX',{}).get('price',None)
    vix_pct=mkt.get('^VIX',{}).get('pct1',None)

    # ── HEADER BAR ──
    if not scan.empty:
        buy_now  = (scan['buy']=='BUY NOW').sum()
        buy_br   = (scan['buy']=='BUY BREAKOUT').sum()
        build    = scan['buy'].isin(['STARTER BUY','BUILD POSITION']).sum()
        exits    = (scan['sell']=='EXIT').sum()
        s2       = (scan['stn']==2).sum()
        rs80     = (scan['rs_rank']>=80).sum()
        sqzn     = scan['sqz_b'].sum()
        ian      = (scan['ia']=='✅').sum()
    else:
        buy_now=buy_br=build=exits=s2=rs80=sqzn=ian=0

    spy_d  = mkt.get('SPY',{})
    qqq_d  = mkt.get('QQQ',{})
    vix_str = f"{vix_price:.1f}" if vix_price else "—"
    vix_col = '#ff3333' if vix_price and vix_price>28 else ('#ffaa00' if vix_price and vix_price>20 else '#00ff88')

    # Børsstatus som kompakt strip
    exch_html = ''
    for name, info in EXCHANGES.items():
        s  = get_exchange_status(info)
        tz = pytz.timezone(info['tz'])
        lt = datetime.now(tz).strftime('%H:%M')
        col = '#00ff88' if s=='ÅBEN' else ('#ffaa00' if s=='PRE' else '#333')
        dot = '●' if s=='ÅBEN' else ('◑' if s=='PRE' else '○')
        exch_html += f'<span style="color:{col};font-size:0.65rem;font-family:IBM Plex Mono,monospace;margin-right:12px">{info["flag"]} {dot} {name} {lt}</span>'

    kpi_cells = [
        ("REGIME",   regime_html(regime), ''),
        ("VIX",      f'<span style="color:{vix_col};font-family:Orbitron,monospace;font-weight:700;font-size:1rem">{vix_str}</span>', pct_html(vix_pct)),
        ("S&P 500",  f'<span style="color:#fff;font-family:Orbitron,monospace;font-size:0.9rem">{spy_d.get("price","—")}</span>', pct_html(spy_d.get('pct1'))),
        ("NASDAQ",   f'<span style="color:#fff;font-family:Orbitron,monospace;font-size:0.9rem">{qqq_d.get("price","—")}</span>', pct_html(qqq_d.get('pct1'))),
        ("AKTIER",   f'<span style="color:#fff;font-family:Orbitron,monospace;font-weight:700;font-size:1rem">{len(scan) if not scan.empty else 0}</span>', ''),
        ("BUY NOW",  f'<span style="color:#00ff88;font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem">{buy_now}</span>', ''),
        ("BREAKOUT", f'<span style="color:#00cc66;font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem">{buy_br}</span>', ''),
        ("BUILD",    f'<span style="color:#4488ff;font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem">{build}</span>', ''),
        ("EXIT",     f'<span style="color:#ff3333;font-family:Orbitron,monospace;font-weight:700;font-size:1.1rem">{exits}</span>', ''),
        ("STAGE 2",  f'<span style="color:#aaa;font-family:Orbitron,monospace;font-size:1rem">{s2}</span>', ''),
        ("SQUEEZE⚡", f'<span style="color:#aaa;font-family:Orbitron,monospace;font-size:1rem">{sqzn}</span>', ''),
        ("RS>80",    f'<span style="color:#aaa;font-family:Orbitron,monospace;font-size:1rem">{rs80}</span>', ''),
    ]
    cells_html = ''.join([
        f'<div class="kpi-cell"><div class="kpi-label">{lbl}</div><div class="kpi-value">{val} {sub}</div></div>'
        for lbl,val,sub in kpi_cells
    ])

    # Opdater-knap øverst til højre
    _c1, _c2 = st.columns([11, 1])
    with _c2:
        if st.button("⟳ OPDATER", use_container_width=True):
            st.cache_data.clear(); st.rerun()

    st.markdown(
        f'<div style="background:#000;border-bottom:2px solid #00ff88;margin-bottom:4px">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 12px;border-bottom:1px solid #0d0d0d">'
        f'<span style="font-family:Orbitron,monospace;font-size:0.85rem;color:#fff;font-weight:900;letter-spacing:3px">▸ TRADING TERMINAL PRO</span>'
        f'<span>{exch_html}</span>'
        f'</div>'
        f'<div class="kpi-strip">{cells_html}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # TABS
    tabs=st.tabs(["▸ FORSIDE","▸ SCANNER","▸ BENCHMARK","▸ POSITIONER","▸ WATCHLIST","▸ CHARTS","▸ RS ANALYSE","▸ PLAYBOOK"])
    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8=tabs

    # ═══════════════════════════════════════════
    # TAB 1: FORSIDE – BLOOMBERG STYLE
    # ═══════════════════════════════════════════
    with tab1:
        # 3-kolonne layout
        col_mkt, col_buy, col_right = st.columns([1, 1, 1])

        # ── KOLONNE 1: MARKET PULSE ──
        with col_mkt:
            st.markdown('<div class="bb-panel"><div class="bb-panel-hdr">MARKET PULSE <span>LIVE</span></div>', unsafe_allow_html=True)

            # Kompakt market rows
            mkt_html = ''
            for grp_name, tickers in MARKET_GROUPS.items():
                mkt_html += f'<div class="mkt-grp">{grp_name}</div>'
                for ticker, name in tickers:
                    d   = mkt.get(ticker, {})
                    p   = d.get('price', None)
                    pct = d.get('pct1', None)
                    tr  = d.get('trend', '')
                    p_str   = f"{p:.2f}" if isinstance(p, float) else '—'
                    pct_cls = 'mkt-up' if pct and pct>0 else ('mkt-dn' if pct and pct<0 else 'mkt-neu')
                    pct_str = f"+{pct:.1f}%" if pct and pct>0 else (f"{pct:.1f}%" if pct else '—')
                    tb  = f'<span class="tr-up">▲</span>' if tr=='UP' else (f'<span class="tr-dn">▼</span>' if tr=='DOWN' else '<span class="tr-mix">◆</span>')
                    mkt_html += (
                        f'<div class="mkt-row">'
                        f'<span class="mkt-t">{ticker}</span>'
                        f'<span class="mkt-n">{name}</span>'
                        f'<span class="mkt-p">{p_str}</span>'
                        f'<span class="{pct_cls}">{pct_str}</span>'
                        f'<span>{tb}</span>'
                        f'</div>'
                    )
            mkt_html += '</div>'
            st.markdown(mkt_html, unsafe_allow_html=True)

        # ── KOLONNE 2: BUY KANDIDATER ──
        with col_buy:
            if not scan.empty:
                cands = scan[
                    (scan['buy'].isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION'])) &
                    (scan['sector'] != 'REF')
                ].head(20)

                n_cands = len(cands)
                st.markdown(f'<div class="bb-panel"><div class="bb-panel-hdr">BUY KANDIDATER <span>{n_cands}</span></div>', unsafe_allow_html=True)

                if cands.empty:
                    st.markdown('<div style="padding:12px 8px;color:#444;font-family:IBM Plex Mono,monospace;font-size:0.75rem">⚠ INGEN AKTIVE SIGNALER – RISK_OFF MARKED</div>', unsafe_allow_html=True)
                else:
                    rows_html = ''
                    for _, r in cands.iterrows():
                        pct = r['dpct']
                        pct_cls = 'mkt-up' if pct>0 else 'mkt-dn'
                        pct_str = f"+{pct:.1f}%" if pct>0 else f"{pct:.1f}%"
                        sb  = sig_block(r['buy'])
                        rows_html += (
                            f'<div class="cand-row">'
                            f'<span class="cand-t">{r["ticker"]}</span>'
                            f'<span class="cand-n">{r["name"]}</span>'
                            f'<span class="cand-p">{r["price"]:.2f}</span>'
                            f'<span class="{pct_cls}">{pct_str}</span>'
                            f'<span class="cand-s">{int(r["score"])}</span>'
                            f'{sb}'
                            f'</div>'
                        )
                    rows_html += '</div>'
                    st.markdown(rows_html, unsafe_allow_html=True)

        # ── KOLONNE 3: POSITIONER + TOP MOVERS ──
        with col_right:
            pos_df_home = enrich_positions(positions, scan)
            if not pos_df_home.empty:
                st.markdown(f'<div class="bb-panel"><div class="bb-panel-hdr">MINE POSITIONER <span>{len(pos_df_home)}</span></div>', unsafe_allow_html=True)
                pos_html = ''
                for _, r in pos_df_home.iterrows():
                    pnl = r['PnL%']
                    pnl_cls = 'mkt-up' if pnl>0 else 'mkt-dn'
                    sb = sig_block(str(r['SIGNAL']))
                    pos_html += (
                        f'<div class="pos-row">'
                        f'<span style="color:#fff;font-weight:700;font-family:IBM Plex Mono,monospace">{r["TICKER"]}</span>'
                        f'<span style="color:#444;font-size:0.67rem;font-family:IBM Plex Mono,monospace;overflow:hidden;white-space:nowrap">{r["NAVN"]}</span>'
                        f'<span style="color:#999;text-align:right;font-family:IBM Plex Mono,monospace">{r["NU"]:.2f}</span>'
                        f'<span class="{pnl_cls}" style="text-align:right;font-family:IBM Plex Mono,monospace;font-weight:700">{pnl:+.1f}%</span>'
                        f'<span style="color:#333;font-size:0.64rem;font-family:IBM Plex Mono,monospace">⬇{r["STOP"]}</span>'
                        f'{sb}'
                        f'</div>'
                    )
                pos_html += '</div>'
                st.markdown(pos_html, unsafe_allow_html=True)

            # TOP 5 OP + NED
            if not scan.empty:
                clean = scan[scan['sector']!='REF']
                st.markdown('<div class="bb-panel"><div class="bb-panel-hdr">TOP MOVERS <span>1D</span></div>', unsafe_allow_html=True)
                mov_html = ''
                for _, r in clean.nlargest(8,'dpct').iterrows():
                    mov_html += (
                        f'<div class="mov-row">'
                        f'<span class="mov-t-up">{r["ticker"]}</span>'
                        f'<span class="mov-sec">{r["sector"]}</span>'
                        f'<span class="mov-p">{r["price"]:.2f}</span>'
                        f'<span class="mkt-up">{r["dpct"]:+.1f}%</span>'
                        f'{sig_block(r["buy"]) if r["buy"]!="WATCHLIST" else ""}'
                        f'</div>'
                    )
                mov_html += '<div style="border-top:1px solid #1a1a1a;margin:2px 0"></div>'
                for _, r in clean.nsmallest(8,'dpct').iterrows():
                    mov_html += (
                        f'<div class="mov-row">'
                        f'<span class="mov-t-dn">{r["ticker"]}</span>'
                        f'<span class="mov-sec">{r["sector"]}</span>'
                        f'<span class="mov-p">{r["price"]:.2f}</span>'
                        f'<span class="mkt-dn">{r["dpct"]:+.1f}%</span>'
                        f'{sig_block(r["sell"]) if r["sell"] not in ["HOLD","WATCHLIST"] else ""}'
                        f'</div>'
                    )
                mov_html += '</div>'
                st.markdown(mov_html, unsafe_allow_html=True)

        # ── SEKTOR HEATMAP – kompakt, mellem de to rækker ──
        if mkt:
            sek_html = '<div class="sek-grid" style="margin:4px 0">'
            for etf, name in SECTOR_ETFS[:15]:
                d   = mkt.get(etf, {})
                pct = d.get('pct1', None)
                bg, fg = sek_color(pct)
                pct_str = f"{pct:+.1f}%" if pct is not None else '—'
                sek_html += (
                    f'<div class="sek-cell" style="background:{bg};border:1px solid #111;padding:4px 6px">'
                    f'<div class="sek-name" style="font-size:0.55rem">{name}</div>'
                    f'<div class="sek-pct" style="color:{fg};font-size:0.82rem">{pct_str}</div>'
                    f'</div>'
                )
            sek_html += '</div>'
            st.markdown(sek_html, unsafe_allow_html=True)

        # ── RÆKKE 2: VIX gauge + Donut + Score + Sparklines ──
        w1, w2, w3, w4 = st.columns([1,1,1,2])

        with w1:
            st.markdown('<div class="bb-panel-hdr">VIX FEAR/GREED</div>', unsafe_allow_html=True)
            fig_vix = make_vix_gauge(vix_price)
            st.plotly_chart(fig_vix, use_container_width=True, config={'displayModeBar':False})

        with w2:
            st.markdown('<div class="bb-panel-hdr">SIGNAL FORDELING</div>', unsafe_allow_html=True)
            fig_donut = make_breadth_chart(scan)
            if fig_donut:
                st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar':False})

        with w3:
            st.markdown('<div class="bb-panel-hdr">SCORE DISTRIBUTION</div>', unsafe_allow_html=True)
            fig_hist = make_score_histogram(scan)
            if fig_hist:
                st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar':False})
            if not scan.empty:
                clean2 = scan[scan['sector']!='REF']
                total2 = max(len(clean2),1)
                a200 = round((clean2['price']>clean2['sma200']).sum()/total2*100,0)
                a20  = round((clean2['price']>clean2['sma20']).sum()/total2*100,0)
                st.markdown(
                    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:2px">'
                    f'<div style="background:#111;padding:4px 6px;font-family:IBM Plex Mono,monospace;font-size:0.7rem"><span style="color:#555">SMA200▲</span><br><span style="color:#fff;font-family:Orbitron,monospace">{a200:.0f}%</span></div>'
                    f'<div style="background:#111;padding:4px 6px;font-family:IBM Plex Mono,monospace;font-size:0.7rem"><span style="color:#555">SMA20▲</span><br><span style="color:#fff;font-family:Orbitron,monospace">{a20:.0f}%</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        with w4:
            st.markdown('<div class="bb-panel-hdr">SPY · QQQ · VIX <span>60D SPARKLINES</span></div>', unsafe_allow_html=True)
            sp1, sp2, sp3 = st.columns(3)
            for col_sp, ticker_sp, label_sp, color_sp in [
                (sp1,'SPY','S&P 500','#00ff88'),
                (sp2,'QQQ','NASDAQ','#4488ff'),
                (sp3,'^VIX','VIX','#ffaa00'),
            ]:
                with col_sp:
                    d_sp = mkt.get(ticker_sp,{})
                    closes_sp = d_sp.get('closes', None)
                    p_sp   = d_sp.get('price','—')
                    pct_sp = d_sp.get('pct1', None)
                    pct_str_sp = f"+{pct_sp:.1f}%" if pct_sp and pct_sp>0 else (f"{pct_sp:.1f}%" if pct_sp else '—')
                    pct_col_sp = '#00ff88' if pct_sp and pct_sp>0 else ('#ff3333' if pct_sp and pct_sp<0 else '#666')
                    st.markdown(
                        f'<div style="background:#0d0d0d;border:1px solid #1a1a1a;padding:5px 8px">'
                        f'<div style="color:#555;font-family:IBM Plex Mono,monospace;font-size:0.58rem;letter-spacing:1px">{label_sp}</div>'
                        f'<div style="color:#fff;font-family:Orbitron,monospace;font-size:0.85rem;font-weight:700">{p_sp if isinstance(p_sp,str) else f"{p_sp:.2f}"}</div>'
                        f'<div style="color:{pct_col_sp};font-family:IBM Plex Mono,monospace;font-size:0.72rem;font-weight:600">{pct_str_sp}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if closes_sp:
                        fig_sp = make_sparkline(closes_sp, color_sp, height=55)
                        if fig_sp:
                            st.plotly_chart(fig_sp, use_container_width=True, config={'displayModeBar':False})

    # ═══════════════════════════════════════════
    # TAB 2: SCANNER
    # ═══════════════════════════════════════════
    with tab2:
        # ── TILFØJ AKTIE ──
        with st.expander("➕ TILFØJ AKTIE TIL SCANNER", expanded=True):
            add_c1, add_c2, add_c3 = st.columns([2,1,1])
            with add_c1:
                new_ticker = st.text_input("TICKER","",placeholder="f.eks. IDR.MC eller HIMS",key='add_ticker').upper().strip()
            with add_c2:
                st.markdown("<br>", unsafe_allow_html=True)
                lookup_btn = st.button("🔍 SLÅ OP", use_container_width=True)
            with add_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                add_btn = st.button("✚ TILFØJ", use_container_width=True)

            if lookup_btn and new_ticker:
                with st.spinner(f"Henter info for {new_ticker}..."):
                    result, err = lookup_ticker(new_ticker)
                if result:
                    st.session_state['lookup_result'] = result
                    st.success(f"✓ **{result[1]}** | {result[2]} | {result[3]}")
                else:
                    st.error(f"Kunne ikke finde {new_ticker}: {err}")
                    st.session_state['lookup_result'] = None

            if add_btn and new_ticker:
                result = st.session_state.get('lookup_result')
                if result and result[0] == new_ticker:
                    existing = load_custom_universe()
                    if any(e[0] == new_ticker for e in existing):
                        st.warning(f"{new_ticker} er allerede i scanneren")
                    elif new_ticker in {t[0] for t in UNIVERSE}:
                        st.warning(f"{new_ticker} er allerede i standard universet")
                    else:
                        existing.append(result)
                        save_custom_universe(existing)
                        st.success(f"✓ {result[1]} tilføjet! Tryk Opdater for at scanne.")
                        st.session_state['lookup_result'] = None
                        st.cache_data.clear(); st.rerun()
                else:
                    st.warning("Tryk først på 🔍 SLÅ OP for at bekræfte tickeren")

            custom_now = load_custom_universe()
            if custom_now:
                st.markdown(f"**Mine tilføjede aktier ({len(custom_now)}):**")
                for i, e in enumerate(custom_now):
                    c1, c2 = st.columns([5,1])
                    with c1: st.markdown(f"`{e[0]}` — {e[1]} | {e[2]} | {e[3]}")
                    with c2:
                        if st.button("×", key=f"rm_{i}"):
                            custom_now.pop(i); save_custom_universe(custom_now)
                            st.cache_data.clear(); st.rerun()

        if not scan.empty:
            # ── Søge og filter række ──
            c1,c2,c3,c4,c5 = st.columns([2,1,1,1,1])
            with c1:
                search = st.text_input("🔍 SØG ticker / navn","", placeholder="f.eks. AAPL eller Apple...")
            with c2:
                sf2 = st.selectbox("SEKTOR",["ALLE"]+sorted(scan['sector'].unique().tolist()))
            with c3:
                rf2 = st.selectbox("REGION",["ALLE"]+sorted(scan['region'].unique().tolist()))
            with c4:
                sig2 = st.selectbox("SIGNAL",["ALLE"]+sorted(scan['buy'].unique().tolist()))
            with c5:
                only_s2b = st.checkbox("KUN STAGE 2",False,key='scanner_s2')

            # ── Filtrering ──
            flt = scan.copy()
            flt = flt[flt['sector'] != 'REF']
            if search:
                s = search.upper()
                flt = flt[flt['ticker'].str.upper().str.contains(s) | flt['name'].str.upper().str.contains(s)]
            if sf2 != "ALLE":  flt = flt[flt['sector']==sf2]
            if rf2 != "ALLE":  flt = flt[flt['region']==rf2]
            if sig2 != "ALLE": flt = flt[flt['buy']==sig2]
            if only_s2b:       flt = flt[flt['stn']==2]

            # ── Earnings on-demand + Portefølje filter ──
            earn_c1, earn_c2, earn_c3, earn_c4 = st.columns([1,2,2,1])
            with earn_c1:
                port_only = st.checkbox("KUN PORTEFØLJE", False, key='pf')
            with earn_c2:
                load_earnings_btn = st.button("📅 HENT EARNINGS", use_container_width=True,
                    help="Henter næste earnings dato for synlige aktier")
            with earn_c3:
                earn_filter = st.selectbox("EARNINGS FILTER",["ALLE","RISK","SOON","UPCOMING","LATER"], key='ef')
            with earn_c4:
                if 'earnings_data' in st.session_state:
                    if st.button("🗑 RYD", use_container_width=True):
                        del st.session_state['earnings_data']; st.rerun()

            if load_earnings_btn:
                # Begræns til top 50 efter score – undgår timeout
                top_flt = flt[flt['sector']!='REF'].nlargest(50, 'score')
                tickers_to_fetch = tuple(top_flt['ticker'].tolist())
                with st.spinner(f"Henter earnings for top {len(tickers_to_fetch)} aktier (efter score)..."):
                    earnings_map = fetch_earnings_dates(tickers_to_fetch)
                    flt = enrich_earnings(flt, earnings_map)
                    st.session_state['earnings_data'] = earnings_map
            elif 'earnings_data' in st.session_state:
                flt = enrich_earnings(flt, st.session_state['earnings_data'])

            if port_only and 'is_in_portfolio' in flt.columns:
                flt = flt[flt['is_in_portfolio']==True]
            if earn_filter != "ALLE" and 'earnings_flag' in flt.columns:
                flt = flt[flt['earnings_flag']==earn_filter]

            st.caption(f"`[ {len(flt)} / {len(scan)} AKTIER ]`")

            def earn_flag_style(val):
                return {'RISK':'background:#cc0000;color:#fff;font-weight:700',
                        'SOON':'background:#cc8800;color:#000;font-weight:700',
                        'UPCOMING':'background:#004499;color:#aad4ff',
                        'LATER':'background:#111;color:#444',
                        'N/A':'background:#0a0a0a;color:#333'}.get(val,'')

            def rot_action_style(val):
                return {'ROTATE':'background:#cc0000;color:#fff;font-weight:700',
                        'TRIM':'background:#cc8800;color:#000;font-weight:700',
                        'HOLD':'background:#003322;color:#00ff88'}.get(val,'')

            cols={
                'ticker':'Ticker','name':'Name','sector':'Sector','region':'Region','tier':'Tier',
                'price':'Price','dpct':'Daily%','rsi':'RSI','rsi_t':'RSI Trend',
                'sma20':'SMA20','sma60':'SMA60','sma200':'SMA200',
                'trend':'Trend','trend200':'Trend200',
                'high20':'High20','low5':'Low5','dh20':'DistHigh20%',
                'volr':'VolRatio','rvol50':'RVOL50','avgvol':'AvgVol20','dolvol_m':'DollarVol20',
                'liq':'LiquidityPass','atr20':'ATR20','sqz':'Squeeze',
                'rs_t':'RS Trend','hl':'HigherLow','ia':'InstAccum','cap':'CapRisk',
                'ifs':'InstFlowScore','ls':'LiquidityScore',
                'ts':'TrendScore','ss':'SetupScore','rp':'RiskPenalty','score':'PriorityScore',
                'setup':'SetupState','buy':'BuySignal','sell':'SellSignal','stop':'Stop',
                'rs_rank':'RS Rank','stage':'Stage',
                'earnings_date':'Earnings','days_to_earnings':'Days','earnings_flag':'Earn.Flag',
                'is_in_portfolio':'Portfolio','best_peer':'Best Peer',
                'best_peer_score':'Peer Score','rotation_score':'Rot.Score','rotation_action':'Rot.Action',
            }
            flt_d = flt[[c for c in cols.keys() if c in flt.columns]].rename(columns=cols)
            flt_d = flt_d.set_index(['Ticker','Name'])

            style = flt_d.style.applymap(sig_style, subset=[c for c in ['BuySignal','SellSignal'] if c in flt_d.columns])
            if 'Earn.Flag' in flt_d.columns:
                style = style.applymap(earn_flag_style, subset=['Earn.Flag'])
            if 'Rot.Action' in flt_d.columns:
                style = style.applymap(rot_action_style, subset=['Rot.Action'])
            style = style.format({
                'Price':'{:.2f}','Daily%':'{:+.1f}%','RSI':'{:.1f}',
                'SMA20':'{:.2f}','SMA60':'{:.2f}','SMA200':'{:.2f}',
                'High20':'{:.2f}','Low5':'{:.2f}','DistHigh20%':'{:.1f}%',
                'VolRatio':'{:.2f}','RVOL50':'{:.2f}','DollarVol20':'{:.1f}M','ATR20':'{:.2f}',
                'InstFlowScore':'{:.0f}','LiquidityScore':'{:.0f}',
                'TrendScore':'{:.0f}','SetupScore':'{:.0f}','RiskPenalty':'{:.0f}',
                'PriorityScore':'{:.0f}','RS Rank':'{:.0f}',
                'Peer Score':'{:.0f}','Rot.Score':'{:.1f}',
            }, na_rep='—')

            st.dataframe(style, use_container_width=True, height=750)
            csv = flt.to_csv(index=False).encode('utf-8')
            st.download_button("⬇ EKSPORT CSV", csv, 'scanner.csv', 'text/csv')

    # ═══════════════════════════════════════════
    # TAB 3: BENCHMARK
    # ═══════════════════════════════════════════
    with tab3:
        st.markdown("### `BENCHMARK & MARKEDSANALYSE`")
        if mkt:
            # Sektor performance chart
            st.plotly_chart(plot_sector_etf_chart(mkt),use_container_width=True)
            st.markdown("---")

            # Detaljeret markedsoversigt per gruppe
            for grp_name,tickers in MARKET_GROUPS.items():
                st.markdown(f"### `{grp_name}`")
                rows=[]
                for ticker,name in tickers:
                    d=mkt.get(ticker,{})
                    if d:
                        rows.append({'Ticker':ticker,'Navn':name,
                                     'Pris':d.get('price','—'),
                                     '1D%':d.get('pct1','—'),
                                     '5D%':d.get('pct5','—'),
                                     '30D%':d.get('pct30','—'),
                                     'Trend':d.get('trend','—')})
                if rows:
                    df_b=pd.DataFrame(rows)
                    def cp(v):
                        if isinstance(v,(int,float)): return f'color:{"#00ff41" if v>0 else "#ff3333" if v<0 else "#008f23"}'
                        return 'color:#008f23'
                    st.dataframe(df_b.style.applymap(cp,subset=['1D%','5D%','30D%'])
                                 .format({'Pris':'{:.2f}','1D%':'{:+.1f}%','5D%':'{:+.1f}%','30D%':'{:+.1f}%'}),
                                 use_container_width=True,hide_index=True)

            # Breadth
            if not scan.empty:
                st.markdown("---")
                st.markdown("### `MARKET BREADTH`")
                total=max(len(scan),1)
                a200=round((scan['price']>scan['sma200']).sum()/total*100,1)
                a20=round((scan['price']>scan['sma20']).sum()/total*100,1)
                r60=round((scan['rsi']>60).sum()/total*100,1)
                r40=round((scan['rsi']<40).sum()/total*100,1)
                s2pct=round((scan['stn']==2).sum()/total*100,1)
                c1,c2,c3,c4,c5=st.columns(5)
                c1.metric("Over SMA200",f"{a200}%")
                c2.metric("Over SMA20",f"{a20}%")
                c3.metric("RSI > 60",f"{r60}%")
                c4.metric("RSI < 40",f"{r40}%")
                c5.metric("Stage 2",f"{s2pct}%")

    # ═══════════════════════════════════════════
    # TAB 4: POSITIONER
    # ═══════════════════════════════════════════
    with tab4:
        st.markdown("### `MINE POSITIONER`")
        pos_df=enrich_positions(positions,scan)
        if not pos_df.empty:
            tp=pos_df['PnLkr'].sum(); ap=pos_df['PnL%'].mean(); wn=(pos_df['PnL%']>0).sum()
            c1,c2,c3,c4=st.columns(4)
            c1.metric("POSITIONER",len(pos_df)); c2.metric("TOTAL PnL",f"{tp:+.0f} kr")
            c3.metric("GNS PnL%",f"{ap:+.1f}%"); c4.metric("WINNERS",f"{wn}/{len(pos_df)}")
            st.dataframe(pos_df.style.applymap(pnl_style,subset=['PnL%','PnLkr'])
                         .applymap(sig_style,subset=['SIGNAL'])
                         .format({'ENTRY':'{:.2f}','NU':'{:.2f}','PnL%':'{:+.2f}%','PnLkr':'{:+.0f}'}),
                         use_container_width=True,hide_index=True)
        else:
            st.info("Ingen aktive positioner.")
        st.markdown("---")
        c1,c2,c3,c4,c5=st.columns(5)
        with c1: nt=st.text_input("TICKER").upper().strip()
        with c2: ne=st.number_input("ENTRY",min_value=0.0,step=0.01,format="%.2f")
        with c3: ns=st.number_input("AKTIER",min_value=1,step=1)
        with c4: nn=st.text_input("NAVN")
        with c5:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("+ TILFØJ",use_container_width=True):
                if nt and ne>0:
                    positions.append({'ticker':nt,'name':nn or nt,'entry_price':ne,'shares':ns,'date':datetime.now().strftime('%Y-%m-%d')})
                    save_json(POSITIONS_FILE,positions); st.success(f"✓ {nt}"); st.rerun()
                else: st.error("Udfyld ticker og pris")
        if positions:
            c1,c2=st.columns([3,1])
            with c1: rm=st.selectbox("FJERN",[p['ticker'] for p in positions])
            with c2:
                st.markdown("<br>",unsafe_allow_html=True)
                if st.button("× FJERN",use_container_width=True):
                    positions=[p for p in positions if p['ticker']!=rm]
                    save_json(POSITIONS_FILE,positions); st.rerun()

    # ═══════════════════════════════════════════
    # TAB 5: WATCHLIST
    # ═══════════════════════════════════════════
    with tab5:
        st.markdown("### `PERSONLIG WATCHLIST`")
        if watchlist and not scan.empty:
            wl_df=scan[scan['ticker'].isin(watchlist)]
            if not wl_df.empty:
                st.dataframe(wl_df[['ticker','name','sector','price','dpct','rsi','rs_rank','stage','score','buy','stop']]
                             .rename(columns={'ticker':'TICKER','name':'NAVN','sector':'SEKTOR','price':'PRIS',
                                              'dpct':'1D%','rsi':'RSI','rs_rank':'RS','stage':'STG','score':'SCORE','buy':'SIGNAL','stop':'STOP'})
                             .style.applymap(sig_style,subset=['SIGNAL'])
                             .format({'PRIS':'{:.2f}','1D%':'{:+.1f}%','RSI':'{:.1f}','SCORE':'{:.0f}'}),
                             use_container_width=True,hide_index=True)
        else:
            st.info("Watchlist er tom.")
        st.markdown("---")
        c1,c2=st.columns([3,1])
        with c1: wt=st.text_input("TILFØJ TICKER").upper().strip()
        with c2:
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("+ TILFØJ",use_container_width=True,key='wl_a'):
                if wt and wt not in watchlist:
                    watchlist.append(wt); save_json(WATCHLIST_FILE,watchlist); st.rerun()
        if watchlist:
            c1,c2=st.columns([3,1])
            with c1: wr=st.selectbox("FJERN",watchlist)
            with c2:
                st.markdown("<br>",unsafe_allow_html=True)
                if st.button("× FJERN",use_container_width=True,key='wl_r'):
                    watchlist=[w for w in watchlist if w!=wr]
                    save_json(WATCHLIST_FILE,watchlist); st.rerun()

    # ═══════════════════════════════════════════
    # TAB 6: CHARTS
    # ═══════════════════════════════════════════
    with tab6:
        st.markdown("### `TERMINAL CHART`")
        if not scan.empty:
            tl=scan['ticker'].tolist()
            sel=st.selectbox("VÆLG AKTIE",tl,
                format_func=lambda t: f"{t} — {scan[scan['ticker']==t].iloc[0]['name']}" if not scan[scan['ticker']==t].empty else t)
            if sel:
                row=scan[scan['ticker']==sel].iloc[0]
                c1,c2,c3,c4,c5,c6,c7=st.columns(7)
                c1.metric("PRIS",f"{row['price']:.2f}"); c2.metric("1D%",f"{row['dpct']:+.1f}%")
                c3.metric("RSI",f"{row['rsi']:.1f}" if row['rsi'] else "—")
                c4.metric("RS RANK",f"{row['rs_rank']}/99"); c5.metric("SCORE",f"{int(row['score'])}")
                c6.metric("STAGE",row['stage']); c7.metric("ATR%",f"{row['atr_pct']:.1f}%")
                c1,c2,c3,c4=st.columns(4)
                c1.info(f"**SIGNAL:** {row['buy']}"); c2.info(f"**SETUP:** {row['setup']}")
                c3.info(f"**STOP:** {row['stop']}");  c4.info(f"**SQZ:** {row['sqz']}")
                with st.spinner("HENTER CHART..."):
                    cdf=get_chart_data(sel)
                    st.plotly_chart(plot_chart(sel,cdf,row['buy']),use_container_width=True)

    # ═══════════════════════════════════════════
    # TAB 7: RS ANALYSE
    # ═══════════════════════════════════════════
    with tab7:
        st.markdown("### `IBD RS RANK ANALYSE`")
        st.caption("`RS Rank påvirker IKKE PriorityScore`")
        if not scan.empty:
            color_map={'BUY NOW':'#00ff41','BUY BREAKOUT':'#00cc33','BUILD POSITION':'#0088ff',
                       'STARTER BUY':'#00aaff','EXTENDED — WAIT':'#ffaa00',
                       'REDUCE':'#ff6600','EXIT':'#ff3333','WATCHLIST':'#225522'}
            fig=go.Figure()
            for sig,grp in scan.groupby('buy'):
                fig.add_trace(go.Scatter(x=grp['rs_rank'],y=grp['score'],mode='markers+text',name=sig,
                    text=grp['ticker'],textposition='top center',
                    textfont=dict(size=8,color='#008f23',family='Share Tech Mono'),
                    marker=dict(size=8,color=color_map.get(sig,'#225522'),opacity=0.9,
                                line=dict(width=1,color='rgba(0,255,65,0.2)')),
                    hovertemplate='<b>%{text}</b><br>RS:%{x} | Score:%{y}<extra></extra>'))
            fig.add_vline(x=70,line_dash='dash',line_color='rgba(0,255,65,0.4)')
            fig.add_hline(y=60,line_dash='dash',line_color='rgba(255,170,0,0.4)')
            fig.update_layout(plot_bgcolor='#000000',paper_bgcolor='#000a00',
                font=dict(color='#00ff41',family='Share Tech Mono'),
                xaxis=dict(title='IBD RS RANK',range=[0,100],gridcolor='rgba(0,255,65,0.1)'),
                yaxis=dict(title='PRIORITY SCORE',range=[0,100],gridcolor='rgba(0,255,65,0.1)'),
                legend=dict(bgcolor='#000a00',bordercolor='rgba(0,255,65,0.2)',font=dict(size=9)),
                height=480,margin=dict(l=60,r=20,t=20,b=60))
            st.plotly_chart(fig,use_container_width=True)
            st.markdown("### `TOP 25 RS`")
            top25=scan.nlargest(25,'rs_rank')[['ticker','name','sector','region','price','dpct','rsi','rs_rank','stage','score','buy']]
            st.dataframe(top25.rename(columns={'ticker':'TICKER','name':'NAVN','sector':'SEKTOR','region':'REGION',
                'price':'PRIS','dpct':'1D%','rsi':'RSI','rs_rank':'RS','stage':'STG','score':'SCORE','buy':'SIGNAL'})
                .style.applymap(sig_style,subset=['SIGNAL'])
                .format({'PRIS':'{:.2f}','1D%':'{:+.1f}%','RSI':'{:.1f}','SCORE':'{:.0f}'}),
                use_container_width=True,hide_index=True)

    # ═══════════════════════════════════════════
    # TAB 8: PLAYBOOK / BOG
    # ═══════════════════════════════════════════
    with tab8:
        st.markdown("# `▸ TRADING TERMINAL – PLAYBOOK`")
        st.markdown("<div style='color:#005f12;font-family:Share Tech Mono;font-size:0.8rem'>Alt du behøver at vide om algoritmen, signalerne og hvordan du bruger terminalen</div>",unsafe_allow_html=True)
        st.markdown("---")

        sections = st.tabs(["📊 ALGORITMEN","🎯 SIGNALER","📈 SETUP STATES","⚠️ RISK","🌍 MARKED REGIME","💡 SÅDAN BRUGER DU DEN","📚 ORDLISTE"])
        s1,s2,s3,s4,s5,s6,s7 = sections

        with s1:
            st.markdown("## `ALGORITMEN – PRIORITY SCORE`")
            st.markdown("""
<div style='font-family:Share Tech Mono;font-size:0.82rem;color:#00cc33;line-height:1.8'>

<span style='color:#00ff41;font-size:0.9rem'>◆ HVAD ER PRIORITY SCORE?</span><br>
Priority Score er en samlet vurdering fra 0-100 der fortæller dig hvor interessant en aktie er som momentum-kandidat.
Den er bygget op af tre komponenter:

<br><br>
<span style='color:#00ff41'>PriorityScore = TrendScore + SetupScore − RiskPenalty</span>
<br><br>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ffaa00'>[ TRENDSCORE – max 72 point ]</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Måler styrken af den overordnede trend:

  +24  →  Pris over SMA200 (langsigtet uptrend)
  +18  →  SMA20 over SMA60 (mellemsigtet trend op)
  +10  →  Pris over SMA20 (kortsigtet styrke)
  +12  →  RS Trend = UP (outperformer lokalt indeks)
  + 8  →  Higher Low (lavere bunde stiger = akkumulation)
  +10  →  InstFlowScore / 10 (institutionel strøm, max 10p)
  ───
  MAX: 82 → begrænset til 72 i praksis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#0088ff'>[ SETUPSCORE – max 100 point ]</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Måler kvaliteten af det tekniske setup:

  +20  →  Accumulation (RSI 38-64, tæt på SMA20, volumen OK)
  + 6  →  Tight Action (ATR20/pris ≤ 4.5% – lav volatilitet)
  +18  →  Institutional Build (akkumulation + institutionel flow)
  +22  →  Breakout Ready (tæt på 20-dages high, volumen, RSI 44-78)
  +16  →  Momentum Active (breakout + volumen + RSI 50-80)
  + 6  →  Squeeze (ATR5 < ATR20 × 0.78 – energi bygger op)
  + 6  →  RSI 46-72 (hverken overkøbt eller oversolgt)
  + 6  →  DistHigh20 ≤ 7% (tæt på modstand)
  + 6  →  VolRatio ≥ 0.95 (volumen mindst normalt)
  +10  →  LiquidityScore / 10 (likviditetskvalitet, max 10p)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ff3333'>[ RISKPENALTY – trækkes fra ]</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Straffer aktier med høj risiko:

  −14  →  Ingen likviditet (AvgVol < 200k eller DollarVol < 8M)
  −10  →  RISK_OFF marked
  − 6  →  RS Trend = DOWN (underperformer lokalt indeks)
  − 8  →  Extended (RSI > 84 eller pris > SMA20 × 1.14)
  − 6  →  CapRisk (dollarvolumen < 25M)
  − 8  →  Weakening (2+ svaghedstegn)
  −14  →  Failed Setup (3+ svaghedstegn + RSI < 42)

</div>
""", unsafe_allow_html=True)

        with s2:
            st.markdown("## `SIGNALER – HVAD BETYDER DE?`")
            signals = [
                ("BUY NOW", "#00ff41", "003300",
                 "Momentum er aktivt. Volumen bekræfter. Breakout sker nu.",
                 "Bedst i RISK_ON marked. Brug tæt stop under Low5 eller 1.5×ATR20 fra pris.",
                 "RSI falder under 50. Pris lukker under Low5."),
                ("BUY BREAKOUT", "#00cc33", "002200",
                 "Aktien er tæt på eller bryder igennem 20-dages modstand med volumen.",
                 "Køb ved breakout med volumenbekræftelse. Stop under SMA20.",
                 "Falsk breakout – pris vender tilbage under modstand."),
                ("BUILD POSITION", "#0088ff", "001133",
                 "Institutionel akkumulation er i gang. Setup er klar men breakout ikke sket endnu.",
                 "Start med lille position. Tilføj ved breakout-bekræftelse.",
                 "Pris lukker under max(Low5, SMA20 − 0.5×ATR20)."),
                ("STARTER BUY", "#00aaff", "001122",
                 "Tidlig akkumulation. Trend er op men setup ikke fuldt modnet.",
                 "Brug lille startposition. Vent på bedre setup inden du tilføjer.",
                 "Pris lukker under SMA20."),
                ("EXTENDED — WAIT", "#ffaa00", "221100",
                 "Aktien er strakt for langt fra SMA20. RSI > 84 eller pris > SMA20 × 1.14.",
                 "Tilføj IKKE ny position. Hold eksisterende. Vent på reset til SMA20.",
                 "—"),
                ("REDUCE", "#ff6600", "221100",
                 "Setup svækkes. 2+ negative faktorer er til stede.",
                 "Reducer position. Skrap de svageste dele.",
                 "Yderligere svaghed bekræfter EXIT."),
                ("EXIT", "#ff3333", "330000",
                 "Setup er brudt ned. 3+ negative faktorer. RSI < 42 eller pris under Low5.",
                 "Luk position. Rationalisér ikke.",
                 "—"),
                ("WATCHLIST", "#336633", "050505",
                 "Aktien er interessant men ikke klar endnu. Ingen aktiv setup.",
                 "Overvåg. Sæt alarm hvis score stiger over 65.",
                 "—"),
            ]
            for sig,col,bg,meaning,action,invalidation in signals:
                st.markdown(f"""
<div style='background:#{bg};border:1px solid {col};border-left:4px solid {col};padding:12px 16px;margin:8px 0;font-family:Share Tech Mono'>
<span style='color:{col};font-size:0.9rem;font-weight:700'>{sig}</span><br>
<span style='color:#00cc33;font-size:0.78rem'>▸ Hvad:       </span><span style='color:#aaa;font-size:0.78rem'>{meaning}</span><br>
<span style='color:#00cc33;font-size:0.78rem'>▸ Hvad gør du:</span><span style='color:#00ff41;font-size:0.78rem'> {action}</span><br>
{"<span style='color:#00cc33;font-size:0.78rem'>▸ Invalideret: </span><span style='color:#ff6600;font-size:0.78rem'>" + invalidation + "</span>" if invalidation != "—" else ""}
</div>""", unsafe_allow_html=True)

        with s3:
            st.markdown("## `SETUP STATES – AKTIENS TILSTAND`")
            st.markdown("""
<div style='font-family:Share Tech Mono;font-size:0.82rem;color:#00cc33;line-height:2'>

Setup State er det tekniske stadie aktien befinder sig i – forskelligt fra Buy Signal.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<span style='color:#00ff41'>MOMENTUM_ACTIVE</span>
Alle faktorer er grønne. Volumen bekræfter. Breakout sker nu.
→ Signal: BUY NOW (eller STARTER BUY i RISK_OFF)

<span style='color:#00cc33'>BREAKOUT_READY</span>
Aktien er tæt på 20-dages high. Setup er klar. Afventer volumen.
→ Signal: BUY BREAKOUT

<span style='color:#0088ff'>INSTITUTIONAL_BUILD</span>
Institutionel akkumulation i gang. Higher lows. Volumen stiger stille.
→ Signal: BUILD POSITION

<span style='color:#00aaff'>ACCUMULATION</span>
Tidlig fase. RSI 38-64. Pris konsoliderer tæt på SMA20.
→ Signal: STARTER BUY

<span style='color:#ffaa00'>EXTENDED</span>
Pris er for langt fra SMA20 (>14%) eller RSI over 84.
→ Signal: EXTENDED — WAIT (tilføj ikke)

<span style='color:#ff6600'>WEAKENING</span>
2+ svaghedstegn: pris under SMA20, SMA20 under SMA60, RS DOWN.
→ Signal: REDUCE

<span style='color:#ff3333'>FAILED_SETUP</span>
Setup er brudt. 3+ svaghedstegn + lav RSI eller pris under Low5.
→ Signal: EXIT

<span style='color:#336633'>NO_SETUP</span>
Ingen aktiv teknisk setup. Aktien er på hold.
→ Signal: WATCHLIST

</div>
""", unsafe_allow_html=True)

        with s4:
            st.markdown("## `RISK MANAGEMENT`")
            st.markdown("""
<div style='font-family:Share Tech Mono;font-size:0.82rem;color:#00cc33;line-height:1.9'>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ff3333'>STOP LEVELS – AUTOMATISK BEREGNET</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Hvert signal har sit eget stop-niveau:

  MOMENTUM_ACTIVE:      Stop = max(Low5, Pris − 1.5 × ATR20)
  INSTITUTIONAL_BUILD:  Stop = max(Low5, SMA20 − 0.5 × ATR20)
  BREAKOUT_READY:       Stop = SMA20
  ACCUMULATION:         Stop = SMA20
  Andre:                Stop = SMA20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ffaa00'>NØGLEPARAMETRE DU SKAL KENDE</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ATR20:     Average True Range 20 dage – måler daglig volatilitet
             Jo højere ATR%, jo større stop skal du have
             
  VolRatio:  Dagens volumen / 20-dages gennemsnit
             > 1.5 = høj institutionel interesse
             < 0.8 = svag interesse
             
  RVOL50:    Volumen vs 50-dages gennemsnit
             Bekræfter langsigtet volumenmønster
             
  DistHigh20: Afstand til 20-dages høj i %
             < 3% = breakout-zone
             > 7% = for langt fra modstand
             
  Squeeze ⚡: ATR5 < ATR20 × 0.78
             Energi bygger op. Breakout nært forestående.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#00ff41'>POSITION SIZING – TOMMELFINGERREGEL</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  STARTER BUY:     0.5–1% af portefølje
  BUILD POSITION:  1–2% af portefølje
  BUY BREAKOUT:    2–3% af portefølje
  BUY NOW:         2–4% af portefølje (kun RISK_ON)
  
  Max enkelt position: 5–8% af portefølje
  Max sektor eksponering: 20–25%

</div>
""", unsafe_allow_html=True)

        with s5:
            st.markdown("## `MARKED REGIME`")
            st.markdown("""
<div style='font-family:Share Tech Mono;font-size:0.82rem;color:#00cc33;line-height:1.9'>

Marked Regime er terminalens makro-filter. Det bestemmer om vi er i et godt eller dårligt
miljø for momentum-trading. Det påvirker:
  1. RiskPenalty (+10 i RISK_OFF)
  2. Signal downgrade (BUILD/BREAKOUT → STARTER i RISK_OFF)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#00ff41'>▲ RISK_ON  (score ≥ 6)</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alle signaler aktive. BUY NOW og BUY BREAKOUT er fuldt aktive.
Momentum-strategier virker bedst i dette miljø.

Typiske tegn:
  • SPY/QQQ/IWM stiger dagligt
  • VIX under 18 og faldende
  • Mere end 55% af aktier over SMA20
  • Mange buy-signaler i scanneren

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ffaa00'>◆ NEUTRAL  (score 1-5)</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Mixed marked. Vær selektiv. Fokus på de stærkeste kandidater.
Reducer positionsstørrelser med 25-50%.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ff3333'>▼ RISK_OFF  (score ≤ 0)</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Defensivt marked. BUILD og BREAKOUT downgraders til STARTER.
Reducer eksponering. Fokus på kapitalbevarelse.

Typiske tegn:
  • SPY/QQQ i downtrend
  • VIX over 28
  • Under 40% af aktier over SMA20
  • Primært WATCHLIST/EXIT signaler

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#00cc33'>REGIME SCORING (hvordan den beregnes)</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  SPY/QQQ/IWM 6M trend:  +/-1 hver
  SPY/QQQ daglig >0.5%:  +2/+1
  VIX niveau:            +2 (<15) til -3 (>35)
  VIX retning faldende:  +2 (>5% fald i dag)
  % aktier over SMA20:   +2 (≥55%) eller -2 (<40%)
  % aktier over SMA200:  +2 (≥50%) eller -2 (<35%)
  Antal buy-signaler:    +1 (≥5) eller -1 (=0)

</div>
""", unsafe_allow_html=True)

        with s6:
            st.markdown("## `SÅDAN BRUGER DU TERMINALEN`")
            st.markdown("""
<div style='font-family:Share Tech Mono;font-size:0.82rem;color:#00cc33;line-height:1.9'>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#00ff41'>DAGLIG RUTINE (5-10 minutter)</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. Åbn FORSIDE
     → Tjek Marked Regime (RISK_ON/NEUTRAL/RISK_OFF)
     → Se VIX – stiger eller falder det?
     → Scan Top Kandidater – hvilke sektorer er stærke?
  
  2. Tjek TOP 10 OP/NED
     → Er der mønster? (fx alle energi-aktier stiger)
     → Er der aktier du følger?
  
  3. Åbn SCANNER
     → Sorter på PriorityScore
     → Filtrér på BUY BREAKOUT eller BUY NOW
     → Tjek Stage 2 filter for Weinstein
  
  4. Tjek POSITIONER
     → Er nogen aktier ved stop?
     → Er der REDUCE eller EXIT signaler?
  
  5. CHARTS for specifikke kandidater
     → Bekræft visuelt hvad scanneren ser

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#ffaa00'>HVAD GØR DU I RISK_OFF?</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Reducer positioner der viser REDUCE signal
  • Luk positioner der viser EXIT signal
  • Tilføj IKKE nye store positioner
  • Brug STARTER BUY med halv normal størrelse
  • Hold mere cash end normalt (30-50%)
  • Fokus på defensive sektorer (Utilities, Healthcare)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#00ff41'>HVAD GØR DU I RISK_ON?</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • Følg BUY NOW og BUY BREAKOUT signaler aktivt
  • Byg positioner gradvist (STARTER → BUILD → FULL)
  • Brug trailing stop (SMA20 som guide)
  • Tilføj til vindere der holder over SMA20
  • Fokus på høj InstFlowScore (≥70) og RS Trend UP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<span style='color:#0088ff'>SÅDAN LÆSER DU SCANNER KOLONNER</span>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  PriorityScore:  Den vigtigste kolonne. Jo højere jo bedre.
  RS Trend:       UP = outperformer lokalt indeks (C25, DAX osv.)
  IFS:            InstFlowScore – institutionel interesse (>70 = godt)
  LS:             LiquidityScore – kan du handle den? (>60 = godt)
  TS/SS/RP:       TrendScore / SetupScore / RiskPenalty
  Stage:          Weinstein stage. S2 = uptrend, S4 = downtrend
  Squeeze ⚡:      Energi bygger op – breakout nært

</div>
""", unsafe_allow_html=True)

        with s7:
            st.markdown("## `ORDLISTE`")
            terms = [
                ("SMA20", "Simple Moving Average 20 dage", "Gennemsnitspris de seneste 20 handelsdage. Vigtig kortsigtede støtte/modstand."),
                ("SMA60", "Simple Moving Average 60 dage", "Mellemsigtet trend. SMA20 > SMA60 = uptrend."),
                ("SMA200", "Simple Moving Average 200 dage", "Langsigtet trend. Pris over SMA200 = LONG TREND."),
                ("RSI", "Relative Strength Index (14)", "Momentum-oscillator 0-100. Over 70 = overkøbt, under 30 = oversolgt. Optimal zone: 46-72."),
                ("ATR20", "Average True Range 20 dage", "Gennemsnitlig daglig prisrange. Bruges til stop-beregning."),
                ("VolRatio", "Volume Ratio", "Dagens volumen divideret med 20-dages gennemsnit. >1.5 = høj institutionel interesse."),
                ("RVOL50", "Relative Volume 50", "Dagens volumen vs 50-dages gennemsnit. Bekræfter langsigtet volumenmønster."),
                ("RS Trend", "Relative Strength Trend", "Sammenligner aktiens pris mod lokalt indeks (C25 for DK, DAX for DE osv.). UP = outperformer."),
                ("DistHigh20", "Distance to 20-day High", "Afstand fra aktuel pris til 20-dages høj i %. < 3% = breakout-zone."),
                ("Higher Low", "Higher Low", "Aktiens bunde (Low5) er højere end 20-dages lave bunde. Tegn på akkumulation."),
                ("Squeeze ⚡", "Volatility Squeeze", "ATR5 < ATR20 × 0.78. Lav volatilitet bygger op til stor bevægelse."),
                ("InstFlowScore", "Institutional Flow Score 0-100", "Sammenvejning af volumen, RS, RSI og prisstyrke. Måler institutionel interesse."),
                ("LiquidityScore", "Liquidity Score 0-100", "Kombinerer AvgVol20, DollarVol og VolRatio. Sikrer at aktien er handelbar."),
                ("IBD RS Rank", "Investor's Business Daily RS Rank 1-99", "Relativ 12-måneders performance vægtet: 40% seneste kvartal + 20% × 3 kvartaler. 99 = bedst."),
                ("Weinstein Stage", "Weinstein Stage Analysis", "S1=Bund, S2=Uptrend (køb her), S3=Top, S4=Downtrend (undgå)"),
                ("CapRisk", "Capitalization Risk", "DollarVol < 25M dagligt. Aktien er for illikvid til store positioner."),
            ]
            for term,full,explanation in terms:
                st.markdown(f"""
<div style='border-bottom:1px solid rgba(0,255,65,0.1);padding:8px 4px;font-family:Share Tech Mono;font-size:0.8rem'>
<span style='color:#00ff41;font-weight:700'>{term}</span>
<span style='color:#005f12;font-size:0.72rem'> — {full}</span><br>
<span style='color:#00cc33'>{explanation}</span>
</div>""", unsafe_allow_html=True)

if __name__=='__main__':
    main()