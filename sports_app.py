import streamlit as st
import pandas as pd
from pybaseball import pitching_stats

# Team Name Mapping
TEAM_MAP = {
    'ARI': 'Arizona Diamondbacks', # Changed from AZ
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',  # Changed from CWS
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Guardians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals', # Changed from KC
    'LAA': 'Los Angeles Angels',
    'LAD': 'Los Angeles Dodgers',
    'MIA': 'Miami Marlins',
    'MIL': 'Milwaukee Brewers',
    'MIN': 'Minnesota Twins',
    'NYM': 'New York Mets',
    'NYY': 'New York Yankees',
    'OAK': 'Oakland Athletics',
    'PHI': 'Philadelphia Phillies',
    'PIT': 'Pittsburgh Pirates',
    'SDP': 'San Diego Padres',    # Changed from SD
    'SFG': 'San Francisco Giants', # Changed from SF
    'SEA': 'Seattle Mariners',
    'STL': 'St. Louis Cardinals',
    'TBR': 'Tampa Bay Rays',       # Changed from TB
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'  # Changed from WSH
}

st.set_page_config(page_title="TommyShleby F5 Starters", layout="wide")
st.title("⚾ MLB First 5 (F5) Starting Pitcher Analysis")

@st.cache_data
def load_all_stats():
    # Set qual=10 to ensure we have enough data for a meaningful average
    df_25 = pitching_stats(2025, qual=10)
    
    try:
        # 2026 data is still populating; we pull it if it's valid
        df_26 = pitching_stats(2026, qual=1)
        if df_26 is not None and len(df_26.columns) > 1:
            return pd.concat([df_25, df_26], ignore_index=True)
    except Exception:
        pass
        
    return df_25

try:
    df = load_all_stats()
    df['Full Team'] = df['Team'].map(TEAM_MAP)
    
    selected_team = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    
    # --- CRITICAL FILTER: STARTERS ONLY ---
    # We filter for pitchers who have at least 1 Game Started (GS > 0)
    # For the 2025 baseline, we might want GS > 5 to find consistent starters.
    team_df = df[(df['Full Team'] == selected_team) & (df['GS'] > 0)].copy()

    df_25 = team_df[team_df['Season'] == 2025]
    df_26 = team_df[team_df['Season'] == 2026]

    st.header(f"Starting Pitcher Analysis: {selected_team}")

    # Top 3 Starters from 2025
    st.subheader("🔥 2025 Top 3 Starters (Baseline)")
    if not df_25.empty:
        # Filter for consistent starters (e.g., at least 10 starts) to remove "Openers"
        starters_25 = df_25[df_25['GS'] >= 5]
        top_3_25 = starters_25.sort_values(by=['ERA', 'WHIP']).head(3)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(top_3_25.iterrows()):
            with cols[i]:
                st.metric(f"{row['Name']}", f"ERA: {row['ERA']}", f"GS: {int(row['GS'])}")
                st.caption(f"WHIP: {row['WHIP']} | IP: {row['IP']}")
    else:
        st.warning("No starting pitcher data found for 2025.")

    st.divider()

    # 2026 Live Starters
    st.subheader("📈 2026 Starter Performance")
    if not df_26.empty:
        # Only show players who have actually started a game in 2026
        starters_26 = df_26[df_26['GS'] > 0]
        st.dataframe(starters_26[['Name', 'GS', 'ERA', 'WHIP', 'IP', 'Season']])
    else:
        st.info("2026 Regular Season stats will show starters here after Opening Day.")

except Exception as e:
    st.error(f"Error: {e}")
