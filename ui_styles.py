import streamlit as st


def load_css():

    st.markdown(
        """
        <style>

        .stApp{
            background:#050505;
            color:white;
        }

        section[data-testid="stSidebar"]{
            background:#0b0b0b;
            border-right:1px solid #1f1f1f;
        }

        .hero-box{
            text-align:center;
            padding:40px 0;
        }

        .hero-title{
            font-size:72px;
            font-weight:800;
            color:white;
            margin-bottom:10px;
        }

        .hero-sub{
            font-size:22px;
            color:#999;
        }

        .feature-card{
            background:#111;
            border:1px solid #222;
            border-radius:20px;
            padding:30px;
            transition:0.3s;
            margin-top:20px;
        }

        .feature-card:hover{
            border:1px solid #ff2b2b;
            transform:translateY(-5px);
        }

        .sidebar-user{
            background:#111;
            padding:15px;
            border-radius:15px;
            border:1px solid #222;
        }

        .stButton button{
            background:linear-gradient(90deg,#ff1f1f,#ff4b4b);
            border:none;
            color:white;
            border-radius:12px;
            font-weight:700;
            padding:12px;
        }

        .stButton button:hover{
            transform:scale(1.02);
        }

        input{
            border-radius:12px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )