import streamlit as st
import pandas as pd
from pybaseball import pitching_stats, statcast_pitcher, playerid_lookup

# Team Name Mapping - Corrected for FanGraphs abbreviations
TEAM_MAP = {
    'ARI': 'Arizona Diamondbacks',
    'ATL': 'Atlanta Braves',
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'CHC': 'Chicago Cubs',
    'CHW': 'Chicago White Sox',
    'CIN': 'Cincinnati Reds',
    'CLE': 'Cleveland Guardians',
    'COL': 'Colorado Rockies',
    'DET': 'Detroit Tigers',
    'HOU': 'Houston Astros',
    'KCR': 'Kansas City Royals',
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
    'SDP': 'San Diego Padres',
    'SFG': 'San Francisco Giants',
    'SEA': 'Seattle Mariners',
    'STL': 'St. Louis Cardinals',
    'TBR': 'Tampa Bay Rays',
    'TEX': 'Texas Rangers',
    'TOR': 'Toronto Blue Jays',
    'WSN': 'Washington Nationals'
}

st.set_page_config(page_title="TommyShleby F5 Starters", layout="wide")
st.title("⚾ MLB First 5 (F5) Starting Pitcher Analysis")

@st.cache_data
def load_all_stats():
    # qual=10 ensures we get the full rotation, not just the top ERA leaders
    df_25 = pitching_stats(2025, qual=10)
    try:
        df_26 = pitching_stats(2026, qual=1)
        if df_26 is not None and len(df_26.columns) > 1:
            return pd.concat([df_25, df_26], ignore_index=True)
    except Exception:
        pass
    return df_25

@st.cache_data
def get_inning_hits(name, year=2025):
    """Pulls pitch-level data to find hits allowed in innings 1-5"""
    try:
        # Split name for lookup
        names = name.split(' ')
        first, last = names[0], names[-1]
        ids = playerid_lookup(last, first)
        if ids.empty: return None
        
        mlb_id = ids.iloc[0]['key_mlbam']
        
        # Pull Statcast data (March to November)
        data = statcast_pitcher(f'{year}-03-01', f'{year}-11-01', mlb_id)
        
        # Filter for hit events
        hit_events = ['single', 'double', 'triple', 'home_run']
        hits = data[data['events'].isin(hit_events)]
        
        # Group by inning and filter for F5
        inning_breakdown = hits.groupby('inning').size().reindex(range(1, 6), fill_value=0)
        return inning_breakdown
    except:
        return None

try:
    df = load_all_stats()
    df['Full Team'] = df['Team'].map(TEAM_MAP)
    
    selected_team = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    
    # Filter for Starters Only
    team_df = df[(df['Full Team'] == selected_team) & (df['GS'] > 0)].copy()

    df_25 = team_df[team_df['Season'] == 2025]
    df_26 = team_df[team_df['Season'] == 2026]

    st.header(f"Starting Pitcher Analysis: {selected_team}")

    # Top 3 Starters from 2025
    st.subheader("🔥 2025 Top 3 Starters (F5 Baseline)")
    if not df_25.empty:
        starters_25 = df_25[df_25['GS'] >= 5]
        top_3_25 = starters_25.sort_values(by=['ERA', 'WHIP']).head(3)
        
        cols = st.columns(3)
        for i, (_, row) in enumerate(top_3_25.iterrows()):
            with cols[i]:
                st.metric(f"{row['Name']}", f"ERA: {row['ERA']}", f"GS: {int(row['GS'])}")
                st.caption(f"WHIP: {row['WHIP']} | K/9: {row['K/9']}")
        
        st.divider()
        st.subheader("📊 F5 Inning-by-Inning Hits (2025 Baseline)")
        st.write("Calculates total hits surrendered per inning across the season.")
        
        hit_cols = st.columns(3)
        for i, (_, row) in enumerate(top_3_25.iterrows()):
            with hit_cols[i]:
                st.write(f"**{row['Name']}**")
                hits_data = get_inning_hits(row['Name'])
                if hits_data is not None:
                    chart_data = pd.DataFrame({'Inning': hits_data.index, 'Hits': hits_data.values})
                    st.bar_chart(chart_data.set_index('Inning'))
                else:
                    st.info("Loading Statcast data...")

    else:
        st.warning("No starting pitcher data found for 2025.")

    st.divider()

    # 2026 Live Starters
    st.subheader("📈 2026 Live Starter Performance")
    if not df_26.empty:
        starters_26 = df_26[df_26['GS'] > 0]
        st.dataframe(starters_26[['Name', 'GS', 'ERA', 'WHIP', 'IP', 'Season']])
    else:
        st.info("2026 Regular Season stats will show starters here after Opening Day.")

except Exception as e:
    st.error(f"Error: {e}")