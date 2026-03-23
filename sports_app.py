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
    # qual=10 ensures we get the full rotation
    df_25 = pitching_stats(2025, qual=10)
    try:
        df_26 = pitching_stats(2026, qual=1)
        if df_26 is not None and len(df_26.columns) > 1:
            return pd.concat([df_25, df_26], ignore_index=True)
    except Exception:
        pass
    return df_25

@st.cache_data
def get_detailed_inning_stats(name, year=2025):
    """Pulls hits, runs, and strikeouts per inning for STARTS only"""
    try:
        names = name.split(' ')
        first, last = names[0], names[-1]
        ids = playerid_lookup(last, first)
        if ids.empty: return None
        mlb_id = ids.iloc[0]['key_mlbam']
        
        # Pull Statcast data
        data = statcast_pitcher(f'{year}-03-01', f'{year}-11-15', mlb_id)
        
        # 1. ONLY Regular Season ('R')
        data = data[data['game_type'] == 'R']
        
        # 2. STARTER ONLY FILTER: Only include games where they pitched in the 1st inning
        starter_game_ids = data[data['inning'] == 1]['game_pk'].unique()
        data = data[data['game_pk'].isin(starter_game_ids)]
        
        # 3. Identify Hits (Official only)
        hit_events = ['single', 'double', 'triple', 'home_run']
        hit_data = data[(data['type'] == 'X') & (data['events'].isin(hit_events))]
        hits_per_inning = hit_data.groupby('inning').size()
        
        # 4. Identify Runs Allowed
        # We track when the score increases on a specific pitch/play
        # Using a copy to avoid SettingWithCopy warnings
        scoring_plays = data[data['post_bat_score'] > data['bat_score']].copy()
        scoring_plays = scoring_plays.drop_duplicates(subset=['game_pk', 'at_bat_number'])
        scoring_plays['runs_on_play'] = scoring_plays['post_bat_score'] - scoring_plays['bat_score']
        runs_per_inning = scoring_plays.groupby('inning')['runs_on_play'].sum()
        
        # 5. Identify Strikeouts
        so_per_inning = data[data['events'] == 'strikeout'].groupby('inning').size()
        
        # Combine into DataFrame
        df_stats = pd.DataFrame({
            'Hits': hits_per_inning,
            'Runs': runs_per_inning,
            'K': so_per_inning
        }).reindex(range(1, 6), fill_value=0)
        
        return df_stats
    except Exception:
        return None

try:
    df = load_all_stats()
    df['Full Team'] = df['Team'].map(TEAM_MAP)
    
    selected_team = st.sidebar.selectbox("Select Team", options=sorted(TEAM_MAP.values()))
    
    # Filter for Starters with at least 5 starts in 2025 for a solid baseline
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
        st.subheader("📊 F5 Inning-by-Inning Deep Dive (2025 Baseline)")
        st.write("Metric breakdown for innings 1-5 (Regular Season Starts Only)")
        
        hit_cols = st.columns(3)
        for i, (_, row) in enumerate(top_3_25.iterrows()):
            with hit_cols[i]:
                st.write(f"#### {row['Name']}")
                detailed_stats = get_detailed_inning_stats(row['Name'])
                
                if detailed_stats is not None:
                    # Display metrics table
                    st.table(detailed_stats.T)
                    
                    # Display visualization
                    st.bar_chart(detailed_stats)
                else:
                    st.info(f"Gathering Statcast data for {row['Name']}...")

    else:
        st.warning("No starting pitcher data found for 2025.")

    st.divider()

    # 2026 Live Starters
    st.subheader("📈 2026 Live Starter Performance")
    if not df_26.empty:
        starters_26 = df_26[df_26['GS'] > 0]
        st.dataframe(starters_26[['Name', 'GS', 'ERA', 'WHIP', 'IP', 'Season']])
    else:
        st.info("2026 Regular Season stats will appear here as games are played (Starting March 25-26).")

except Exception as e:
    st.error(f"Error: {e}")