import streamlit as st
from coding_service import generate_code

st.title("💻 Coding AI")

prompt = st.text_area("Was soll programmiert werden?")

if st.button("Generate Code"):
    with st.spinner("AI schreibt Code..."):
        success, answer = generate_code(prompt)

    if success:
        st.code(answer, language="python")
    else:
        st.error(answer)