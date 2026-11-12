import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from io import BytesIO


# =========================================================
# 1. 페이지 설정
# =========================================================

st.set_page_config(
    page_title="멸종 위기 동물 데이터 탐색실",
    page_icon="🐾",
    layout="wide"
)


# =========================================================
# 2. 디자인 설정
# =========================================================

st.markdown(unsafe_allow_html=True)
<style>
    .stApp {
        background-color: #F1F7FD;
    }

    .main-title {
        background: linear-gradient(120deg, #174A78, #4F91C7);
        color: white;
        padding: 35px 30px;
        border-radius: 18px;
        margin-bottom: 22px;
    }

    .main-title h1 {
        color: white;
        font-size: 32px;
        margin-bottom: 8px;
    }

    .main-title p {
        color: #EAF4FC;
        font-size: 15px;
        margin-bottom: 0;
    }

    .section-title {
        color: #174A78;
        font-weight: 700;
        font-size: 23px;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    .animal-name {
        color: #174A78;
        font-size: 21px;
        font-weight: 700;
    }

    .animal-scientific {
        color: #777777;
        font-size: 13px;
        font-style: italic;
    }

    .animal-emoji {
        font-size: 43px;
        text-align: center;
    }

    .book-note {
        background-color: #E8F3FC;
        padding: 16px;
        border-radius: 12px;
        color: #28577F;
        margin: 12px 0;
    }

    .cover-box {
        background: linear-gradient(135deg, #174A78, #76936C);
        color: white;
        border-radius: 20px;
        padding: 45px 30px;
        text-align: center;
        margin-bottom: 20px;
    }

    .cover-box h1 {
        color: white;
        font-size: 36px;
    }

    .cover-box p {
