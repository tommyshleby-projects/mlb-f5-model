import streamlit as st
import pandas as pd
from pybaseball import pitching_stats

# Team Name Mapping
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

st.set_page_config(page_title="TommyShleby F5 Comparison", layout="wide")
st.title("⚾ MLB First 5 (F5) Pitcher Comparison")

@st.cache_data
def load_all_stats():
    # Pulling both 2025 and 2026 to ensure we have a full "Top 3" list
    data_25 = pitching_stats(2025)
    data_26 = pitching_stats(2026)
    return pd.concat([data_25, data_26], ignore_index=True)

try:
    df = load_all_stats()
    df['Full Team'] = df['Team'].map(TEAM_MAP)
    
    selected_team = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    team_df = df[df['Full Team'] == selected_team].copy()

    # Split for clear comparison
    df_25 = team_df[team_df['Season'] == 2025]
    df_26 = team_df[team_df['Season'] == 2026]

    st.header(f"Pitching Analysis: {selected_team}")

    # Top 3 from 2025 (The Baseline)
    st.subheader("🔥 2025 Top 3 (Baseline)")
    top_3_25 = df_25.sort_values(by=['ERA', 'WHIP']).head(3)
    cols = st.columns(3)
    for i, (_, row) in enumerate(top_3_25.iterrows()):
        with cols[i]:
            st.metric(f"{row['Name']}", f"ERA: {row['ERA']}", f"WHIP: {row['WHIP']}", delta_color="inverse")

    st.divider()

    # 2026 Current Stats (Updates automatically as games are played)
    st.subheader("📈 2026 Current Performance")
    if not df_26.empty:
        st.dataframe(df_26[['Name', 'ERA', 'WHIP', 'K/9', 'BB/9']])
    else:
        st.info("Regular Season starts March 25th. 2026 stats will appear here after the first pitch!")

except Exception as e:
    st.error(f"Error loading data: {e}")