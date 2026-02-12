import streamlit as st
from controllers import CaronaController

st.set_page_config(page_title="Carona", layout="wide")

if __name__ == "__main__":
    app = CaronaController()
    app.run()