import streamlit as st
import pandas as pd
from pybaseball import pitching_stats

# 1. Team Name Dictionary
TEAM_MAP = {
    'AZ': 'Arizona Diamondbacks', 'ATL': 'Atlanta Braves', 'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox', 'CHC': 'Chicago Cubs', 'CWS': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds', 'CLE': 'Cleveland Guardians', 'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers', 'HOU': 'Houston Astros', 'KC': 'Kansas City Royals',
    'LAA': 'Los Angeles Angels', 'LAD': 'Los Angeles Dodgers', 'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers', 'MIN': 'Minnesota Twins', 'NYM': 'New York Mets',
    'NYY': 'New York Yankees', 'OAK': 'Oakland Athletics', 'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates', 'SD': 'San Diego Padres', 'SF': 'San Francisco Giants',
    'SEA': 'Seattle Mariners', 'STL': 'St. Louis Cardinals', 'TB': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers', 'TOR': 'Toronto Blue Jays', 'WSH': 'Washington Nationals'
}

st.set_page_config(page_title="TommyShleby F5 Model", layout="wide")
st.title("⚾ 2025-2026 First 5 (F5) Analysis")

@st.cache_data
def load_data():
    # Attempt to get 2026 data; fall back to 2025 if empty
    data = pitching_stats(2026)
    if data.empty:
        data = pitching_stats(2025)
    return data

try:
    df = load_data()
    
    # Filter for active teams and map full names
    df = df[df['Team'].isin(TEAM_MAP.keys())].copy()
    df['Full Team'] = df['Team'].map(TEAM_MAP)

    # Sidebar
    selected_full_name = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    
    # Filter by Team
    team_df = df[df['Full Team'] == selected_full_name].copy()
    
    st.header(f"Top 3 Starters: {selected_full_name}")

    # Top 3 based on ERA/WHIP (F5 Fundamentals)
    top_3 = team_df.sort_values(by=['ERA', 'WHIP'], ascending=[True, True]).head(3)

    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.metric(f"{row['Name']}", f"ERA: {row['ERA']}")
            st.write(f"**WHIP:** {row['WHIP']} | **K/9:** {row['K/9']}")

    st.divider()
    st.subheader("Team Rotation Stats")
    st.dataframe(team_df[['Name', 'ERA', 'WHIP', 'K/9', 'FIP', 'Season']])

except Exception as e:
    st.error(f"Waiting for 2026 Stats: {e}")
    st.write("If the season just started, stats may take 24-48 hours to update.")