import os
import glob
import streamlit as st

st.write("📂 Current working directory:", os.getcwd())
st.write("📄 Python sees these files in cwd:")
st.write(glob.glob("*"))
