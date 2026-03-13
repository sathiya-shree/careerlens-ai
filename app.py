"""
CareerLens AI — Professional Resume Intelligence Platform
Stack : Streamlit · spaCy · pdfplumber · Gemini 1.5 Flash
Author: Sathiya Shree S
"""

import streamlit as st
import os, re, json, tempfile, math
import pdfplumber, docx2txt, pytesseract, spacy
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import requests

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerLens AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "page": "Overview", "resume_text": "", "resume_name": "", "parsed": {},
    "ats": 0, "ats_reasons": [], "match": 0, "matched": [], "missing": [],
    "jd_text": "", "job_role": "", "tone": {},
    "analysis_done": False,
    "iq": [], "ifb": {}, "api_key": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────────────────
#  DESIGN SYSTEM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

/* ── Tokens ── */
:root {
  --bg       : #fafaf9;
  --surface  : #ffffff;
  --border   : #e7e5e0;
  --border-md: #d4d1cb;
  --text-1   : #1c1c1e;
  --text-2   : #4a4a52;
  --text-3   : #8e8e9a;
  --text-4   : #b8b8c2;

  --teal     : #0ea5a0;
  --teal-d   : #0c8c88;
  --teal-dk  : #0a6b68;
  --teal-bg  : #f0fffe;
  --teal-bd  : #a3e8e6;

  --green    : #16a34a;
  --green-bg : #f0fdf4;
  --green-bd : #86efac;

  --amber    : #c97b10;
  --amber-bg : #fffbeb;
  --amber-bd : #fcd34d;

  --red      : #dc2626;
  --red-bg   : #fef2f2;
  --red-bd   : #fca5a5;

  --purple   : #7c3aed;
  --purple-bg: #f5f3ff;
  --purple-bd: #c4b5fd;

  --pink     : #be185d;
  --blue     : #0369a1;

  --r        : 10px;
  --r-lg     : 14px;
  --r-xl     : 18px;
  --sh       : 0 1px 2px rgba(0,0,0,.04),0 3px 10px rgba(0,0,0,.06);
  --sh-md    : 0 4px 8px rgba(0,0,0,.06),0 12px 28px rgba(0,0,0,.09);
  --sh-teal  : 0 4px 16px rgba(14,165,160,.28);
}

/* ── Base ── */
*,*::before,*::after{box-sizing:border-box;}
html,body,.stApp{background:var(--bg)!important;font-family:'Inter',sans-serif!important;color:var(--text-1)!important;}
.block-container{padding:0!important;max-width:100%!important;}
.stApp>div{background:var(--bg)!important;}

/* ── Sidebar shell ── */
section[data-testid="stSidebar"]{
  background:#111827!important;
  border-right:none!important;
  min-width:220px!important;
  max-width:220px!important;
}
section[data-testid="stSidebar"]>div:first-child{
  background:#111827!important;
  padding:0!important;
}

/* Sidebar nav buttons — must be scoped BEFORE global .stButton */
section[data-testid="stSidebar"] .stButton>button{
  background:transparent!important;
  color:rgba(255,255,255,.52)!important;
  border:none!important;
  border-radius:8px!important;
  font-size:.84rem!important;
  font-weight:500!important;
  text-align:left!important;
  padding:9px 12px!important;
  width:100%!important;
  box-shadow:none!important;
  transform:none!important;
  letter-spacing:0!important;
  transition:background .14s,color .14s!important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(255,255,255,.08)!important;
  color:#fff!important;
  box-shadow:none!important;
  transform:none!important;
}
section[data-testid="stSidebar"] .stButton>button:focus{outline:none!important;box-shadow:none!important;}

/* Sidebar text input */
section[data-testid="stSidebar"] .stTextInput input{
  background:rgba(255,255,255,.07)!important;
  border:1px solid rgba(255,255,255,.15)!important;
  border-radius:8px!important;
  color:#fff!important;
  font-size:.82rem!important;
}
section[data-testid="stSidebar"] .stTextInput input::placeholder{color:rgba(255,255,255,.3)!important;}
section[data-testid="stSidebar"] label{color:rgba(255,255,255,.35)!important;font-size:.7rem!important;}

/* ── Global buttons ── */
.stButton>button{
  background:var(--teal)!important;
  color:#fff!important;
  border:none!important;
  border-radius:var(--r)!important;
  font-family:'Inter',sans-serif!important;
  font-size:.84rem!important;
  font-weight:600!important;
  padding:10px 20px!important;
  letter-spacing:.01em!important;
  box-shadow:none!important;
  transition:background .16s,box-shadow .16s,transform .14s!important;
}
.stButton>button:hover{
  background:var(--teal-d)!important;
  box-shadow:var(--sh-teal)!important;
  transform:translateY(-1px)!important;
}
.stButton>button:focus{outline:none!important;box-shadow:var(--sh-teal)!important;}

/* ── Inputs ── */
.stTextArea textarea,.stTextInput input{
  background:var(--surface)!important;
  border:1.5px solid var(--border)!important;
  border-radius:var(--r)!important;
  color:var(--text-1)!important;
  font-family:'Inter',sans-serif!important;
  font-size:.86rem!important;
  line-height:1.6!important;
  transition:border-color .16s,box-shadow .16s!important;
}
.stTextArea textarea:focus,.stTextInput input:focus{
  border-color:var(--teal)!important;
  box-shadow:0 0 0 3px rgba(14,165,160,.14)!important;
}
label{color:var(--text-2)!important;font-size:.82rem!important;font-weight:500!important;}
.stFileUploader,.stFileUploader section{background:transparent!important;border:none!important;}
div[data-testid="stFileUploader"]{background:transparent!important;}
div[data-testid="stFileUploader"] section{background:transparent!important;border:none!important;}

/* ── Alerts ── */
.stSuccess,.stWarning,.stError,.stInfo{border-radius:var(--r)!important;font-size:.83rem!important;}
.stSuccess{background:var(--green-bg)!important;border-color:var(--green-bd)!important;color:var(--green)!important;}
.stWarning{background:var(--amber-bg)!important;border-color:var(--amber-bd)!important;color:var(--amber)!important;}
.stError  {background:var(--red-bg)!important;border-color:var(--red-bd)!important;color:var(--red)!important;}
.stInfo   {background:var(--teal-bg)!important;border-color:var(--teal-bd)!important;color:var(--teal-d)!important;}
.stSpinner>div{border-top-color:var(--teal)!important;}

/* ══════════════════════════════════
   Sidebar custom HTML
══════════════════════════════════ */
.sb-brand{
  padding:22px 18px 16px;
  border-bottom:1px solid rgba(255,255,255,.08);
  margin-bottom:8px;
}
.sb-brand-name{
  font-family:'Instrument Serif',serif;
  font-size:1.2rem;color:#fff;font-weight:400;letter-spacing:.3px;
}
.sb-brand-name em{color:#2dd4bf;font-style:normal;}
.sb-brand-sub{font-size:.68rem;color:rgba(255,255,255,.35);margin-top:3px;letter-spacing:.3px;}

.sb-group{
  font-size:.6rem;font-weight:600;letter-spacing:2.5px;
  text-transform:uppercase;color:rgba(255,255,255,.28);
  padding:12px 18px 5px;
}
.sb-active-nav button{
  background:rgba(255,255,255,.1)!important;
  color:#ffffff!important;
  font-weight:600!important;
}
.sb-divider{height:1px;background:rgba(255,255,255,.08);margin:10px 14px;}

.sb-card{
  margin:10px 12px 0;
  padding:12px 13px;
  background:rgba(255,255,255,.05);
  border:1px solid rgba(255,255,255,.1);
  border-radius:10px;
}
.sb-card-title{font-size:.72rem;font-weight:600;color:#fff;margin-bottom:3px;}
.sb-card-body{font-size:.71rem;color:rgba(255,255,255,.5);line-height:1.6;}
.sb-card-stat{
  display:flex;gap:0;margin-top:10px;
  border-top:1px solid rgba(255,255,255,.08);padding-top:10px;
}
.sb-stat{flex:1;text-align:center;}
.sb-stat-val{font-family:'Instrument Serif',serif;font-size:1.3rem;color:#fff;line-height:1;}
.sb-stat-lbl{font-size:.58rem;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.35);margin-top:2px;}

/* ══════════════════════════════════
   Topbar
══════════════════════════════════ */
.topbar{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:0 28px;height:54px;
  display:flex;align-items:center;justify-content:space-between;
  position:sticky;top:0;z-index:300;
}
.tb-title{font-family:'Instrument Serif',serif;font-size:1.05rem;color:var(--text-1);}
.tb-sub{font-size:.71rem;color:var(--text-3);margin-top:1px;}
.tb-right{display:flex;align-items:center;gap:8px;}
.badge{
  display:inline-flex;align-items:center;gap:5px;
  padding:4px 10px;border-radius:20px;
  font-size:.7rem;font-weight:600;border:1px solid;white-space:nowrap;
}
.badge-green {background:var(--green-bg);color:var(--green);border-color:var(--green-bd);}
.badge-amber {background:var(--amber-bg);color:var(--amber);border-color:var(--amber-bd);}
.badge-teal  {background:var(--teal-bg);color:var(--teal-dk);border-color:var(--teal-bd);}

/* ══════════════════════════════════
   Page layout
══════════════════════════════════ */
.page{padding:26px 28px 80px;animation:rise .32s ease both;}
@keyframes rise{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:translateY(0);}}

.page-header{margin-bottom:22px;}
.page-title{font-family:'Instrument Serif',serif;font-size:1.55rem;color:var(--text-1);margin-bottom:3px;}
.page-sub  {font-size:.83rem;color:var(--text-3);line-height:1.5;}

/* ══════════════════════════════════
   Hero
══════════════════════════════════ */
.hero{
  background:linear-gradient(118deg,#0a3d3b 0%,#0a6b68 50%,var(--teal) 100%);
  border-radius:var(--r-xl);padding:36px 40px;margin-bottom:22px;
  position:relative;overflow:hidden;
}
.hero::before{
  content:'';position:absolute;right:-30px;top:-30px;
  width:200px;height:200px;border-radius:50%;
  background:rgba(255,255,255,.05);
}
.hero::after{
  content:'';position:absolute;right:80px;bottom:-60px;
  width:150px;height:150px;border-radius:50%;
  background:rgba(255,255,255,.04);
}
.hero-eyebrow{
  font-size:.6rem;font-weight:700;letter-spacing:3px;
  text-transform:uppercase;color:#5eead4;margin-bottom:10px;
}
.hero-heading{
  font-family:'Instrument Serif',serif;
  font-size:2.1rem;color:#fff;line-height:1.18;margin-bottom:9px;
}
.hero-heading i{color:#a7f3d0;font-style:normal;}
.hero-body{
  font-size:.85rem;color:rgba(255,255,255,.65);
  max-width:400px;line-height:1.75;margin-bottom:24px;
}
.hero-kpis{display:flex;gap:28px;}
.kpi-val{font-family:'Instrument Serif',serif;font-size:1.75rem;color:#fff;line-height:1;}
.kpi-lbl{font-size:.59rem;text-transform:uppercase;letter-spacing:1.5px;color:#5eead4;margin-top:2px;}

/* ══════════════════════════════════
   KPI tiles
══════════════════════════════════ */
.kpi-row{display:grid;grid-template-columns:repeat(4,1fr);gap:13px;margin-bottom:22px;}
.kpi-tile{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:17px 16px;
  box-shadow:var(--sh);transition:all .2s;position:relative;overflow:hidden;
}
.kpi-tile:hover{transform:translateY(-2px);box-shadow:var(--sh-md);}
.kpi-tile-bar{position:absolute;top:0;left:0;right:0;height:3px;border-radius:var(--r-lg) var(--r-lg) 0 0;}
.kpi-tile-val{font-family:'Instrument Serif',serif;font-size:2rem;font-weight:400;line-height:1;margin-bottom:4px;}
.kpi-tile-lbl{font-size:.61rem;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;color:var(--text-3);}

/* ══════════════════════════════════
   Cards
══════════════════════════════════ */
.card{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:20px 22px;
  margin-bottom:14px;box-shadow:var(--sh);
  transition:box-shadow .2s;
}
.card:hover{box-shadow:var(--sh-md);}

.card-head{
  font-size:.8rem;font-weight:700;color:var(--text-1);
  margin-bottom:13px;padding-bottom:10px;
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.card-head-tag{
  font-size:.64rem;font-weight:600;padding:2px 8px;
  border-radius:20px;background:var(--teal-bg);
  color:var(--teal-dk);border:1px solid var(--teal-bd);
}

/* ══════════════════════════════════
   Score ring
══════════════════════════════════ */
.score-ring{text-align:center;padding:18px 10px;}
.score-num{font-family:'Instrument Serif',serif;font-size:4rem;line-height:1;}
.score-den{font-size:.75rem;color:var(--text-3);margin-top:2px;}
.score-tag{
  display:inline-block;margin-top:10px;
  padding:4px 14px;border-radius:20px;
  font-size:.72rem;font-weight:600;border:1px solid;
}

/* ══════════════════════════════════
   Progress bars
══════════════════════════════════ */
.pb{margin:7px 0;}
.pb-row{
  display:flex;justify-content:space-between;
  font-size:.78rem;color:var(--text-2);margin-bottom:4px;font-weight:500;
}
.pb-val{font-weight:600;}
.pb-track{background:var(--border);border-radius:999px;height:5px;overflow:hidden;}
.pb-fill{height:5px;border-radius:999px;animation:grow 1.1s cubic-bezier(.22,1,.36,1) forwards;}
@keyframes grow{from{width:0!important;}}

/* ══════════════════════════════════
   Tags
══════════════════════════════════ */
.taglist{display:flex;flex-wrap:wrap;gap:5px;margin-top:7px;}
.tag{
  padding:3px 10px;border-radius:20px;
  font-size:.72rem;font-weight:500;border:1px solid;
  cursor:default;transition:transform .12s;
}
.tag:hover{transform:translateY(-1px);}
.t-teal  {background:var(--teal-bg);border-color:var(--teal-bd);color:var(--teal-dk);}
.t-green {background:var(--green-bg);border-color:var(--green-bd);color:var(--green);}
.t-red   {background:var(--red-bg);border-color:var(--red-bd);color:var(--red);}
.t-amber {background:var(--amber-bg);border-color:var(--amber-bd);color:var(--amber);}
.t-purple{background:var(--purple-bg);border-color:var(--purple-bd);color:var(--purple);}
.t-gray  {background:#f4f4f5;border-color:#e4e4e7;color:var(--text-2);}

/* ══════════════════════════════════
   Divider label
══════════════════════════════════ */
.div-lbl{
  font-size:.6rem;font-weight:700;text-transform:uppercase;
  letter-spacing:2px;color:var(--text-3);
  margin:14px 0 8px;display:flex;align-items:center;gap:9px;
}
.div-lbl::after{content:'';flex:1;height:1px;background:var(--border);}

/* ══════════════════════════════════
   Breakdown row
══════════════════════════════════ */
.brow{
  display:flex;align-items:center;gap:8px;
  padding:7px 0;font-size:.8rem;color:var(--text-2);
  border-bottom:1px solid var(--border);
}
.brow:last-child{border:none;}
.brow-icon{font-size:.85rem;min-width:18px;}
.brow-pts{font-weight:700;min-width:46px;font-size:.8rem;}

/* ══════════════════════════════════
   Insight callout
══════════════════════════════════ */
.callout{
  background:var(--teal-bg);border-left:3px solid var(--teal);
  border-radius:0 8px 8px 0;padding:10px 13px;
  margin:9px 0;font-size:.8rem;color:var(--text-2);line-height:1.65;
}
.callout b{color:var(--teal-dk);}

/* ══════════════════════════════════
   Upload zone
══════════════════════════════════ */
.upload-zone{
  background:linear-gradient(135deg,var(--teal-bg),#f7ffff);
  border:1.5px dashed var(--teal-bd);
  border-radius:var(--r-lg);
  padding:40px 24px;text-align:center;transition:all .2s;
}
.upload-zone:hover{border-color:var(--teal);}
.uz-ico{font-size:2.2rem;margin-bottom:8px;display:block;}
.uz-h  {font-family:'Instrument Serif',serif;font-size:.98rem;color:var(--teal-dk);margin-bottom:4px;}
.uz-s  {font-size:.76rem;color:var(--text-3);}

/* ══════════════════════════════════
   Profile block
══════════════════════════════════ */
.profile{
  background:linear-gradient(128deg,#0a3d3b,var(--teal-dk));
  border-radius:var(--r-lg);padding:20px 22px;
  margin-bottom:14px;
}
.profile-name{font-family:'Instrument Serif',serif;font-size:1.15rem;color:#fff;margin-bottom:3px;}
.profile-sub{font-size:.76rem;color:rgba(255,255,255,.55);}
.profile-grid{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:0;margin-top:14px;
  border-top:1px solid rgba(255,255,255,.1);padding-top:14px;
}
.profile-stat-v{font-family:'Instrument Serif',serif;font-size:1.55rem;color:#fff;line-height:1;}
.profile-stat-l{font-size:.57rem;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.45);margin-top:2px;}

/* ══════════════════════════════════
   Quick action grid
══════════════════════════════════ */
.qa-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:6px;}
.qa-tile{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:16px 15px;
  box-shadow:var(--sh);transition:all .2s;
}
.qa-tile:hover{transform:translateY(-2px);box-shadow:var(--sh-md);border-color:var(--teal-bd);}
.qa-ico{font-size:1.4rem;margin-bottom:7px;}
.qa-h  {font-size:.84rem;font-weight:600;color:var(--text-1);margin-bottom:3px;}
.qa-s  {font-size:.73rem;color:var(--text-3);line-height:1.5;}

/* ══════════════════════════════════
   Interview
══════════════════════════════════ */
.qcard{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r);padding:15px 18px;
  margin-bottom:9px;transition:box-shadow .18s;
}
.qcard:hover{box-shadow:var(--sh);}
.qcard-type{font-size:.61rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:5px;}
.qcard-text{font-size:.87rem;font-weight:500;color:var(--text-1);line-height:1.6;}
.fb-box{
  background:var(--bg);border:1px solid var(--border);
  border-radius:var(--r);padding:14px 16px;margin-top:8px;
  animation:rise .28s ease;
}
.fb-num{font-family:'Instrument Serif',serif;font-size:2.3rem;line-height:1;}
.fb-row{font-size:.79rem;color:var(--text-2);margin:6px 0;line-height:1.6;}

/* ══════════════════════════════════
   Tone
══════════════════════════════════ */
.tone-row{display:flex;align-items:center;gap:10px;margin:7px 0;}
.tone-n{width:96px;font-size:.78rem;color:var(--text-2);font-weight:500;flex-shrink:0;}
.tone-track{flex:1;background:var(--border);border-radius:999px;height:6px;overflow:hidden;}
.tone-fill{height:6px;border-radius:999px;animation:grow 1.1s cubic-bezier(.22,1,.36,1) forwards;}
.tone-pct{width:30px;text-align:right;font-size:.78rem;font-weight:700;}

/* ══════════════════════════════════
   Empty state
══════════════════════════════════ */
.empty{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--r-lg);padding:56px 28px;
  text-align:center;box-shadow:var(--sh);
}
.empty-ico{font-size:2.2rem;margin-bottom:11px;}
.empty-h  {font-family:'Instrument Serif',serif;font-size:.95rem;color:var(--text-1);margin-bottom:5px;}
.empty-s  {font-size:.77rem;color:var(--text-3);line-height:1.5;}

/* ══════════════════════════════════
   Footer
══════════════════════════════════ */
.footer{
  background:#111827;
  padding:15px 28px;
  display:flex;align-items:center;justify-content:space-between;
  margin-top:40px;
}
.footer-brand{font-family:'Instrument Serif',serif;font-size:.9rem;color:#fff;}
.footer-brand em{color:#2dd4bf;font-style:normal;}
.footer-meta{font-size:.7rem;color:rgba(255,255,255,.4);}
.footer-meta b{color:rgba(255,255,255,.7);}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  BACKEND — NLP + SCORING
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def load_nlp():
    try:    return spacy.load("en_core_web_sm")
    except: st.error("Run: python -m spacy download en_core_web_sm"); st.stop()
nlp = load_nlp()

SKILLS_DB = [
    "python","java","javascript","typescript","c++","c#","go","rust","kotlin","swift",
    "r","scala","php","ruby","html","css","react","vue","angular","node.js","express",
    "django","flask","fastapi","next.js","tailwind","machine learning","deep learning",
    "nlp","computer vision","pytorch","tensorflow","scikit-learn","keras","pandas",
    "numpy","matplotlib","seaborn","plotly","tableau","power bi","data analysis",
    "data mining","xai","explainable ai","shap","lime","sql","mysql","postgresql",
    "mongodb","redis","elasticsearch","aws","azure","gcp","docker","kubernetes",
    "ci/cd","git","github","linux","bash","rest api","graphql","microservices",
    "spark","hadoop","opencv","mediapipe","spacy","nltk","huggingface",
    "communication","leadership","teamwork","problem solving","time management",
    "critical thinking","project management","agile","scrum","research","presentation",
]
SOFT = {"communication","leadership","teamwork","problem solving","time management",
        "critical thinking","project management","agile","scrum","research","presentation"}

TONE_PAT = {
    "Technical":      r'\b(developed|implemented|built|deployed|engineered|algorithm|system|api|model)\b',
    "Leadership":     r'\b(led|managed|coordinated|supervised|spearheaded|mentored|oversaw)\b',
    "Analytical":     r'\b(analyzed|evaluated|optimized|improved|measured|assessed|researched|solved)\b',
    "Creative":       r'\b(designed|created|innovated|crafted|conceptualized|visualized|produced)\b',
    "Collaborative":  r'\b(collaborated|partnered|team|together|contributed|supported)\b',
    "Results-Driven": r'\b(\d+\s*%|increased|decreased|grew|achieved|delivered|exceeded|boosted)\b',
}
TONE_CLR = {
    "Technical":"#0ea5a0","Leadership":"#7c3aed","Analytical":"#16a34a",
    "Creative":"#c97b10","Collaborative":"#be185d","Results-Driven":"#0369a1",
}

def score_color(v):  return "#16a34a" if v>=75 else "#c97b10" if v>=50 else "#dc2626"
def score_label(v):  return ("Excellent","#f0fdf4","#86efac") if v>=80 else \
                            ("Good",     "#fffbeb","#fcd34d") if v>=60 else \
                            ("Fair",     "#fff7ed","#fdba74") if v>=40 else \
                            ("Weak",     "#fef2f2","#fca5a5")

def get_api_key():
    try:
        k = st.secrets["GEMINI_API_KEY"]
        if k: return k
    except: pass
    return st.session_state.get("api_key", "")

def call_gemini(prompt, max_tokens=900):
    k = get_api_key()
    if not k: return None, "No API key."
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={k}",
            headers={"Content-Type":"application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}],
                  "generationConfig":{"maxOutputTokens":max_tokens,"temperature":0.7}},
            timeout=30)
        d = r.json()
        if "error" in d: return None, d["error"]["message"]
        return d["candidates"][0]["content"]["parts"][0]["text"].strip(), None
    except Exception as e: return None, str(e)

def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == ".pdf":
            t = ""
            with pdfplumber.open(path) as pdf:
                for pg in pdf.pages:
                    x = pg.extract_text()
                    if x: t += x + "\n"
            return t
        if ext == ".docx":   return docx2txt.process(path) or ""
        if ext in (".png",".jpg",".jpeg"):
            return pytesseract.image_to_string(Image.open(path))
    except Exception as e:
        st.error(f"Extraction error: {e}")
    return ""

def parse_resume(text):
    doc  = nlp(text[:2000])
    stop = {"phone","email","contact","mobile","address"}
    name = next(
        (" ".join([w for w in e.text.split() if w.lower() not in stop][:3])
         for e in doc.ents if e.label_ == "PERSON"), "Candidate")
    emails = list(set(re.findall(r"\b[\w.\-]+@[\w.\-]+\.\w{2,}\b", text)))
    phones = list({m[0]+m[1] for m in re.findall(
        r"(\+?\d{1,3}[\s\-.]?)?(\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4})",
        text.replace("\n"," ")) if any(m)})
    tl  = text.lower()
    skills = sorted([s for s in SKILLS_DB if re.search(r'\b'+re.escape(s)+r'\b', tl)])
    edu_re = [r'\b(b\.?sc|b\.?tech|m\.?sc|m\.?tech|mba|phd|bachelor|master)\b',
              r'\b(university|college|institute)\b']
    edu = list(dict.fromkeys([l.strip() for l in text.splitlines()
               if l.strip() and any(re.search(p, l, re.I) for p in edu_re)]))[:5]
    return {"name":name,"emails":emails,"phones":phones,"skills":skills,"education":edu}

def calc_ats(text, skills):
    checks = [
        (bool(re.search(r'\b[\w.\-]+@[\w.\-]+\.\w{2,}\b', text)),
         "Email address found", "No email address", 10),
        (bool(re.search(r'\+?\d[\d\s\-]{7,}', text)),
         "Phone number found", "No phone number", 5),
        (bool(re.search(r'\b(university|college|bachelor|master|b\.sc|m\.sc)\b', text, re.I)),
         "Education section present", "Missing education section", 10),
        (bool(re.search(r'\b(experience|intern|project|work)\b', text, re.I)),
         "Experience / Projects present", "No experience or projects", 10),
    ]
    s, rows = 0, []
    for ok, yes, no, pts in checks:
        if ok: s+=pts; rows.append(("✓", yes, pts, "#16a34a"))
        else:          rows.append(("✗", no,  0,  "#dc2626"))
    sk = min(25, len(skills)*2); s += sk
    rows.append(("◆", f"{len(skills)} skills detected", sk, "#0ea5a0"))
    w = len(text.split())
    if 300<=w<=1200: s+=10; rows.append(("✓",f"Ideal length — {w} words", 10,"#16a34a"))
    elif w<300:             rows.append(("✗",f"Too short — {w} words",     0, "#dc2626"))
    else:            s+=5;  rows.append(("○",f"Slightly long — {w} words", 5, "#c97b10"))
    nums = re.findall(r'\d+\s*%|\d+\s*(users|students|projects|clients)', text, re.I)
    if nums: s+=10; rows.append(("✓",f"{len(nums)} quantified achievement(s)",10,"#16a34a"))
    else:           rows.append(("✗","No quantified achievements",0,"#dc2626"))
    verbs = [v for v in
             ["developed","built","designed","implemented","led","created","improved","deployed"]
             if re.search(r'\b'+v+r'\b', text, re.I)]
    if len(verbs)>=3: s+=10; rows.append(("✓",f"Action verbs: {', '.join(verbs[:4])}",10,"#16a34a"))
    else:             rows.append(("○","Add more strong action verbs",0,"#c97b10"))
    return min(s,100), rows

def calc_match(skills, jd):
    if not jd: return 0,[],[]
    jl = jd.lower()
    js = set(s for s in SKILLS_DB if re.search(r'\b'+re.escape(s)+r'\b', jl))
    if not js: return 0,[],[]
    rs = set(skills)
    return round(len(rs&js)/len(js)*100), sorted(rs&js), sorted(js-rs)

def calc_tone(text):
    tl  = text.lower()
    raw = {t: len(re.findall(p, tl, re.I)) for t,p in TONE_PAT.items()}
    tot = max(sum(raw.values()), 1)
    return {k: round(v/tot*100) for k,v in raw.items()}

def gen_questions(parsed, jd, role):
    prompt = f"""Generate exactly 6 interview questions for a {role or 'tech'} candidate.
Candidate skills: {', '.join(parsed.get('skills',[])[:10])}.
JD context: {jd[:400] if jd else 'general tech role'}.
Include: 2 TECHNICAL, 2 BEHAVIORAL, 1 SITUATIONAL, 1 CAREER question.
Format — each line exactly: [TYPE] Question text
No preamble, no numbering, 6 lines only."""
    res, err = call_gemini(prompt, 500)
    if err: return [{"type":"ERROR","q":f"Error: {err}"}]
    qs = []
    for line in res.splitlines():
        line = line.strip()
        if not line: continue
        m = re.match(r'\[([A-Z\-]+)\]\s*(.*)', line)
        if m: qs.append({"type":m.group(1),"q":m.group(2)})
        else: qs.append({"type":"GENERAL","q":line})
    return qs[:6]

def eval_answer(q, a, role):
    res, err = call_gemini(f"""Evaluate this interview answer for a {role or 'tech'} role.
Question: {q}
Answer: {a}
Reply in EXACTLY this format, nothing else:
SCORE: [integer 1-10]
STRENGTH: [one sentence]
IMPROVE: [one sentence]
SAMPLE: [two-sentence better answer]""", 380)
    out = {"score":6,"strength":"","improve":"","sample":""}
    if err: out["strength"] = f"Error: {err}"; return out
    for line in (res or "").splitlines():
        if   line.startswith("SCORE:"):    
            try: out["score"] = int(re.search(r'\d+', line).group())
            except: pass
        elif line.startswith("STRENGTH:"): out["strength"] = line[9:].strip()
        elif line.startswith("IMPROVE:"):  out["improve"]  = line[8:].strip()
        elif line.startswith("SAMPLE:"):   out["sample"]   = line[7:].strip()
    return out

# ── Render micro-components ───────────────────────────────────────────────────
def render_pbar(label, val, total=100, color="#0ea5a0"):
    pct = round(val/total*100) if total else 0
    st.markdown(f"""<div class="pb">
<div class="pb-row"><span>{label}</span>
<span class="pb-val" style="color:{color}">{val}<span style="color:var(--text-3);font-weight:400">/{total}</span></span></div>
<div class="pb-track"><div class="pb-fill" style="width:{pct}%;background:{color}"></div></div>
</div>""", unsafe_allow_html=True)

def render_tags(items, cls, fallback="None detected"):
    if not items:
        st.markdown(f'<span style="font-size:.76rem;color:var(--text-4)">{fallback}</span>',
                    unsafe_allow_html=True); return
    html = '<div class="taglist">' + \
           "".join(f'<span class="tag {cls}">{i}</span>' for i in items) + '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_divlbl(t):
    st.markdown(f'<div class="div-lbl">{t}</div>', unsafe_allow_html=True)

def render_empty(icon, heading, sub):
    st.markdown(f"""<div class="empty">
<div class="empty-ico">{icon}</div>
<div class="empty-h">{heading}</div>
<div class="empty-s">{sub}</div>
</div>""", unsafe_allow_html=True)

def render_callout(text):
    st.markdown(f'<div class="callout">{text}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""<div class="sb-brand">
  <div class="sb-brand-name">Career<em>Lens</em></div>
  <div class="sb-brand-sub">AI RESUME INTELLIGENCE</div>
</div>""", unsafe_allow_html=True)

    # Nav
    st.markdown('<div class="sb-group">Navigate</div>', unsafe_allow_html=True)

    NAV = [
        ("◈", "Overview",    "Dashboard & KPIs"),
        ("↑", "Resume",      "Upload & ATS score"),
        ("⌖", "JD Match",    "Skill gap analysis"),
        ("◉", "Skills",      "Skill breakdown"),
        ("◎", "Tone",        "Writing tone profile"),
        ("◷", "Interview",   "AI practice questions"),
        ("⬡", "Report",      "Export your report"),
    ]
    for icon, label, _ in NAV:
        active = st.session_state.page == label
        if active:
            st.markdown('<div class="sb-active-nav">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"sb_{label}", use_container_width=True):
            st.session_state.page = label
            st.rerun()
        if active:
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # Resume summary card
    if st.session_state.analysis_done:
        p = st.session_state.parsed
        st.markdown(f"""<div class="sb-card">
  <div class="sb-card-title">{p['name']}</div>
  <div class="sb-card-body">{p['emails'][0] if p['emails'] else '—'}</div>
  <div class="sb-card-stat">
    <div class="sb-stat"><div class="sb-stat-val">{st.session_state.ats}</div><div class="sb-stat-lbl">ATS</div></div>
    <div class="sb-stat"><div class="sb-stat-val">{st.session_state.match}%</div><div class="sb-stat-lbl">Match</div></div>
    <div class="sb-stat"><div class="sb-stat-val">{len(p['skills'])}</div><div class="sb-stat-lbl">Skills</div></div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="sb-card"><div class="sb-card-body">No resume uploaded yet.</div></div>',
                    unsafe_allow_html=True)

    # API key
    if not get_api_key():
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        ki = st.text_input("", type="password", placeholder="◈ Gemini API key",
                           label_visibility="collapsed", key="ki")
        if ki:
            st.session_state.api_key = ki
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
#  TOPBAR
# ─────────────────────────────────────────────────────────────────────────────
PAGE_META = {
    "Overview":  ("Overview",          "Career intelligence at a glance"),
    "Resume":    ("Resume Analysis",   "ATS scoring and profile extraction"),
    "JD Match":  ("JD Match",          "Skill gap against a job description"),
    "Skills":    ("Skills",            "Technical and soft skill breakdown"),
    "Tone":      ("Tone Profile",      "Language tone and personality signal"),
    "Interview": ("Interview Prep",    "AI questions with scored feedback"),
    "Report":    ("Export Report",     "Download your full analysis as JSON"),
}
pg          = st.session_state.page
tb_t, tb_s  = PAGE_META.get(pg, (pg,""))
api_ok      = bool(get_api_key())

badge_api   = f'<span class="badge {"badge-green" if api_ok else "badge-amber"}">{"✓ AI ready" if api_ok else "⚠ No API key"}</span>'
badge_resume= '<span class="badge badge-teal">◈ Resume loaded</span>' \
              if st.session_state.analysis_done else ""

st.markdown(f"""<div class="topbar">
  <div>
    <div class="tb-title">{tb_t}</div>
    <div class="tb-sub">{tb_s}</div>
  </div>
  <div class="tb-right">{badge_api}{badge_resume}</div>
</div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="page">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
#  OVERVIEW
# ═══════════════════════════════════════════════════
if pg == "Overview":
    p      = st.session_state.parsed
    ats    = st.session_state.ats
    match  = st.session_state.match
    n_sk   = len(p.get("skills", []))
    n_edu  = len(p.get("education", []))

    # Hero
    st.markdown(f"""<div class="hero">
  <div class="hero-eyebrow">AI · Resume · Intelligence</div>
  <div class="hero-heading">Build a resume that<br><i>gets you hired.</i></div>
  <div class="hero-body">Instant ATS scoring, job description matching, tone analysis,
  and personalised interview coaching — all powered by Gemini AI.</div>
  <div class="hero-kpis">
    <div><div class="kpi-val">{ats}</div><div class="kpi-lbl">ATS Score</div></div>
    <div><div class="kpi-val">{match}%</div><div class="kpi-lbl">JD Match</div></div>
    <div><div class="kpi-val">{n_sk}</div><div class="kpi-lbl">Skills</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    # KPI tiles
    c1,c2,c3,c4 = st.columns(4)
    for col, val, lbl, clr, grad in [
        (c1, str(ats),    "ATS Score",  score_color(ats),   f"linear-gradient(90deg,{score_color(ats)},{score_color(ats)}66)"),
        (c2, f"{match}%", "JD Match",   score_color(match), f"linear-gradient(90deg,{score_color(match)},{score_color(match)}66)"),
        (c3, str(n_sk),   "Skills",     "#0ea5a0",           "linear-gradient(90deg,#0ea5a0,#5eead4)"),
        (c4, str(n_edu),  "Education",  "#7c3aed",           "linear-gradient(90deg,#7c3aed,#c4b5fd)"),
    ]:
        with col:
            st.markdown(f"""<div class="kpi-tile">
  <div class="kpi-tile-bar" style="background:{grad}"></div>
  <div class="kpi-tile-val" style="color:{clr}">{val}</div>
  <div class="kpi-tile-lbl">{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick action grid
    st.markdown('<div style="font-family:\'Instrument Serif\',serif;font-size:.95rem;color:var(--text-1);margin-bottom:10px">What would you like to do?</div>',
                unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col, ico, h, s, dest in [
        (c1,"📄","Analyse Resume","Upload your CV for instant ATS scoring","Resume"),
        (c2,"🔗","Match to JD",   "Find gaps between your skills and a job post","JD Match"),
        (c3,"🎤","Interview Prep","AI questions + scored answer feedback","Interview"),
        (c4,"📊","Export Report", "Download your full JSON analysis report","Report"),
    ]:
        with col:
            st.markdown(f"""<div class="qa-tile">
  <div class="qa-ico">{ico}</div>
  <div class="qa-h">{h}</div>
  <div class="qa-s">{s}</div>
</div>""", unsafe_allow_html=True)
            if st.button("Open →", key=f"qa_{dest}", use_container_width=True):
                st.session_state.page = dest; st.rerun()

# ═══════════════════════════════════════════════════
#  RESUME
# ═══════════════════════════════════════════════════
elif pg == "Resume":
    col_l, col_r = st.columns([1.5, 1], gap="large")

    with col_l:
        st.markdown('<div class="page-header"><div class="page-title">Upload Resume</div><div class="page-sub">PDF, DOCX, or image. We extract, parse, and score it automatically.</div></div>',
                    unsafe_allow_html=True)

        st.markdown('<div class="upload-zone"><span class="uz-ico">📋</span><div class="uz-h">Drop your resume here</div><div class="uz-s">PDF · DOCX · PNG · JPG</div></div>',
                    unsafe_allow_html=True)
        uploaded = st.file_uploader("", type=["pdf","docx","png","jpg","jpeg"],
                                    label_visibility="collapsed")
        if uploaded:
            ext = os.path.splitext(uploaded.name)[1].lower()
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded.getbuffer()); path = tmp.name
            with st.spinner("Extracting and analysing…"):
                text = extract_text(path)
            if text.strip():
                parsed        = parse_resume(text)
                ats, reasons  = calc_ats(text, parsed["skills"])
                st.session_state.update({
                    "resume_text": text, "resume_name": uploaded.name,
                    "parsed": parsed, "ats": ats, "ats_reasons": reasons,
                    "tone": calc_tone(text), "analysis_done": True,
                })
                st.success(f"✓  Parsed — {len(parsed['skills'])} skills detected, ATS score {ats}/100.")
            else:
                st.error("Could not extract text. Try a PDF or DOCX file.")

        # ATS card
        if st.session_state.analysis_done:
            p   = st.session_state.parsed
            ats = st.session_state.ats
            clr = score_color(ats); lbl, bb, bc = score_label(ats)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">ATS Score Breakdown</div>', unsafe_allow_html=True)

            ra, rb = st.columns([1, 2])
            with ra:
                st.markdown(f"""<div class="score-ring">
  <div class="score-num" style="color:{clr}">{ats}</div>
  <div class="score-den">out of 100</div>
  <div class="score-tag" style="background:{bb};border-color:{bc};color:{clr}">{lbl}</div>
</div>""", unsafe_allow_html=True)
            with rb:
                render_divlbl("Checklist")
                for icon, reason, pts, clr2 in st.session_state.ats_reasons:
                    st.markdown(f"""<div class="brow">
  <span class="brow-icon" style="color:{clr2}">{icon}</span>
  <span class="brow-pts" style="color:{clr2}">+{pts}</span>
  <span>{reason}</span>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col_r:
        if st.session_state.analysis_done:
            p = st.session_state.parsed

            # Profile block
            st.markdown(f"""<div class="profile">
  <div class="profile-name">{p['name']}</div>
  <div class="profile-sub">{p['emails'][0] if p['emails'] else '—'}</div>
  {'<div class="profile-sub">' + p["phones"][0] + '</div>' if p.get("phones") else ''}
  <div class="profile-grid">
    <div><div class="profile-stat-v">{len(p['skills'])}</div><div class="profile-stat-l">Skills</div></div>
    <div><div class="profile-stat-v">{ats}</div><div class="profile-stat-l">ATS</div></div>
    <div><div class="profile-stat-v">{len(p['education'])}</div><div class="profile-stat-l">Edu</div></div>
  </div>
</div>""", unsafe_allow_html=True)

            # Progress card
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Scores</div>', unsafe_allow_html=True)
            render_pbar("ATS Score",    st.session_state.ats,   100, score_color(st.session_state.ats))
            render_pbar("Hard Skills",  len([s for s in p["skills"] if s not in SOFT]), 30, "#0ea5a0")
            render_pbar("Soft Skills",  len([s for s in p["skills"] if s in SOFT]),     10, "#c97b10")
            if st.session_state.match:
                render_pbar("JD Match", st.session_state.match, 100, score_color(st.session_state.match))
            st.markdown('</div>', unsafe_allow_html=True)

            # Education
            if p.get("education"):
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown('<div class="card-head">Education</div>', unsafe_allow_html=True)
                for e in p["education"][:4]:
                    st.markdown(f'<div style="font-size:.78rem;color:var(--text-2);padding:5px 0;border-bottom:1px solid var(--border)">· {e[:72]}{"…" if len(e)>72 else ""}</div>',
                                unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            render_empty("📤", "No resume yet",
                         "Upload a file on the left to get started.")

# ═══════════════════════════════════════════════════
#  JD MATCH
# ═══════════════════════════════════════════════════
elif pg == "JD Match":
    if not st.session_state.analysis_done:
        st.info("Please upload a resume in **Resume** first.")
    else:
        col_l, col_r = st.columns([1, 1.2], gap="large")
        with col_l:
            st.markdown('<div class="page-header"><div class="page-title">JD Match</div><div class="page-sub">Paste a job description to see how well your skills align.</div></div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Job Description</div>', unsafe_allow_html=True)
            jd = st.text_area("", height=190,
                              placeholder="Paste the full job description here…",
                              label_visibility="collapsed", key="jd_box")
            role = st.text_input("Target Role", placeholder="e.g. Data Scientist, ML Engineer")
            if st.button("Analyse Match →", use_container_width=True):
                ms, mt, mi = calc_match(st.session_state.parsed["skills"], jd)
                st.session_state.match   = ms
                st.session_state.matched = mt
                st.session_state.missing = mi
                st.session_state.jd_text = jd
                if role: st.session_state.job_role = role
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            match = st.session_state.match
            clr   = score_color(match); lbl, bb, bc = score_label(match)

            st.markdown(f"""<div class="card">
  <div class="card-head">Match Score</div>
  <div class="score-ring">
    <div class="score-num" style="color:{clr}">{match}%</div>
    <div class="score-den">skill overlap</div>
    <div class="score-tag" style="background:{bb};border-color:{bc};color:{clr}">{lbl}</div>
  </div>
</div>""", unsafe_allow_html=True)

            # Pie chart
            if st.session_state.matched or st.session_state.missing:
                fig, ax = plt.subplots(figsize=(3.6,3.6), facecolor="#fafaf9")
                sizes  = [max(len(st.session_state.matched),1), max(len(st.session_state.missing),1)]
                ax.pie(sizes,
                       labels  = [f"Matched\n{len(st.session_state.matched)}",
                                   f"Missing\n{len(st.session_state.missing)}"],
                       colors  = ["#0ea5a0","#dc2626"],
                       autopct = "%1.0f%%", startangle=90,
                       textprops={"color":"#1c1c1e","fontsize":9},
                       wedgeprops={"edgecolor":"#fafaf9","linewidth":3})
                ax.set_facecolor("#fafaf9"); fig.patch.set_facecolor("#fafaf9")
                st.pyplot(fig); plt.close()

            st.markdown('<div class="card">', unsafe_allow_html=True)
            render_divlbl("✓ Skills You Have")
            render_tags(st.session_state.matched, "t-green")
            render_divlbl("✗ Skills to Add")
            render_tags(st.session_state.missing, "t-red")
            if st.session_state.missing:
                top4 = ", ".join(st.session_state.missing[:4])
                render_callout(f'Adding <b>{top4}</b> to your resume could significantly boost your match.')
            elif st.session_state.matched:
                st.markdown('<div style="color:#16a34a;font-size:.8rem;font-weight:600;margin-top:10px">🎉 No skill gaps — excellent match!</div>',
                            unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
#  SKILLS
# ═══════════════════════════════════════════════════
elif pg == "Skills":
    if not st.session_state.analysis_done:
        st.info("Please upload a resume in **Resume** first.")
    else:
        p    = st.session_state.parsed
        text = st.session_state.resume_text
        hard = [s for s in p["skills"] if s not in SOFT]
        soft = [s for s in p["skills"] if s in SOFT]

        st.markdown('<div class="page-header"><div class="page-title">Skills</div><div class="page-sub">Extracted skills with frequency analysis.</div></div>',
                    unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 1.1], gap="large")

        with col_a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Technical Skills <span class="card-head-tag">Hard</span></div>',
                        unsafe_allow_html=True)
            render_tags(hard, "t-teal")
            render_divlbl("Soft Skills")
            render_tags(soft, "t-amber")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Coverage</div>', unsafe_allow_html=True)
            render_pbar("Technical Skills", len(hard), 30, "#0ea5a0")
            render_pbar("Soft Skills",      len(soft), 10, "#c97b10")
            render_pbar("Total Skills",     len(p["skills"]), 40, "#7c3aed")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            if p["skills"]:
                top    = p["skills"][:14]
                counts = [max(1, len(re.findall(r'\b'+re.escape(s)+r'\b', text.lower())))
                          for s in top]
                colors_b = ["#0ea5a0" if s not in SOFT else "#c97b10" for s in top]
                fig, ax = plt.subplots(figsize=(5.5, 5.2), facecolor="#fafaf9")
                ax.barh(top, counts, color=colors_b, edgecolor="none", height=0.6)
                ax.set_facecolor("#fafaf9"); fig.patch.set_facecolor("#fafaf9")
                ax.tick_params(colors="#4a4a52", labelsize=8.5)
                for sp in ax.spines.values(): sp.set_color("#e7e5e0")
                ax.set_xlabel("Mentions", color="#8e8e9a", fontsize=8)
                ax.set_title("Top Skills by Frequency", color="#1c1c1e",
                             fontsize=10.5, fontweight="bold", pad=10)
                fig.tight_layout(); st.pyplot(fig); plt.close()
                st.markdown('<div style="display:flex;gap:14px;margin-top:6px;font-size:.72rem;color:var(--text-3)"><span><span style="display:inline-block;width:9px;height:9px;background:#0ea5a0;border-radius:2px;margin-right:4px;vertical-align:middle"></span>Technical</span><span><span style="display:inline-block;width:9px;height:9px;background:#c97b10;border-radius:2px;margin-right:4px;vertical-align:middle"></span>Soft</span></div>',
                            unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
#  TONE
# ═══════════════════════════════════════════════════
elif pg == "Tone":
    if not st.session_state.analysis_done:
        st.info("Please upload a resume in **Resume** first.")
    else:
        tone = st.session_state.tone
        dom  = max(tone, key=tone.get) if tone else "—"
        dc   = TONE_CLR.get(dom, "#0ea5a0")

        st.markdown('<div class="page-header"><div class="page-title">Tone Profile</div><div class="page-sub">How your resume reads to a recruiter based on language patterns.</div></div>',
                    unsafe_allow_html=True)
        col_a, col_b = st.columns([1, 1], gap="large")

        with col_a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Tone Breakdown</div>', unsafe_allow_html=True)
            for t, pct in sorted(tone.items(), key=lambda x: -x[1]):
                clr = TONE_CLR.get(t,"#0ea5a0")
                st.markdown(f"""<div class="tone-row">
  <div class="tone-n">{t}</div>
  <div class="tone-track"><div class="tone-fill" style="width:{pct}%;background:{clr}"></div></div>
  <div class="tone-pct" style="color:{clr}">{pct}%</div>
</div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="margin-top:16px;padding:12px 14px;background:var(--teal-bg);border:1px solid var(--teal-bd);border-radius:9px">
  <div style="font-size:.59rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--teal);margin-bottom:4px">Dominant Tone</div>
  <div style="font-family:'Instrument Serif',serif;font-size:1.3rem;color:{dc}">{dom}</div>
  <div style="font-size:.75rem;color:var(--text-3);margin-top:4px;line-height:1.5">Your resume reads primarily as <b style="color:{dc}">{dom.lower()}</b>.</div>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("""<div class="card">
  <div class="card-head">Tone Guide</div>
  <div style="font-size:.78rem;color:var(--text-2);line-height:2.1">
    <span style="color:#0ea5a0;font-weight:600">Technical</span> — depth in tools and systems<br>
    <span style="color:#7c3aed;font-weight:600">Leadership</span> — managing and influencing<br>
    <span style="color:#16a34a;font-weight:600">Analytical</span> — data-driven problem solving<br>
    <span style="color:#c97b10;font-weight:600">Creative</span> — design and innovation<br>
    <span style="color:#be185d;font-weight:600">Collaborative</span> — cross-functional teamwork<br>
    <span style="color:#0369a1;font-weight:600">Results-Driven</span> — measurable outcomes
  </div>
</div>""", unsafe_allow_html=True)

        with col_b:
            cats   = list(tone.keys())
            vals   = [tone[c] for c in cats]
            N      = len(cats)
            angles = [n/float(N)*2*math.pi for n in range(N)]
            a2 = angles + angles[:1]; v2 = vals + vals[:1]
            fig, ax = plt.subplots(figsize=(5,5), subplot_kw=dict(polar=True), facecolor="#fafaf9")
            ax.set_facecolor("#f0fffe"); fig.patch.set_facecolor("#fafaf9")
            ax.plot(a2, v2, linewidth=2, color="#0ea5a0")
            ax.fill(a2, v2, alpha=0.15, color="#0ea5a0")
            ax.set_xticks(angles)
            ax.set_xticklabels(cats, color="#4a4a52", fontsize=8.5)
            ax.set_yticklabels([])
            ax.grid(color="#e7e5e0")
            ax.spines["polar"].set_color("#e7e5e0")
            st.pyplot(fig); plt.close()

# ═══════════════════════════════════════════════════
#  INTERVIEW
# ═══════════════════════════════════════════════════
elif pg == "Interview":
    if not st.session_state.analysis_done:
        st.info("Please upload a resume in **Resume** first.")
    else:
        parsed = st.session_state.parsed
        TYPE_C = {"TECHNICAL":"#0ea5a0","BEHAVIORAL":"#7c3aed","SITUATIONAL":"#c97b10",
                  "CAREER":"#16a34a","GENERAL":"#8e8e9a","ERROR":"#dc2626"}
        TYPE_I = {"TECHNICAL":"💻","BEHAVIORAL":"🤝","SITUATIONAL":"🧩",
                  "CAREER":"🚀","GENERAL":"💬","ERROR":"⚠"}

        st.markdown('<div class="page-header"><div class="page-title">Interview Prep</div><div class="page-sub">AI-generated questions personalised to your resume. Answer each one for scored feedback.</div></div>',
                    unsafe_allow_html=True)

        r_role, r_btn = st.columns([2.5, 1])
        with r_role:
            iv_role = st.text_input("Target Role",
                                    placeholder="e.g. Data Scientist, ML Engineer, Backend Developer",
                                    value=st.session_state.job_role, key="iv_role")
        with r_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate Questions ⚡", use_container_width=True):
                if not get_api_key():
                    st.warning("Enter your Gemini API key in the sidebar first.")
                else:
                    with st.spinner("Generating with Gemini AI…"):
                        qs = gen_questions(parsed, st.session_state.jd_text, iv_role)
                        st.session_state.iq  = qs
                        st.session_state.ifb = {}

        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.iq:
            render_empty("🎤", "No questions yet",
                         "Enter a target role and click Generate Questions.")
        else:
            for i, q in enumerate(st.session_state.iq):
                qtype = q.get("type","GENERAL")
                qtext = q.get("q","")
                clr   = TYPE_C.get(qtype,"#8e8e9a")
                icon  = TYPE_I.get(qtype,"💬")

                st.markdown(f"""<div class="qcard">
  <div class="qcard-type" style="color:{clr}">{icon}  {qtype}</div>
  <div class="qcard-text">{qtext}</div>
</div>""", unsafe_allow_html=True)

                ans = st.text_area("", height=84, key=f"ans_{i}",
                                   label_visibility="collapsed",
                                   placeholder="Write your answer here for AI feedback…")
                c_btn, _ = st.columns([1, 3])
                with c_btn:
                    if st.button("Evaluate →", key=f"ev_{i}"):
                        if ans.strip():
                            with st.spinner("Scoring…"):
                                st.session_state.ifb[i] = eval_answer(qtext, ans, iv_role)
                        else:
                            st.warning("Please write an answer first.")

                if i in st.session_state.ifb:
                    fb  = st.session_state.ifb[i]
                    sv  = fb.get("score",0)
                    sc2 = score_color(sv*10)
                    bb2 = "#f0fdf4" if sv>=8 else "#fffbeb" if sv>=6 else "#fef2f2"
                    bc2 = "#86efac" if sv>=8 else "#fcd34d" if sv>=6 else "#fca5a5"
                    st.markdown(f"""<div class="fb-box">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
    <div class="fb-num" style="color:{sc2}">{sv}<span style="font-size:.9rem;color:var(--text-3)">/10</span></div>
    <div style="padding:3px 11px;border-radius:20px;background:{bb2};border:1px solid {bc2};color:{sc2};font-size:.7rem;font-weight:700">{"Excellent 🏆" if sv>=8 else "Good ✓" if sv>=6 else "Needs Work"}</div>
  </div>
  <div class="fb-row"><b style="color:#16a34a">Strength —</b> {fb.get('strength','')}</div>
  <div class="fb-row"><b style="color:#c97b10">Improve —</b> {fb.get('improve','')}</div>
  <div class="fb-row"><b style="color:#0ea5a0">Better answer —</b> {fb.get('sample','')}</div>
</div>""", unsafe_allow_html=True)
                st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════
#  REPORT
# ═══════════════════════════════════════════════════
elif pg == "Report":
    if not st.session_state.analysis_done:
        st.info("Please upload a resume in **Resume** first.")
    else:
        p = st.session_state.parsed
        report = {
            "candidate":      p["name"],
            "emails":         p["emails"],
            "ats_score":      st.session_state.ats,
            "jd_match_pct":   st.session_state.match,
            "matched_skills": st.session_state.matched,
            "missing_skills": st.session_state.missing,
            "hard_skills":    [s for s in p["skills"] if s not in SOFT],
            "soft_skills":    [s for s in p["skills"] if s in SOFT],
            "dominant_tone":  max(st.session_state.tone, key=st.session_state.tone.get)
                              if st.session_state.tone else "",
            "education":      p.get("education",[]),
        }

        st.markdown('<div class="page-header"><div class="page-title">Export Report</div><div class="page-sub">Your full analysis summary, ready to download.</div></div>',
                    unsafe_allow_html=True)

        col_a, col_b = st.columns([1.2, 1], gap="large")
        with col_a:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Score Summary</div>', unsafe_allow_html=True)
            render_pbar("ATS Score",   st.session_state.ats,   100, score_color(st.session_state.ats))
            render_pbar("JD Match",    st.session_state.match, 100, score_color(st.session_state.match))
            render_pbar("Hard Skills", len([s for s in p["skills"] if s not in SOFT]), 30, "#0ea5a0")
            render_pbar("Soft Skills", len([s for s in p["skills"] if s in SOFT]),     10, "#c97b10")
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                "⬇  Download JSON Report",
                data=json.dumps(report, indent=2),
                file_name=f"{p['name'].replace(' ','_')}_careerlens.json",
                mime="application/json",
                use_container_width=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("↺  Start Over", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k not in ("api_key",): del st.session_state[k]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            # Candidate summary card
            dom  = max(st.session_state.tone, key=st.session_state.tone.get) \
                   if st.session_state.tone else "—"
            dc   = TONE_CLR.get(dom,"#0ea5a0")

            st.markdown(f"""<div class="profile">
  <div class="profile-name">{p['name']}</div>
  <div class="profile-sub">{p['emails'][0] if p['emails'] else '—'}</div>
  <div class="profile-grid">
    <div><div class="profile-stat-v">{st.session_state.ats}</div><div class="profile-stat-l">ATS</div></div>
    <div><div class="profile-stat-v">{st.session_state.match}%</div><div class="profile-stat-l">Match</div></div>
    <div><div class="profile-stat-v">{len(p['skills'])}</div><div class="profile-stat-l">Skills</div></div>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-head">Top Skills</div>', unsafe_allow_html=True)
            render_tags(p["skills"][:12], "t-teal")
            st.markdown(f"""<div style="margin-top:14px;padding:11px 13px;background:var(--teal-bg);border:1px solid var(--teal-bd);border-radius:8px">
  <div style="font-size:.59rem;font-weight:700;text-transform:uppercase;letter-spacing:2px;color:var(--teal);margin-bottom:3px">Dominant Tone</div>
  <div style="font-family:'Instrument Serif',serif;font-size:1.2rem;color:{dc}">{dom}</div>
</div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)   # .page


