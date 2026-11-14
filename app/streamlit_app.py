"""Afterlife demo app. Owner: Role B. Milestone M7.
Run: streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import streamlit as st
from afterlife.io import load, data_dir

st.set_page_config(page_title="Afterlife", layout="wide")
st.title("Afterlife")
st.caption(f"Data: {data_dir()}")
tables = load()

tab1, tab2, tab3 = st.tabs(["1 · Linking", "2 · Early warning", "3 · Supplier brief"])
with tab1:
    st.write("TODO(B): coverage before/after, accuracy from evaluate.py")
    for name, df in tables.items():
        st.write(f"**{name}**: {len(df)} rows")
with tab2:
    st.write("TODO(B): alerts table + claim-rate-by-build-month chart with spike highlighted")
with tab3:
    st.write("TODO(B): pick supplier -> render brief")
