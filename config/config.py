import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

VECTORSTORE_PATH = "vectorstore"
DATA_PATH = "data"

MODEL_NAME = "gemini-2.5-flash"