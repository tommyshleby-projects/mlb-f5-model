import streamlit as st
import pandas as pd
from pybaseball import pitching_stats

# Team Name Dictionary for full spelling
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
    try:
        # Try 2026 first (current season)
        data = pitching_stats(2026)
        if data is None or data.empty:
            raise ValueError("No 2026 data yet")
    except:
        # Fallback to 2025 (last full season)
        data = pitching_stats(2025)
    return data

try:
    df = load_data()
    df = df[df['Team'].isin(TEAM_MAP.keys())].copy()
    df['Full Team'] = df['Team'].map(TEAM_MAP)

    selected_team = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    team_df = df[df['Full Team'] == selected_team].copy()
    
    st.header(f"Top 3 Starters: {selected_team}")

    # Rank by F5 fundamentals: Lowest ERA and WHIP
    top_3 = team_df.sort_values(by=['ERA', 'WHIP'], ascending=[True, True]).head(3)

    cols = st.columns(3)
    for i, (index, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.metric(f"{row['Name']}", f"ERA: {row['ERA']}")
            st.write(f"**WHIP:** {row['WHIP']} | **K/9:** {row['K/9']}")

    st.divider()
    st.subheader("Full Rotation Stats")
    st.dataframe(team_df[['Name', 'ERA', 'WHIP', 'K/9', 'FIP', 'Season']])

except Exception as e:
    st.error(f"Data Source Error: {e}")
    st.info("The MLB season might be in transition. Try again in a few minutes.")