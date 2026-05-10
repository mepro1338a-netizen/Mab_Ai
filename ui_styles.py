import streamlit as st

GLOBAL_CSS = """

<style>

html, body, [class*="css"]{
    font-family: 'Inter', sans-serif;
}

.stApp{
    background:
    radial-gradient(circle at top left,#1d4ed8 0%,transparent 25%),
    radial-gradient(circle at bottom right,#2563eb 0%,transparent 20%),
    linear-gradient(135deg,#050816,#091224,#0f172a);
    color:white;
}

/* Sidebar */

section[data-testid="stSidebar"]{
    background:linear-gradient(180deg,#071122,#0f172a);
    border-right:1px solid rgba(59,130,246,0.25);
}

/* Buttons */

.stButton button{
    width:100%;
    border:none;
    border-radius:18px;
    padding:14px;
    background:linear-gradient(90deg,#2563eb,#38bdf8);
    color:white;
    font-weight:700;
    transition:0.3s;
    box-shadow:0 0 20px rgba(37,99,235,0.35);
}

.stButton button:hover{
    transform:translateY(-2px) scale(1.01);
    box-shadow:0 0 30px rgba(56,189,248,0.45);
}

/* Inputs */

.stTextInput input,
.stTextArea textarea{
    background:#091427 !important;
    color:white !important;
    border:1px solid rgba(59,130,246,0.35) !important;
    border-radius:18px !important;
}

/* Cards */

.glass-card{
    background:rgba(15,23,42,0.82);
    border:1px solid rgba(59,130,246,0.25);
    border-radius:28px;
    padding:30px;
    backdrop-filter: blur(18px);
    box-shadow:0 0 40px rgba(37,99,235,0.22);
}

/* Hero */

.hero-title{
    font-size:72px;
    font-weight:900;
    color:white;
    line-height:1;
}

.hero-sub{
    margin-top:20px;
    font-size:24px;
    color:#cbd5e1;
    line-height:1.6;
}

/* Tool Cards */

.tool-card{
    background:linear-gradient(145deg,#0f172a,#111827);
    border:1px solid rgba(59,130,246,0.25);
    border-radius:28px;
    padding:30px;
    min-height:260px;
    transition:0.3s;
    box-shadow:0 0 25px rgba(37,99,235,0.15);
}

.tool-card:hover{
    transform:translateY(-6px);
    box-shadow:0 0 40px rgba(56,189,248,0.35);
}

.tool-title{
    font-size:32px;
    font-weight:800;
    color:white;
    margin-bottom:18px;
}

.tool-text{
    color:#cbd5e1;
    font-size:18px;
    line-height:1.7;
}

.badge{
    display:inline-block;
    padding:10px 24px;
    border-radius:999px;
    background:linear-gradient(90deg,#2563eb,#38bdf8);
    color:white;
    font-weight:800;
    box-shadow:0 0 25px rgba(56,189,248,0.35);
    margin-bottom:25px;
}

</style>

"""

def load_css():
    st.markdown(
        GLOBAL_CSS,
        unsafe_allow_html=True
    )