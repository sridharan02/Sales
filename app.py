import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import get_as_dataframe

st.title("Sales Dashboard")

# Auth
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp"],
    scopes=scope
)

gc = gspread.authorize(creds)

# Read sheet
sheet_url = st.secrets["sheet"]["url"]
sh = gc.open_by_url(sheet_url)
worksheet = sh.sheet1

df = get_as_dataframe(worksheet)
df = df.dropna(how='all')

st.write(df.head())

# Basic plots
fig = px.bar(df, x='city', y='sales', title='Revenue by City')
st.plotly_chart(fig)
