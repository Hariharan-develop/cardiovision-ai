import streamlit as st

res = st.html('<script>console.log("top level listener ready");</script>', unsafe_allow_javascript=True)
print("st.html executed without error, returned:", type(res))
