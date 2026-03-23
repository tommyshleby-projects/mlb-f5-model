import streamlit as st
from pybaseball import pitching_stats
import pandas as pd

st.set_page_config(page_title="Pi Sports Model", layout="wide")

st.title("⚾ MLB Pitching Dashboard (F5 Model)")
st.write("Using real-time Statcast data to find the best First 5 Inning starters.")

@st.cache_data
def get_data():
    # Pull current year stats
    data = pitching_stats(2024) 
    return data[['Name', 'Team', 'FIP', 'K/BB', 'ERA']]

# Load data
df = get_data()

# Sidebar for Team Selection
teams = sorted(df['Team'].unique())
selected_team = st.sidebar.selectbox("Select a Team", teams)

# Filter for the Top 3
team_data = df[df['Team'] == selected_team].sort_values('FIP').head(3)

st.header(f"Top 3 Starters for {selected_team}")
st.table(team_data)

st.info("**F5 Tip:** Focus on FIP and K/BB. If FIP is significantly lower than ERA, that pitcher is 'due' for a dominant start.")

