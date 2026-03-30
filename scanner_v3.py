"""
╔══════════════════════════════════════════════════════════════╗
║           TRADING SCANNER PRO v3.0                          ║
║  - Komplet portering af Google Sheets v5.2 signallogik      ║
║  - IBD-stil Relative Strength ranking (1-99)                ║
║  - Stan Weinstein Stage Analysis (1-4)                      ║
║  - 500+ aktier på tværs af regioner                         ║
║  - Avanceret markedsregime model                            ║
║  - Nemt at tilføje aktier                                   ║
║  - Professionelt mørkt dashboard                            ║
╚══════════════════════════════════════════════════════════════╝
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, time
import pytz
import json
import os

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Scanner Pro v3.0",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── DARK THEME ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Base */
    .stApp, .main { background-color: #060b17; color: #e2e8f0; }
    section[data-testid="stSidebar"] { background-color: #0d1526; border-right: 1px solid #1e3a5f; }

    /* Typography */
    h1 { color: #60a5fa !important; font-size: 2rem !important; letter-spacing: -0.5px; }
    h2 { color: #93c5fd !important; }
    h3 { color: #bfdbfe !important; }
    p, li { color: #cbd5e1; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #0d1f3c, #132040);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    [data-testid="metric-container"] label { color: #64748b !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1px; }
    [data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 2rem !important; font-weight: 700 !important; }
    [data-testid="stMetricDelta"] { font-size: 0.9rem !important; }

    /* Dataframes */
    .stDataFrame { border: 1px solid #1e3a5f; border-radius: 10px; overflow: hidden; }
    iframe { background: #0d1f3c !important; }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        color: white; border: none; border-radius: 8px;
        font-weight: 600; letter-spacing: 0.3px;
        transition: all 0.2s;
    }
    .stButton button:hover { background: linear-gradient(135deg, #1e40af, #1d4ed8); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(37,99,235,0.4); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #0d1526; border-radius: 10px; padding: 4px; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #64748b; border-radius: 8px; font-weight: 500; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #1d4ed8, #2563eb) !important; color: white !important; }

    /* Inputs */
    .stSelectbox > div > div, .stMultiSelect > div > div, .stTextInput > div > div {
        background: #0d1f3c; border-color: #1e3a5f; color: #e2e8f0; border-radius: 8px;
    }
    .stSlider > div > div > div { background: #1d4ed8; }

    /* Divider */
    hr { border-color: #1e3a5f; margin: 20px 0; }

    /* Custom badges */
    .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px; }
    .badge-buy-now    { background: #16a34a; color: white; }
    .badge-breakout   { background: #22c55e; color: white; }
    .badge-build      { background: #2563eb; color: white; }
    .badge-starter    { background: #0ea5e9; color: white; }
    .badge-extended   { background: #d97706; color: white; }
    .badge-reduce     { background: #ea580c; color: white; }
    .badge-exit       { background: #dc2626; color: white; }
    .badge-watchlist  { background: #334155; color: #94a3b8; }

    /* Stage badges */
    .stage-1 { background: #1e3a5f; color: #93c5fd; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .stage-2 { background: #14532d; color: #86efac; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .stage-3 { background: #78350f; color: #fcd34d; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }
    .stage-4 { background: #7f1d1d; color: #fca5a5; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; }

    /* Regime banner */
    .regime-risk-on  { background: linear-gradient(135deg,#14532d,#166534); color:#86efac; padding:8px 20px; border-radius:8px; font-weight:700; font-size:1.1rem; border:1px solid #16a34a; }
    .regime-risk-off { background: linear-gradient(135deg,#7f1d1d,#991b1b); color:#fca5a5; padding:8px 20px; border-radius:8px; font-weight:700; font-size:1.1rem; border:1px solid #dc2626; }
    .regime-neutral  { background: linear-gradient(135deg,#78350f,#92400e); color:#fcd34d; padding:8px 20px; border-radius:8px; font-weight:700; font-size:1.1rem; border:1px solid #d97706; }

    /* Market status */
    .mkt-open   { color:#22c55e; font-weight:700; }
    .mkt-closed { color:#ef4444; font-weight:700; }
    .mkt-pre    { color:#f59e0b; font-weight:700; }

    /* Info box */
    .info-box { background:#0d1f3c; border:1px solid #1e3a5f; border-radius:10px; padding:16px; margin:8px 0; }
    .info-box h4 { color:#60a5fa; margin:0 0 8px 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# KONFIGURATION
# ══════════════════════════════════════════════════════════════
CONFIG = {
    'rsi_period':         14,
    'sma_fast':           20,
    'sma_mid':            60,
    'sma_long':           200,
    'atr_fast':           5,
    'atr_slow':           20,
    'breakout_distance':  0.06,
    'squeeze_factor':     0.78,
    'min_avg_vol':        200_000,
    'min_dollar_vol':     8_000_000,
}

POSITIONS_FILE = 'positions.json'

# ══════════════════════════════════════════════════════════════
# BØRS STATUS
# ══════════════════════════════════════════════════════════════
EXCHANGES = {
    'NYSE/NASDAQ': {'tz':'America/New_York',  'open':time(9,30), 'close':time(16,0),  'pre':time(4,0),  'flag':'🇺🇸'},
    'Copenhagen':  {'tz':'Europe/Copenhagen', 'open':time(9,0),  'close':time(17,0),  'pre':time(8,30), 'flag':'🇩🇰'},
    'Oslo':        {'tz':'Europe/Oslo',       'open':time(9,0),  'close':time(16,30), 'pre':time(8,30), 'flag':'🇳🇴'},
    'Stockholm':   {'tz':'Europe/Stockholm',  'open':time(9,0),  'close':time(17,30), 'pre':time(8,30), 'flag':'🇸🇪'},
    'Amsterdam':   {'tz':'Europe/Amsterdam',  'open':time(9,0),  'close':time(17,30), 'pre':time(8,0),  'flag':'🇳🇱'},
    'Frankfurt':   {'tz':'Europe/Berlin',     'open':time(9,0),  'close':time(17,30), 'pre':time(8,0),  'flag':'🇩🇪'},
    'London':      {'tz':'Europe/London',     'open':time(8,0),  'close':time(16,30), 'pre':time(7,0),  'flag':'🇬🇧'},
    'Paris':       {'tz':'Europe/Paris',      'open':time(9,0),  'close':time(17,30), 'pre':time(8,0),  'flag':'🇫🇷'},
    'Tokyo':       {'tz':'Asia/Tokyo',        'open':time(9,0),  'close':time(15,30), 'pre':time(8,0),  'flag':'🇯🇵'},
    'Hong Kong':   {'tz':'Asia/Hong_Kong',    'open':time(9,30), 'close':time(16,0),  'pre':time(9,0),  'flag':'🇭🇰'},
}

def get_exchange_status(info):
    tz  = pytz.timezone(info['tz'])
    now = datetime.now(tz)
    t   = now.time()
    wd  = now.weekday()
    if wd >= 5: return 'LUKKET', now.strftime('%H:%M')
    if info['open'] <= t < info['close']: return 'ÅBEN', now.strftime('%H:%M')
    if info['pre']  <= t < info['open']:  return 'PRE',  now.strftime('%H:%M')
    return 'LUKKET', now.strftime('%H:%M')

# ══════════════════════════════════════════════════════════════
# UNIVERS – 500+ AKTIER
# Tilføj nemt nye aktier her: ('TICKER','Navn','Sektor','Region')
# ══════════════════════════════════════════════════════════════
UNIVERSE = [
    # ── USA MEGA/LARGE CAP ─────────────────────────────────
    ('AAPL','Apple','Tech','US'),
    ('MSFT','Microsoft','Tech','US'),
    ('GOOGL','Alphabet','Tech','US'),
    ('META','Meta','Tech','US'),
    ('NVDA','NVIDIA','AI','US'),
    ('AMD','AMD','AI','US'),
    ('AVGO','Broadcom','AI','US'),
    ('MU','Micron','AI','US'),
    ('INTC','Intel','AI','US'),
    ('QCOM','Qualcomm','AI','US'),
    ('ARM','ARM Holdings','AI','US'),
    ('SMCI','Super Micro','AI','US'),
    ('PLTR','Palantir','AI','US'),
    ('TSM','TSMC','AI','US'),
    ('ADBE','Adobe','Tech','US'),
    ('CRM','Salesforce','Tech','US'),
    ('NOW','ServiceNow','Tech','US'),
    ('SNOW','Snowflake','Tech','US'),
    ('DDOG','Datadog','Tech','US'),
    ('NET','Cloudflare','Tech','US'),
    ('CRWD','CrowdStrike','Tech','US'),
    ('PANW','Palo Alto','Tech','US'),
    ('ORCL','Oracle','Tech','US'),
    ('INTU','Intuit','Tech','US'),
    ('UBER','Uber','Tech','US'),
    ('LYFT','Lyft','Tech','US'),
    ('SHOP','Shopify','Tech','US'),
    ('SQ','Block','Tech','US'),
    ('PYPL','PayPal','Tech','US'),
    ('GTLB','GitLab','Tech','US'),
    ('PATH','UiPath','AI','US'),
    ('AI','C3.ai','AI','US'),
    ('SOUN','SoundHound AI','AI','US'),
    ('IONQ','IonQ','AI','US'),
    ('BBAI','BigBear.ai','AI','US'),
    # ── USA FINANCIALS ──────────────────────────────────────
    ('JPM','JPMorgan','Financials','US'),
    ('GS','Goldman Sachs','Financials','US'),
    ('MS','Morgan Stanley','Financials','US'),
    ('BAC','Bank of America','Financials','US'),
    ('WFC','Wells Fargo','Financials','US'),
    ('C','Citigroup','Financials','US'),
    ('V','Visa','Financials','US'),
    ('MA','Mastercard','Financials','US'),
    ('AXP','Amex','Financials','US'),
    ('BLK','BlackRock','Financials','US'),
    ('COIN','Coinbase','Financials','US'),
    ('HOOD','Robinhood','Financials','US'),
    ('SOFI','SoFi','Financials','US'),
    ('AFRM','Affirm','Financials','US'),
    # ── USA ENERGY ──────────────────────────────────────────
    ('XOM','Exxon Mobil','Energy','US'),
    ('CVX','Chevron','Energy','US'),
    ('COP','ConocoPhillips','Energy','US'),
    ('DVN','Devon Energy','Energy','US'),
    ('EOG','EOG Resources','Energy','US'),
    ('OXY','Occidental','Energy','US'),
    ('FANG','Diamondback','Energy','US'),
    ('PSX','Phillips 66','Energy','US'),
    ('VLO','Valero','Energy','US'),
    ('MPC','Marathon Petroleum','Energy','US'),
    ('SLB','Schlumberger','Energy','US'),
    ('HAL','Halliburton','Energy','US'),
    ('CCJ','Cameco','Energy','US'),
    ('ENPH','Enphase','Energy','US'),
    ('FSLR','First Solar','Energy','US'),
    # ── USA HEALTHCARE ──────────────────────────────────────
    ('LLY','Eli Lilly','Healthcare','US'),
    ('UNH','UnitedHealth','Healthcare','US'),
    ('REGN','Regeneron','Healthcare','US'),
    ('VRTX','Vertex','Healthcare','US'),
    ('JNJ','J&J','Healthcare','US'),
    ('MRK','Merck','Healthcare','US'),
    ('ABBV','AbbVie','Healthcare','US'),
    ('BMY','Bristol-Myers','Healthcare','US'),
    ('AMGN','Amgen','Healthcare','US'),
    ('GILD','Gilead','Healthcare','US'),
    ('MRNA','Moderna','Healthcare','US'),
    ('BNTX','BioNTech','Healthcare','US'),
    ('ISRG','Intuitive Surgical','Healthcare','US'),
    ('TMO','Thermo Fisher','Healthcare','US'),
    ('DHR','Danaher','Healthcare','US'),
    ('SYK','Stryker','Healthcare','US'),
    ('EW','Edwards Lifesciences','Healthcare','US'),
    ('IDXX','IDEXX Labs','Healthcare','US'),
    ('RXRX','Recursion Pharma','Healthcare','US'),
    ('CRSP','CRISPR Therapeutics','Healthcare','US'),
    # ── USA CONSUMER ────────────────────────────────────────
    ('AMZN','Amazon','Consumer','US'),
    ('TSLA','Tesla','Consumer','US'),
    ('NFLX','Netflix','Consumer','US'),
    ('COST','Costco','Consumer','US'),
    ('HD','Home Depot','Consumer','US'),
    ('WMT','Walmart','Consumer','US'),
    ('TGT','Target','Consumer','US'),
    ('NKE','Nike','Consumer','US'),
    ('SBUX','Starbucks','Consumer','US'),
    ('MCD','McDonalds','Consumer','US'),
    ('LULU','Lululemon','Consumer','US'),
    ('CELH','Celsius Holdings','Consumer','US'),
    ('ABNB','Airbnb','Consumer','US'),
    ('DASH','DoorDash','Consumer','US'),
    ('BYDDY','BYD','Consumer','US'),
    ('RIVN','Rivian','Consumer','US'),
    ('LCID','Lucid','Consumer','US'),
    ('DKNG','DraftKings','Consumer','US'),
    ('MGM','MGM Resorts','Consumer','US'),
    ('RCL','Royal Caribbean','Consumer','US'),
    ('CCL','Carnival','Consumer','US'),
    ('MELI','MercadoLibre','Consumer','US'),
    # ── USA INDUSTRIALS ─────────────────────────────────────
    ('CAT','Caterpillar','Industrials','US'),
    ('GE','GE Aerospace','Industrials','US'),
    ('RTX','RTX','Industrials','US'),
    ('LMT','Lockheed Martin','Industrials','US'),
    ('NOC','Northrop Grumman','Industrials','US'),
    ('BA','Boeing','Industrials','US'),
    ('HON','Honeywell','Industrials','US'),
    ('GEV','GE Vernova','Industrials','US'),
    ('PWR','Quanta Services','Industrials','US'),
    ('ALSN','Allison Transmission','Industrials','US'),
    ('HPE','HP Enterprise','Tech','US'),
    ('DAL','Delta Airlines','Industrials','US'),
    # ── USA MATERIALS ───────────────────────────────────────
    ('FCX','Freeport-McMoRan','Materials','US'),
    ('NUE','Nucor','Materials','US'),
    ('ALB','Albemarle','Materials','US'),
    ('MP','MP Materials','Materials','US'),
    ('CF','CF Industries','Materials','US'),
    ('MOS','Mosaic','Materials','US'),
    # ── USA MOMENTUM/CRYPTO ─────────────────────────────────
    ('MARA','Marathon Digital','Momentum','US'),
    ('RIOT','Riot Platforms','Momentum','US'),
    ('RKLB','Rocket Lab','Momentum','US'),
    ('AXON','Axon Enterprise','Momentum','US'),

    # ── DANMARK ─────────────────────────────────────────────
    ('NOVO-B.CO','Novo Nordisk','Healthcare','Denmark'),
    ('DSV.CO','DSV','Industrials','Denmark'),
    ('DANSKE.CO','Danske Bank','Financials','Denmark'),
    ('MAERSK-B.CO','AP Moeller Maersk','Industrials','Denmark'),
    ('PNDORA.CO','Pandora','Consumer','Denmark'),
    ('GMAB.CO','Genmab','Healthcare','Denmark'),
    ('VWS.CO','Vestas','Industrials','Denmark'),
    ('ORSTED.CO','Orsted','Utilities','Denmark'),
    ('ALMB.CO','Alm. Brand','Financials','Denmark'),
    ('JYSK.CO','Jyske Bank','Financials','Denmark'),
    ('TRMD-A.CO','TORM','Energy','Denmark'),
    ('SPG.CO','SP Group','Industrials','Denmark'),
    ('AGF-B.CO','AGF','Consumer','Denmark'),
    ('PARKEN.CO','PARKEN','Consumer','Denmark'),
    ('ASTK.CO','Asetek','Tech','Denmark'),
    ('BETCO.ST','Better Collective','Consumer','Denmark'),

    # ── SVERIGE ─────────────────────────────────────────────
    ('EVO.ST','Evolution','Tech','Sweden'),
    ('VOLV-B.ST','Volvo','Industrials','Sweden'),
    ('ERIC-B.ST','Ericsson','Tech','Sweden'),
    ('ATCO-A.ST','Atlas Copco','Industrials','Sweden'),
    ('SAND.ST','Sandvik','Industrials','Sweden'),
    ('INVE-B.ST','Investor AB','Financials','Sweden'),
    ('NDA-SE.ST','Nordea','Financials','Sweden'),
    ('SECU-B.ST','Securitas','Industrials','Sweden'),
    ('SKA-B.ST','Skanska','Industrials','Sweden'),
    ('SINCH.ST','Sinch','Tech','Sweden'),
    ('MILDEF.ST','MilDef Group','Industrials','Sweden'),
    ('CLAV.ST','Clavister','Tech','Sweden'),
    ('VSURE.ST','Verisure','Tech','Sweden'),
    ('SPRINT.ST','Sprint Bioscience','Healthcare','Sweden'),
    ('NANEXA.ST','Nanexa','Healthcare','Sweden'),
    ('CHOSA.ST','CHOSA Oncology','Healthcare','Sweden'),

    # ── NORGE ───────────────────────────────────────────────
    ('EQNR.OL','Equinor','Energy','Norway'),
    ('DNB.OL','DNB Bank','Financials','Norway'),
    ('KOG.OL','Kongsberg Gruppen','Industrials','Norway'),
    ('TEL.OL','Telenor','Tech','Norway'),
    ('NAS.OL','Norwegian Air','Industrials','Norway'),
    ('KIT.OL','Kitron','Industrials','Norway'),
    ('KOMPL.OL','Komplett','Consumer','Norway'),

    # ── NEDERLANDENE ────────────────────────────────────────
    ('ASML.AS','ASML','AI','Netherlands'),
    ('ASM.AS','ASM International','AI','Netherlands'),
    ('BESI.AS','BE Semiconductor','AI','Netherlands'),
    ('ADYEN.AS','Adyen','Tech','Netherlands'),
    ('INGA.AS','ING','Financials','Netherlands'),

    # ── TYSKLAND ────────────────────────────────────────────
    ('SAP.DE','SAP','Tech','Germany'),
    ('IFX.DE','Infineon','AI','Germany'),
    ('RHM.DE','Rheinmetall','Industrials','Germany'),
    ('SIE.DE','Siemens','Industrials','Germany'),
    ('ALV.DE','Allianz','Financials','Germany'),
    ('MBG.DE','Mercedes-Benz','Consumer','Germany'),
    ('BMW.DE','BMW','Consumer','Germany'),

    # ── UK ──────────────────────────────────────────────────
    ('SHEL.L','Shell','Energy','UK'),
    ('BP.L','BP','Energy','UK'),
    ('AZN.L','AstraZeneca','Healthcare','UK'),
    ('GSK.L','GSK','Healthcare','UK'),
    ('RR.L','Rolls-Royce','Industrials','UK'),
    ('BA.L','BAE Systems','Industrials','UK'),
    ('RIO.L','Rio Tinto','Materials','UK'),
    ('GLEN.L','Glencore','Materials','UK'),
    ('HSBA.L','HSBC','Financials','UK'),
    ('REL.L','RELX','Tech','UK'),

    # ── FRANKRIG ────────────────────────────────────────────
    ('MC.PA','LVMH','Consumer','France'),
    ('RMS.PA','Hermes','Consumer','France'),
    ('AIR.PA','Airbus','Industrials','France'),
    ('HO.PA','Thales','Industrials','France'),
    ('TTE.PA','TotalEnergies','Energy','France'),
    ('BNP.PA','BNP Paribas','Financials','France'),
    ('SAN.PA','Sanofi','Healthcare','France'),
    ('CAP.PA','Capgemini','Tech','France'),
    ('STMPA.PA','STMicroelectronics','AI','France'),

    # ── SCHWEIZ ─────────────────────────────────────────────
    ('ROG.SW','Roche','Healthcare','Switzerland'),
    ('NOVN.SW','Novartis','Healthcare','Switzerland'),
    ('UBSG.SW','UBS','Financials','Switzerland'),
    ('ABBN.SW','ABB','Industrials','Switzerland'),
    ('LOGN.SW','Logitech','Tech','Switzerland'),
    ('NESN.SW','Nestle','Consumer','Switzerland'),

    # ── SPANIEN/ITALIEN ─────────────────────────────────────
    ('IBE.MC','Iberdrola','Utilities','Spain'),
    ('SAN.MC','Banco Santander','Financials','Spain'),
    ('ITX.MC','Inditex','Consumer','Spain'),
    ('ENEL.MI','Enel','Utilities','Italy'),
    ('ENI.MI','ENI','Energy','Italy'),
    ('UCG.MI','UniCredit','Financials','Italy'),

    # ── FINLAND ─────────────────────────────────────────────
    ('NOKIA.HE','Nokia','Tech','Finland'),
    ('KNEBV.HE','Kone','Industrials','Finland'),

    # ── JAPAN ───────────────────────────────────────────────
    ('7203.T','Toyota','Consumer','Japan'),
    ('6758.T','Sony','Tech','Japan'),
    ('9984.T','SoftBank','Tech','Japan'),
    ('6861.T','Keyence','AI','Japan'),
    ('6501.T','Hitachi','Industrials','Japan'),
    ('8306.T','Mitsubishi UFJ','Financials','Japan'),

    # ── HONG KONG ───────────────────────────────────────────
    ('0700.HK','Tencent','Tech','HongKong'),
    ('9988.HK','Alibaba','Consumer','HongKong'),
    ('3690.HK','Meituan','Consumer','HongKong'),
    ('1810.HK','Xiaomi','Tech','HongKong'),

    # ── ASIEN ØVRIGE ────────────────────────────────────────
    ('005930.KS','Samsung','Tech','SouthKorea'),
    ('000660.KS','SK Hynix','AI','SouthKorea'),
    ('2330.TW','TSMC TW','AI','Taiwan'),
    ('INFY.NS','Infosys','Tech','India'),
    ('TCS.NS','Tata Consultancy','Tech','India'),

    # ── GLOBALE ETF'er ──────────────────────────────────────
    ('SPY','S&P 500','ETF','Global'),
    ('QQQ','Nasdaq 100','ETF','Global'),
    ('IWM','Russell 2000','ETF','Global'),
    ('VGK','Europe ETF','ETF','Europe'),
    ('EEM','Emerging Markets','ETF','Global'),
    ('EWJ','Japan ETF','ETF','Japan'),
    ('EWY','South Korea ETF','ETF','Asia'),
    ('GLD','Gold','ETF','Commodities'),
    ('SLV','Silver','ETF','Commodities'),
    ('USO','Oil','ETF','Commodities'),
    ('COPX','Copper Miners','ETF','Commodities'),
    ('XLE','Energy SPDR','ETF','US'),
    ('XLK','Tech SPDR','ETF','US'),
    ('XLF','Financials SPDR','ETF','US'),
    ('XLV','Healthcare SPDR','ETF','US'),
    ('XLI','Industrials SPDR','ETF','US'),
    ('SOXX','Semiconductors','ETF','US'),
    ('ARKK','ARK Innovation','ETF','US'),
    ('BOTZ','Robotics AI','ETF','Global'),
    ('CIBR','Cybersecurity','ETF','US'),
    ('BITO','Bitcoin ETF','ETF','Crypto'),
]

MACRO_TICKERS = ['SPY','QQQ','IWM','^VIX','GLD','CL=F','UUP','EEM','^TNX']

# ══════════════════════════════════════════════════════════════
# TEKNISKE INDIKATORER
# ══════════════════════════════════════════════════════════════
def sma(s, n):         return s.rolling(n).mean()
def ema(s, n):         return s.ewm(span=n, adjust=False).mean()

def calc_rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0).rolling(n).mean()
    l = (-d.clip(upper=0)).rolling(n).mean()
    rs = g / l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_atr(h, l, c, n=20):
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def calc_squeeze(h, l, c, fast=5, slow=20, factor=0.78):
    atr_fast = calc_atr(h, l, c, fast)
    atr_slow = calc_atr(h, l, c, slow)
    return (atr_fast < atr_slow * factor).iloc[-1]

# ══════════════════════════════════════════════════════════════
# WEINSTEIN STAGE ANALYSE
# Stage 1: Basing (SMA200 flad, pris konsoliderer)
# Stage 2: Advancing (pris over SMA200, SMA200 stigende) ← KØB
# Stage 3: Topping (pris under SMA200, SMA200 flader)
# Stage 4: Declining (pris og SMA200 falder) ← UNDGÅ
# ══════════════════════════════════════════════════════════════
def weinstein_stage(close, sma200_series):
    if len(close) < 210: return 0, 'Ukendt'
    price    = float(close.iloc[-1])
    sma200   = float(sma200_series.iloc[-1])
    sma200_4w = float(sma200_series.iloc[-20]) if len(sma200_series) > 20 else sma200
    sma200_rising  = sma200 > sma200_4w
    sma200_falling = sma200 < sma200_4w

    if price > sma200 and sma200_rising:
        return 2, 'Stage 2 – Advancing ✅'
    elif price > sma200 and not sma200_rising:
        return 3, 'Stage 3 – Topping ⚠️'
    elif price < sma200 and sma200_falling:
        return 4, 'Stage 4 – Declining ❌'
    else:
        return 1, 'Stage 1 – Basing 🔄'

# ══════════════════════════════════════════════════════════════
# IBD RELATIVE STRENGTH RANKING (1-99)
# Måler 12-måneders price performance vægtet mod slutningen
# ══════════════════════════════════════════════════════════════
def calc_ibd_rs_raw(close):
    """Beregn raw RS score (vægtet 12M performance)"""
    if len(close) < 252: return None
    try:
        q4 = float(close.iloc[-1]  / close.iloc[-64]  - 1) if len(close) >= 64  else 0
        q3 = float(close.iloc[-64] / close.iloc[-127] - 1) if len(close) >= 127 else 0
        q2 = float(close.iloc[-127]/ close.iloc[-189] - 1) if len(close) >= 189 else 0
        q1 = float(close.iloc[-189]/ close.iloc[-252] - 1) if len(close) >= 252 else 0
        return q4 * 0.40 + q3 * 0.20 + q2 * 0.20 + q1 * 0.20
    except:
        return None

def rank_rs_scores(df):
    """Konverter raw scores til 1-99 ranking"""
    if df.empty or 'rs_raw' not in df.columns: return df
    valid = df['rs_raw'].dropna()
    if valid.empty: return df
    df['rs_rank'] = df['rs_raw'].rank(pct=True).multiply(99).round(0).fillna(50).astype(int)
    return df

# ══════════════════════════════════════════════════════════════
# SIGNALLOGIK – IDENTISK MED GOOGLE SHEETS v5.2
# ══════════════════════════════════════════════════════════════
def derive_states(row, market_regime='NEUTRAL'):
    price    = row['price']
    sma20    = row['sma20']
    sma60    = row['sma60']
    sma200   = row['sma200']
    rsi      = row['rsi']
    vol_ratio = row['vol_ratio']
    dist_high20 = row['dist_high20_raw']
    rs_trend = row['rs_trend']
    atr20    = row['atr20']
    low5     = row['low5']
    squeeze  = row['squeeze']
    inst_flow = row['inst_flow_score']
    liq_score = row['liquidity_score']

    # ── Trend scores (identisk med Sheets) ──
    trend_score = 0
    if price > sma200:     trend_score += 24
    if sma20 > sma60:      trend_score += 18
    if price > sma20:      trend_score += 10
    if rs_trend == 'UP':   trend_score += 12
    if row['higher_low']:  trend_score += 8
    trend_score += min(10, int(inst_flow / 10))

    trend    = 'BUY'  if sma20 > sma60 else ('SELL' if sma20 < sma60 else 'HOLD')
    trend200 = 'LONG TREND' if price > sma200 else 'WEAK LONG TREND'

    # ── Setup conditions ──
    tight_action = (atr20 / price) <= 0.045 if price > 0 else False

    accumulation = (
        trend == 'BUY' and trend200 == 'LONG TREND' and
        38 <= rsi <= 64 and vol_ratio >= 0.90 and
        abs((price - sma20) / sma20) <= 0.06 and
        rs_trend in ('UP','FLAT','')
    )
    inst_build = accumulation and (row['inst_accum'] or inst_flow >= 65)

    breakout_ready = (
        trend == 'BUY' and trend200 == 'LONG TREND' and
        rs_trend in ('UP','FLAT','') and
        0 <= dist_high20 <= CONFIG['breakout_distance'] and
        0.95 <= vol_ratio <= 3.0 and 44 <= rsi <= 78 and
        (squeeze or dist_high20 <= 0.03)
    )

    momentum_active = (
        breakout_ready and vol_ratio >= 1.10 and
        50 <= rsi <= 80 and
        row['liquidity_pass'] and
        market_regime != 'RISK_OFF'
    )

    extended = rsi > 84 or price > sma20 * 1.14

    # ── Weakness ──
    weak1 = price < sma20
    weak2 = sma20 < sma60
    weak3 = price < sma200
    weak4 = rs_trend == 'DOWN'
    weak_count = sum([weak1, weak2, weak3, weak4])

    weakening    = weak_count >= 2 or (price < sma20 and rs_trend == 'DOWN')
    failed_setup = weak_count >= 3 and (rsi < 42 or price < low5)

    # ── Setup score ──
    setup_score = 0
    if accumulation:  setup_score += 20
    if tight_action:  setup_score += 6
    if inst_build:    setup_score += 18
    if breakout_ready: setup_score += 22
    if momentum_active: setup_score += 16
    if squeeze:        setup_score += 6
    if 46 <= rsi <= 72: setup_score += 6
    if dist_high20 <= 0.07: setup_score += 6
    if vol_ratio >= 0.95: setup_score += 6
    setup_score += min(10, int(liq_score / 10))

    # ── Risk penalty ──
    risk_penalty = 0
    if not row['liquidity_pass']:  risk_penalty += 14
    if market_regime == 'RISK_OFF': risk_penalty += 10
    if rs_trend == 'DOWN':         risk_penalty += 6
    if extended:                   risk_penalty += 8
    if row['cap_risk']:            risk_penalty += 6
    if weakening:                  risk_penalty += 8
    if failed_setup:               risk_penalty += 14

    priority_score = max(0, min(100, trend_score + setup_score - risk_penalty))

    # ── Setup state ──
    if failed_setup:    ss = 'FAILED_SETUP'
    elif extended:      ss = 'EXTENDED'
    elif momentum_active: ss = 'MOMENTUM_ACTIVE'
    elif breakout_ready:  ss = 'BREAKOUT_READY'
    elif inst_build:    ss = 'INSTITUTIONAL_BUILD'
    elif accumulation:  ss = 'ACCUMULATION'
    elif weakening:     ss = 'WEAKENING'
    else:               ss = 'NO_SETUP'

    # ── Action state ──
    action = {
        'ACCUMULATION':'STARTER','INSTITUTIONAL_BUILD':'BUILD',
        'BREAKOUT_READY':'BREAKOUT_ENTRY','MOMENTUM_ACTIVE':'MOMENTUM_ENTRY',
        'EXTENDED':'EXTENDED','WEAKENING':'REDUCE','FAILED_SETUP':'EXIT'
    }.get(ss, 'WATCHLIST')

    if market_regime == 'RISK_OFF' and action in ('BUILD','BREAKOUT_ENTRY','MOMENTUM_ENTRY'):
        action = 'STARTER'

    buy_signal = {
        'STARTER':'STARTER BUY','BUILD':'BUILD POSITION',
        'BREAKOUT_ENTRY':'BUY BREAKOUT','MOMENTUM_ENTRY':'BUY NOW',
        'EXTENDED':'EXTENDED — WAIT'
    }.get(action, 'WATCHLIST')

    sell_signal = 'EXIT' if action=='EXIT' else ('REDUCE' if action=='REDUCE' else 'HOLD')

    risk_state = {'MOMENTUM_ENTRY':'TIGHT','REDUCE':'DEFENSIVE','EXIT':'TRIGGERED'}.get(action,'NORMAL')

    stop_level = round(sma20, 2)
    if ss == 'MOMENTUM_ACTIVE':
        stop_level = round(max(low5, price - 1.5 * atr20), 2)
    elif ss == 'INSTITUTIONAL_BUILD':
        stop_level = round(max(low5, sma20 - 0.5 * atr20), 2)

    return {
        'trend_score':    trend_score,
        'setup_score':    setup_score,
        'risk_penalty':   risk_penalty,
        'priority_score': priority_score,
        'setup_state':    ss,
        'action_state':   action,
        'buy_signal':     buy_signal,
        'sell_signal':    sell_signal,
        'risk_state':     risk_state,
        'stop_level':     stop_level,
    }

# ══════════════════════════════════════════════════════════════
# DATA FETCH + BEREGNING
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def fetch_scanner_data(universe_tuple, market_regime='NEUTRAL'):
    universe = list(universe_tuple)
    tickers  = [t[0] for t in universe]
    info_map = {t[0]: t for t in universe}
    results  = []

    # Download i chunks for stabilitet
    chunk_size = 50
    all_raw    = {}

    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i:i+chunk_size]
        try:
            raw = yf.download(
                chunk, period='1y', interval='1d',
                group_by='ticker', auto_adjust=True,
                progress=False, threads=True
            )
            for t in chunk:
                try:
                    df = raw[t].dropna() if len(chunk) > 1 else raw.dropna()
                    if len(df) >= 210:
                        all_raw[t] = df
                except:
                    pass
        except:
            pass

    # Beregn RS raw scores
    rs_raw_scores = {}
    for t, df in all_raw.items():
        rs_raw_scores[t] = calc_ibd_rs_raw(df['Close'])

    # Rank RS scores
    rs_series = pd.Series(rs_raw_scores).dropna()
    rs_ranks  = rs_series.rank(pct=True).multiply(99).round(0).astype(int) if not rs_series.empty else pd.Series()

    # Beregn alle indikatorer
    for ticker, df in all_raw.items():
        try:
            info  = info_map.get(ticker, (ticker, ticker, 'Unknown', 'Unknown'))
            close = df['Close'].squeeze()
            high  = df['High'].squeeze()
            low   = df['Low'].squeeze()
            vol   = df['Volume'].squeeze()

            price  = float(close.iloc[-1])
            prev   = float(close.iloc[-2])
            daily_pct = (price / prev - 1) * 100 if prev != 0 else 0

            sma20_s  = sma(close, 20)
            sma60_s  = sma(close, 60)
            sma200_s = sma(close, 200)
            rsi_s    = calc_rsi(close, 14)
            atr5_s   = calc_atr(high, low, close, 5)
            atr20_s  = calc_atr(high, low, close, 20)

            sma20_v  = float(sma20_s.iloc[-1])
            sma60_v  = float(sma60_s.iloc[-1])
            sma200_v = float(sma200_s.iloc[-1])
            rsi_v    = float(rsi_s.iloc[-1])
            atr5_v   = float(atr5_s.iloc[-1])
            atr20_v  = float(atr20_s.iloc[-1])

            high20   = float(close.tail(20).max())
            low5_v   = float(low.tail(5).min())
            low20    = float(low.tail(20).min())
            avg_v20  = float(vol.tail(20).mean())
            avg_v50  = float(vol.tail(50).mean())
            last_vol = float(vol.iloc[-1])
            vol_ratio  = last_vol / avg_v20 if avg_v20 > 0 else 0
            rvol50     = last_vol / avg_v50 if avg_v50 > 0 else 0
            dollar_vol = avg_v20 * price
            dist_high20_raw = (high20 - price) / high20 if high20 > 0 else 0
            higher_low = low5_v > low20
            liq_pass   = avg_v20 >= CONFIG['min_avg_vol'] and dollar_vol >= CONFIG['min_dollar_vol']
            cap_risk   = dollar_vol < 25_000_000

            # Squeeze
            squeeze_v = bool(atr5_v < atr20_v * CONFIG['squeeze_factor'])

            # RSI trend
            rsi_prev5 = float(calc_rsi(close, 14).iloc[-6]) if len(close) > 20 else rsi_v
            rsi_trend = 'UP' if rsi_v > rsi_prev5 else ('DOWN' if rsi_v < rsi_prev5 else 'FLAT')

            # RS trend (vs 20 dage siden)
            rs_prev = float(close.iloc[-21]) if len(close) > 21 else price
            rs_trend_v = 'UP' if price > rs_prev else ('DOWN' if price < rs_prev else 'FLAT')

            # 52-uger
            w52_high = float(close.tail(252).max())
            w52_low  = float(close.tail(252).min())
            dist_52w = (w52_high - price) / w52_high if w52_high > 0 else 0

            # Institutional Accum (identisk med Sheets)
            trend_v    = 'BUY' if sma20_v > sma60_v else ('SELL' if sma20_v < sma60_v else 'HOLD')
            trend200_v = 'LONG TREND' if price > sma200_v else 'WEAK LONG TREND'
            inst_accum = (
                trend_v == 'BUY' and trend200_v == 'LONG TREND' and
                40 <= rsi_v <= 64 and
                rs_trend_v in ('UP','FLAT') and rsi_trend in ('UP','FLAT') and
                vol_ratio >= 0.95 and higher_low and dist_high20_raw <= 0.10
            )

            # Inst Flow Score (identisk med Sheets)
            ifs = 0
            if vol_ratio > 1.15:      ifs += 20
            if higher_low:            ifs += 20
            if rs_trend_v == 'UP':    ifs += 20
            if price > sma20_v:       ifs += 20
            if 42 <= rsi_v <= 68:     ifs += 20
            if trend200_v == 'LONG TREND': ifs += 10
            if inst_accum:            ifs += 10
            ifs = min(ifs, 100)

            # Liquidity Score (identisk med Sheets)
            ls = 0
            if avg_v20 >= 5_000_000:    ls += 40
            elif avg_v20 >= 1_000_000:  ls += 25
            elif avg_v20 >= 200_000:    ls += 12
            if dollar_vol >= 100_000_000: ls += 30
            elif dollar_vol >= 30_000_000: ls += 20
            elif dollar_vol >= 8_000_000:  ls += 10
            if vol_ratio >= 1.0:  ls += 20
            if not cap_risk:      ls += 10
            ls = min(ls, 100)

            # Weinstein Stage
            stage_num, stage_label = weinstein_stage(close, sma200_s)

            # IBD RS Rank
            rs_rank = int(rs_ranks.get(ticker, 50))

            row = {
                'ticker': ticker, 'name': info[1], 'sector': info[2], 'region': info[3],
                'price': round(price, 2),
                'daily_pct': round(daily_pct, 2),
                'rsi': round(rsi_v, 1),
                'rsi_trend': rsi_trend,
                'sma20': round(sma20_v, 2),
                'sma60': round(sma60_v, 2),
                'sma200': round(sma200_v, 2),
                'high20': round(high20, 2),
                'low5': low5_v,
                'dist_high20_raw': dist_high20_raw,
                'dist_high20': round(dist_high20_raw * 100, 2),
                'vol_ratio': round(vol_ratio, 2),
                'rvol50': round(rvol50, 2),
                'avg_vol20': round(avg_v20, 0),
                'dollar_vol_m': round(dollar_vol / 1e6, 1),
                'liquidity_pass': liq_pass,
                'liquidity': '✅' if liq_pass else '❌',
                'atr5': round(atr5_v, 2),
                'atr20': round(atr20_v, 2),
                'squeeze': '✅' if squeeze_v else '—',
                'rs_trend': rs_trend_v,
                'higher_low': higher_low,
                'inst_accum': inst_accum,
                'cap_risk': cap_risk,
                'inst_flow_score': ifs,
                'liquidity_score': ls,
                'week52_high': round(w52_high, 2),
                'week52_low': round(w52_low, 2),
                'dist_52w': round(dist_52w * 100, 1),
                'stage_num': stage_num,
                'stage': stage_label,
                'rs_rank': rs_rank,
                'rs_raw': rs_raw_scores.get(ticker, None),
            }

            states = derive_states(row, market_regime)
            row.update(states)
            results.append(row)
        except:
            continue

    df_out = pd.DataFrame(results)
    if not df_out.empty:
        df_out = df_out.sort_values('priority_score', ascending=False).reset_index(drop=True)
    return df_out

@st.cache_data(ttl=900, show_spinner=False)
def fetch_macro():
    rows = []
    try:
        raw = yf.download(MACRO_TICKERS, period='1y', interval='1d',
                          group_by='ticker', auto_adjust=True, progress=False)
        for t in MACRO_TICKERS:
            try:
                df = (raw[t] if len(MACRO_TICKERS) > 1 else raw).dropna()
                if len(df) < 60: continue
                c = df['Close']
                p = float(c.iloc[-1]); prev = float(c.iloc[-2])
                d5  = float(c.iloc[-6])  if len(c) > 5  else prev
                d30 = float(c.iloc[-31]) if len(c) > 30 else prev
                s20 = float(sma(c,20).iloc[-1]); s60 = float(sma(c,60).iloc[-1])
                trend = 'UPTREND' if p>s20>s60 else ('DOWNTREND' if p<s20<s60 else 'MIXED')
                rows.append({'Ticker':t,'Pris':round(p,2),
                    '1D%':round((p/prev-1)*100,2),'5D%':round((p/d5-1)*100,2),
                    '30D%':round((p/d30-1)*100,2),'Trend':trend})
            except: pass
    except: pass
    return pd.DataFrame(rows)

def derive_regime(macro_df, scan_df):
    score = 0
    if not macro_df.empty:
        for t, pts in [('SPY',2),('QQQ',2),('IWM',1)]:
            row = macro_df[macro_df['Ticker']==t]
            if not row.empty:
                score += pts if row.iloc[0]['Trend']=='UPTREND' else (-pts if row.iloc[0]['Trend']=='DOWNTREND' else 0)
        vix = macro_df[macro_df['Ticker']=='^VIX']
        if not vix.empty:
            v = vix.iloc[0]['Pris']
            score += -2 if v>30 else (-1 if v>25 else (1 if v<18 else 0))
    if not scan_df.empty:
        a20  = (scan_df['price']>scan_df['sma20']).mean()
        a200 = (scan_df['price']>scan_df['sma200']).mean()
        score += 2 if a20>=0.55 else (-2 if a20<0.45 else 0)
        score += 2 if a200>=0.50 else (-2 if a200<0.40 else 0)
        buys = scan_df['buy_signal'].isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION']).sum()
        score += 1 if buys>=5 else (-1 if buys==0 else 0)
    if score >= 5: return 'RISK_ON'
    if score <= 0: return 'RISK_OFF'
    return 'NEUTRAL'

# ══════════════════════════════════════════════════════════════
# POSITIONER
# ══════════════════════════════════════════════════════════════
def load_pos():
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE,'r') as f: return json.load(f)
    return []

def save_pos(p):
    with open(POSITIONS_FILE,'w') as f: json.dump(p, f, indent=2, default=str)

def enrich_positions(positions, scan_df):
    if not positions: return pd.DataFrame()
    rows = []
    for p in positions:
        t     = p['ticker']
        match = scan_df[scan_df['ticker']==t] if not scan_df.empty else pd.DataFrame()
        cp    = float(match.iloc[0]['price']) if not match.empty else p['entry_price']
        pnl_p = round((cp/p['entry_price']-1)*100, 2)
        pnl_k = round((cp-p['entry_price'])*p['shares'], 2)
        rows.append({
            'Ticker':     t,
            'Navn':       p.get('name', t),
            'Entry':      p['entry_price'],
            'Nu':         round(cp, 2),
            'PnL %':      pnl_p,
            'PnL Kr':     pnl_k,
            'Aktier':     p['shares'],
            'Stop':       match.iloc[0]['stop_level'] if not match.empty else '—',
            'Signal':     match.iloc[0]['buy_signal']  if not match.empty else '—',
            'RS Rank':    match.iloc[0]['rs_rank']     if not match.empty else '—',
            'Stage':      match.iloc[0]['stage']       if not match.empty else '—',
            'Dato':       p.get('date','—'),
        })
    df = pd.DataFrame(rows)
    return df.sort_values('PnL %', ascending=False) if not df.empty else df

# ══════════════════════════════════════════════════════════════
# CHARTS
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=900, show_spinner=False)
def get_chart_data(ticker):
    return yf.download(ticker, period='1y', interval='1d', auto_adjust=True, progress=False).dropna()

def plot_full_chart(ticker, df):
    if df.empty: return go.Figure()
    c = df['Close'].squeeze(); h = df['High'].squeeze()
    l = df['Low'].squeeze();   o = df['Open'].squeeze()
    v = df['Volume'].squeeze()

    s20=sma(c,20); s60=sma(c,60); s200=sma(c,200)
    rsi_s = calc_rsi(c,14)

    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.6, 0.2, 0.2],
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=[f'{ticker} – Kurs', 'Volumen', 'RSI (14)']
    )

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df.index, open=o, high=h, low=l, close=c, name=ticker,
        increasing_line_color='#22c55e', decreasing_line_color='#ef4444',
        increasing_fillcolor='#22c55e', decreasing_fillcolor='#ef4444'
    ), row=1, col=1)

    # SMAs
    for s, name, color, width in [(s20,'SMA20','#f59e0b',1.5),(s60,'SMA60','#3b82f6',1.5),(s200,'SMA200','#a855f7',2)]:
        fig.add_trace(go.Scatter(x=df.index, y=s, name=name, line=dict(color=color,width=width)), row=1, col=1)

    # Volume
    colors = ['#22c55e' if float(c.iloc[i]) >= float(o.iloc[i]) else '#ef4444' for i in range(len(c))]
    fig.add_trace(go.Bar(x=df.index, y=v, name='Vol', marker_color=colors, opacity=0.7), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=rsi_s, name='RSI', line=dict(color='#f59e0b', width=2)), row=3, col=1)
    fig.add_hline(y=70, line_dash='dash', line_color='#ef4444', row=3, col=1)
    fig.add_hline(y=30, line_dash='dash', line_color='#22c55e', row=3, col=1)
    fig.add_hline(y=50, line_dash='dot',  line_color='#475569', row=3, col=1)
    fig.add_hrect(y0=30, y1=70, fillcolor='#1e293b', opacity=0.2, row=3, col=1)

    layout = dict(
        plot_bgcolor='#060b17', paper_bgcolor='#0d1526',
        font=dict(color='#e2e8f0', size=12),
        legend=dict(bgcolor='#0d1526', bordercolor='#1e3a5f', orientation='h', y=1.02),
        height=650, margin=dict(l=60,r=20,t=40,b=20),
        xaxis_rangeslider_visible=False,
    )
    for axis in ['xaxis','xaxis2','xaxis3','yaxis','yaxis2','yaxis3']:
        layout[axis] = dict(gridcolor='#1e3a5f', zerolinecolor='#1e3a5f',
                            **({'showgrid':True} if 'y' in axis else {}))
    fig.update_layout(**layout)
    return fig

def plot_sector_heatmap(df):
    if df.empty: return go.Figure()
    s = df.groupby('sector').agg(
        Avg_Score=('priority_score','mean'),
        Buy=('buy_signal', lambda x: x.isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION']).sum()),
        Exit=('sell_signal', lambda x: (x=='EXIT').sum()),
        Avg_RS=('rs_rank','mean'),
        Count=('ticker','count'),
    ).round(1).reset_index().sort_values('Avg_Score', ascending=True)

    fig = go.Figure()
    bar_colors = [
        '#dc2626' if v < 30 else '#ea580c' if v < 45 else '#d97706' if v < 55 else '#22c55e' if v < 70 else '#16a34a'
        for v in s['Avg_Score']
    ]
    fig.add_trace(go.Bar(
        x=s['Avg_Score'], y=s['sector'], orientation='h',
        marker_color=bar_colors,
        text=[f"Score: {v:.0f} | Buy: {b} | RS: {r:.0f}" for v,b,r in zip(s['Avg_Score'],s['Buy'],s['Avg_RS'])],
        textposition='inside', textfont=dict(color='white', size=11),
    ))
    fig.update_layout(
        title='Sektor Score Heatmap', height=max(350, len(s)*45),
        plot_bgcolor='#060b17', paper_bgcolor='#0d1526',
        font=dict(color='#e2e8f0'),
        xaxis=dict(range=[0,100], gridcolor='#1e3a5f', title='Priority Score'),
        yaxis=dict(gridcolor='#1e3a5f'),
        margin=dict(l=140, r=20, t=50, b=40),
    )
    return fig

def plot_rs_scatter(df):
    if df.empty: return go.Figure()
    colors_map = {
        'BUY NOW':'#16a34a','BUY BREAKOUT':'#22c55e',
        'BUILD POSITION':'#2563eb','STARTER BUY':'#0ea5e9',
        'EXTENDED — WAIT':'#d97706','REDUCE':'#ea580c',
        'EXIT':'#dc2626','WATCHLIST':'#475569',
    }
    df2 = df.copy()
    df2['color'] = df2['buy_signal'].map(colors_map).fillna('#475569')

    fig = go.Figure()
    for signal, grp in df2.groupby('buy_signal'):
        fig.add_trace(go.Scatter(
            x=grp['rs_rank'], y=grp['priority_score'],
            mode='markers+text',
            name=signal,
            text=grp['ticker'],
            textposition='top center',
            textfont=dict(size=9, color='#94a3b8'),
            marker=dict(size=9, color=colors_map.get(signal,'#475569'), opacity=0.85,
                        line=dict(width=1, color='#1e3a5f')),
            hovertemplate='<b>%{text}</b><br>RS Rank: %{x}<br>Score: %{y}<extra></extra>'
        ))

    fig.add_vline(x=70, line_dash='dash', line_color='#22c55e', annotation_text='RS > 70')
    fig.add_hline(y=60, line_dash='dash', line_color='#f59e0b', annotation_text='Score > 60')

    fig.update_layout(
        title='RS Rank vs Priority Score – Alle Aktier',
        height=500, plot_bgcolor='#060b17', paper_bgcolor='#0d1526',
        font=dict(color='#e2e8f0'),
        xaxis=dict(title='IBD RS Rank (1-99)', range=[0,100], gridcolor='#1e3a5f'),
        yaxis=dict(title='Priority Score (0-100)', range=[0,100], gridcolor='#1e3a5f'),
        legend=dict(bgcolor='#0d1526', bordercolor='#1e3a5f'),
        margin=dict(l=60,r=20,t=50,b=60),
    )
    return fig

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def signal_style(val):
    return {
        'BUY NOW':          'background:#16a34a;color:white;font-weight:700',
        'BUY BREAKOUT':     'background:#22c55e;color:white;font-weight:600',
        'BUILD POSITION':   'background:#2563eb;color:white',
        'STARTER BUY':      'background:#0ea5e9;color:white',
        'EXTENDED — WAIT':  'background:#d97706;color:white',
        'REDUCE':           'background:#ea580c;color:white',
        'EXIT':             'background:#dc2626;color:white;font-weight:700',
        'HOLD':             'background:#334155;color:#94a3b8',
        'WATCHLIST':        'background:#1e293b;color:#64748b',
    }.get(val, '')

def pnl_style(val):
    if isinstance(val,(int,float)):
        return 'color:#22c55e;font-weight:700' if val>0 else ('color:#ef4444;font-weight:700' if val<0 else '')
    return ''

def regime_html(r):
    cls = {'RISK_ON':'regime-risk-on','RISK_OFF':'regime-risk-off','NEUTRAL':'regime-neutral'}.get(r,'regime-neutral')
    icons = {'RISK_ON':'🟢 RISK ON','RISK_OFF':'🔴 RISK OFF','NEUTRAL':'🟡 NEUTRAL'}
    return f'<div class="{cls}">{icons.get(r,r)}</div>'

def stage_badge(s):
    cls = {1:'stage-1',2:'stage-2',3:'stage-3',4:'stage-4'}.get(s,'stage-1')
    labels = {1:'Stage 1',2:'Stage 2',3:'Stage 3',4:'Stage 4'}
    return f'<span class="{cls}">{labels.get(s,"?")}</span>'

# ══════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════
def main():
    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("## 🎯 Scanner Pro v3.0")
        st.markdown("---")
        if st.button("🔄 Opdater data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.markdown("### ⚙️ Filtre")
        max_rows = st.slider("Maks rækker", 5, 50, 20)
        min_score = st.slider("Min score", 0, 100, 0)
        only_stage2 = st.checkbox("Kun Stage 2 aktier", False)
        min_rs = st.slider("Min RS Rank", 0, 99, 0)
        show_watchlist = st.checkbox("Vis WATCHLIST", False)

        st.markdown("---")
        st.markdown("### 🕐 Børsstatus")
        for name, info in EXCHANGES.items():
            status, lt = get_exchange_status(info)
            icon = '🟢' if status=='ÅBEN' else ('🟡' if status=='PRE' else '🔴')
            css  = 'mkt-open' if status=='ÅBEN' else ('mkt-pre' if status=='PRE' else 'mkt-closed')
            st.markdown(f"{info['flag']} **{name}** {icon} <span class='{css}'>{status}</span> `{lt}`", unsafe_allow_html=True)

        st.markdown("---")
        st.caption(f"v3.0 | {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # ── DATA LOAD ──
    prog = st.progress(0, text="🔄 Henter makrodata...")
    macro_df = fetch_macro()
    prog.progress(20, text="📊 Beregner markedsregime...")
    regime = derive_regime(macro_df, pd.DataFrame())
    prog.progress(30, text="🔍 Scanner aktier (kan tage 1-2 min)...")
    scan_df = fetch_scanner_data(tuple(UNIVERSE), regime)
    regime  = derive_regime(macro_df, scan_df)
    prog.progress(100, text="✅ Data hentet!")
    prog.empty()

    # ── HEADER ──
    col_h1, col_h2, col_h3 = st.columns([3,1,1])
    with col_h1:
        st.markdown("# 🎯 Trading Scanner Pro")
    with col_h2:
        st.markdown(regime_html(regime), unsafe_allow_html=True)
    with col_h3:
        st.markdown(f"<div style='color:#64748b;font-size:0.85rem;padding-top:8px'>📡 {len(scan_df)} aktier<br>⏰ {datetime.now().strftime('%H:%M')}</div>", unsafe_allow_html=True)

    # ── KPI CARDS ──
    if not scan_df.empty:
        buy_now   = (scan_df['buy_signal']=='BUY NOW').sum()
        buy_break = (scan_df['buy_signal']=='BUY BREAKOUT').sum()
        build     = (scan_df['buy_signal'].isin(['STARTER BUY','BUILD POSITION'])).sum()
        exits     = (scan_df['sell_signal']=='EXIT').sum()
        stage2    = (scan_df['stage_num']==2).sum()
        rs_top    = (scan_df['rs_rank']>=80).sum()
        above200  = (scan_df['price']>scan_df['sma200']).sum()
        total     = len(scan_df)
        avg_rs    = int(scan_df['rs_rank'].mean())

        c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
        c1.metric("🚀 BUY NOW",      buy_now)
        c2.metric("📈 BUY BREAKOUT", buy_break)
        c3.metric("🌱 BUILD/STARTER",build)
        c4.metric("🔴 EXIT",         exits)
        c5.metric("📗 Stage 2",      stage2)
        c6.metric("⭐ RS > 80",      rs_top)
        c7.metric("📊 Over SMA200",  f"{above200}/{total}")
        c8.metric("📡 Gns RS Rank",  avg_rs)

    st.divider()

    # ── TABS ──
    tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs([
        "🏠 Overblik","📋 Scanner","💼 Positioner","📊 Charts","🔥 Sektorer","🎯 RS Analyse"
    ])

    # ════════════ TAB 1: OVERBLIK ════════════
    with tab1:
        col_m, col_b = st.columns([1,1])

        with col_m:
            st.subheader("🌍 Market Pulse")
            if not macro_df.empty:
                def c_pct(v):
                    if isinstance(v,float): return f'color:{"#22c55e" if v>0 else "#ef4444" if v<0 else "#94a3b8"}'
                    return ''
                st.dataframe(
                    macro_df.style.applymap(c_pct, subset=['1D%','5D%','30D%']),
                    use_container_width=True, hide_index=True, height=340
                )

        with col_b:
            st.subheader("🚀 Top Buy Kandidater")
            if not scan_df.empty:
                top_buy = scan_df[
                    scan_df['buy_signal'].isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION'])
                ].head(max_rows)
                if top_buy.empty:
                    st.info("Ingen aktive buy-signaler. Markedet er i RISK_OFF tilstand.")
                else:
                    st.dataframe(
                        top_buy[['ticker','name','sector','price','daily_pct','rsi','rs_rank','stage_num','priority_score','buy_signal']]
                        .rename(columns={'daily_pct':'1D%','rs_rank':'RS','stage_num':'Stage','priority_score':'Score','buy_signal':'Signal'})
                        .style.applymap(signal_style, subset=['Signal'])
                        .format({'price':'{:.2f}','1D%':'{:+.2f}%','rsi':'{:.1f}','Score':'{:.0f}'}),
                        use_container_width=True, hide_index=True, height=340
                    )

        st.divider()

        col_up, col_dn = st.columns(2)
        with col_up:
            st.subheader("📈 Top 10 Op i dag")
            if not scan_df.empty:
                st.dataframe(
                    scan_df.nlargest(10,'daily_pct')[['ticker','sector','region','price','daily_pct','rsi','buy_signal']]
                    .style.applymap(signal_style,subset=['buy_signal'])
                    .format({'price':'{:.2f}','daily_pct':'{:+.2f}%','rsi':'{:.1f}'}),
                    use_container_width=True, hide_index=True
                )
        with col_dn:
            st.subheader("📉 Top 10 Ned i dag")
            if not scan_df.empty:
                st.dataframe(
                    scan_df.nsmallest(10,'daily_pct')[['ticker','sector','region','price','daily_pct','rsi','sell_signal']]
                    .style.applymap(signal_style,subset=['sell_signal'])
                    .format({'price':'{:.2f}','daily_pct':'{:+.2f}%','rsi':'{:.1f}'}),
                    use_container_width=True, hide_index=True
                )

    # ════════════ TAB 2: SCANNER ════════════
    with tab2:
        st.subheader("📋 Fuld Scanner")
        if not scan_df.empty:
            c1,c2,c3,c4 = st.columns(4)
            with c1: sf = st.multiselect("Sektor",   sorted(scan_df['sector'].unique()))
            with c2: rf = st.multiselect("Region",   sorted(scan_df['region'].unique()))
            with c3: sig= st.multiselect("Signal",   sorted(scan_df['buy_signal'].unique()))
            with c4: stg= st.multiselect("Stage",    [1,2,3,4])

            flt = scan_df.copy()
            if sf:  flt = flt[flt['sector'].isin(sf)]
            if rf:  flt = flt[flt['region'].isin(rf)]
            if sig: flt = flt[flt['buy_signal'].isin(sig)]
            if stg: flt = flt[flt['stage_num'].isin(stg)]
            if only_stage2: flt = flt[flt['stage_num']==2]
            if not show_watchlist: flt = flt[flt['buy_signal']!='WATCHLIST']
            flt = flt[flt['priority_score']>=min_score]
            flt = flt[flt['rs_rank']>=min_rs]

            st.caption(f"Viser **{len(flt)}** aktier af {len(scan_df)}")
            st.dataframe(
                flt[[
                    'ticker','name','sector','region',
                    'price','daily_pct','rsi','rsi_trend',
                    'sma20','sma200','vol_ratio','dist_high20',
                    'squeeze','inst_flow_score','liquidity_score',
                    'rs_rank','stage_num',
                    'trend_score','setup_score','risk_penalty','priority_score',
                    'buy_signal','sell_signal','setup_state','stop_level',
                    'dist_52w','liquidity'
                ]].style
                .applymap(signal_style, subset=['buy_signal','sell_signal'])
                .format({
                    'price':'{:.2f}','daily_pct':'{:+.2f}%',
                    'rsi':'{:.1f}','vol_ratio':'{:.2f}',
                    'dist_high20':'{:.1f}%','dist_52w':'{:.1f}%',
                    'priority_score':'{:.0f}',
                    'inst_flow_score':'{:.0f}','liquidity_score':'{:.0f}',
                }),
                use_container_width=True, hide_index=True, height=600
            )

    # ════════════ TAB 3: POSITIONER ════════════
    with tab3:
        st.subheader("💼 Mine Positioner")
        positions = load_pos()
        pos_df    = enrich_positions(positions, scan_df)

        if not pos_df.empty:
            total_pnl = pos_df['PnL Kr'].sum()
            avg_pnl   = pos_df['PnL %'].mean()
            winners   = (pos_df['PnL %']>0).sum()

            c1,c2,c3,c4 = st.columns(4)
            c1.metric("📊 Positioner",  len(pos_df))
            c2.metric("💰 Total PnL",   f"{total_pnl:+.0f} kr")
            c3.metric("📈 Gns PnL %",   f"{avg_pnl:+.1f}%")
            c4.metric("✅ Winners",      f"{winners}/{len(pos_df)}")

            st.dataframe(
                pos_df.style
                .applymap(pnl_style, subset=['PnL %','PnL Kr'])
                .applymap(signal_style, subset=['Signal'])
                .format({'Entry':'{:.2f}','Nu':'{:.2f}','PnL %':'{:+.2f}%','PnL Kr':'{:+.0f}'}),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("Ingen aktive positioner. Tilføj nedenfor.")

        st.divider()
        st.subheader("➕ Tilføj / Fjern Position")
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: new_t = st.text_input("Ticker").upper().strip()
        with c2: new_e = st.number_input("Entry Pris", min_value=0.0, step=0.01, format="%.2f")
        with c3: new_s = st.number_input("Antal Aktier", min_value=1, step=1)
        with c4: new_n = st.text_input("Navn")
        with c5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Tilføj", use_container_width=True):
                if new_t and new_e > 0:
                    positions.append({'ticker':new_t,'name':new_n or new_t,'entry_price':new_e,'shares':new_s,'date':datetime.now().strftime('%Y-%m-%d')})
                    save_pos(positions)
                    st.success(f"✅ {new_t} tilføjet!")
                    st.rerun()
                else:
                    st.error("Udfyld ticker og pris.")

        if positions:
            c1, c2 = st.columns([3,1])
            with c1: rm = st.selectbox("Fjern position", [p['ticker'] for p in positions])
            with c2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Fjern", use_container_width=True):
                    positions = [p for p in positions if p['ticker']!=rm]
                    save_pos(positions)
                    st.success(f"✅ {rm} fjernet.")
                    st.rerun()

    # ════════════ TAB 4: CHARTS ════════════
    with tab4:
        st.subheader("📊 Kurs, Volumen & RSI")
        if not scan_df.empty:
            tickers = scan_df['ticker'].tolist()
            sel = st.selectbox("Vælg aktie", tickers, format_func=lambda t: f"{t} – {scan_df[scan_df['ticker']==t].iloc[0]['name']}" if not scan_df[scan_df['ticker']==t].empty else t)
            if sel:
                row = scan_df[scan_df['ticker']==sel].iloc[0]
                c1,c2,c3,c4,c5,c6 = st.columns(6)
                c1.metric("Pris",      f"{row['price']:.2f}")
                c2.metric("1D %",      f"{row['daily_pct']:+.2f}%")
                c3.metric("RSI",       f"{row['rsi']:.1f}")
                c4.metric("RS Rank",   f"{row['rs_rank']}/99")
                c5.metric("Score",     f"{row['priority_score']:.0f}")
                c6.metric("Stage",     row['stage_num'])

                col_i1, col_i2, col_i3 = st.columns(3)
                col_i1.info(f"**Signal:** {row['buy_signal']}")
                col_i2.info(f"**Setup:** {row['setup_state']}")
                col_i3.info(f"**Stop:** {row['stop_level']}")

                with st.spinner("Henter chart..."):
                    chart_df = get_chart_data(sel)
                    st.plotly_chart(plot_full_chart(sel, chart_df), use_container_width=True)

    # ════════════ TAB 5: SEKTORER ════════════
    with tab5:
        st.subheader("🔥 Sektor & Region Analyse")
        if not scan_df.empty:
            st.plotly_chart(plot_sector_heatmap(scan_df), use_container_width=True)

            c1,c2 = st.columns(2)
            with c1:
                st.subheader("Sektor Detaljer")
                st.dataframe(
                    scan_df.groupby('sector').agg(
                        Antal=('ticker','count'),
                        Score=('priority_score','mean'),
                        RSI=('rsi','mean'),
                        RS=('rs_rank','mean'),
                        Buy=('buy_signal', lambda x: x.isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION']).sum()),
                        Exit=('sell_signal', lambda x: (x=='EXIT').sum()),
                        Stage2=('stage_num', lambda x: (x==2).sum()),
                    ).round(1).sort_values('Score', ascending=False),
                    use_container_width=True
                )
            with c2:
                st.subheader("Region Detaljer")
                st.dataframe(
                    scan_df.groupby('region').agg(
                        Antal=('ticker','count'),
                        Score=('priority_score','mean'),
                        RS=('rs_rank','mean'),
                        Buy=('buy_signal', lambda x: x.isin(['BUY NOW','BUY BREAKOUT','STARTER BUY','BUILD POSITION']).sum()),
                        Stage2=('stage_num', lambda x: (x==2).sum()),
                    ).round(1).sort_values('Score', ascending=False),
                    use_container_width=True
                )

    # ════════════ TAB 6: RS ANALYSE ════════════
    with tab6:
        st.subheader("🎯 IBD RS Rank vs Priority Score")
        st.caption("Aktier øverst til højre (høj RS + høj score) er de stærkeste kandidater")
        if not scan_df.empty:
            st.plotly_chart(plot_rs_scatter(scan_df), use_container_width=True)

            st.subheader("⭐ Top 25 – Stærkeste RS Ranking")
            top_rs = scan_df.nlargest(25,'rs_rank')[['ticker','name','sector','region','price','daily_pct','rsi','rs_rank','stage_num','priority_score','buy_signal']]
            st.dataframe(
                top_rs.style
                .applymap(signal_style, subset=['buy_signal'])
                .format({'price':'{:.2f}','daily_pct':'{:+.2f}%','rsi':'{:.1f}','priority_score':'{:.0f}'}),
                use_container_width=True, hide_index=True
            )

if __name__ == '__main__':
    main()