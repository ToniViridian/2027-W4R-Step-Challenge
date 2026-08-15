from pathlib import Path
from datetime import date
import html
import base64

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="2027 W4R Step Challenge",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------------
# EASY-TO-CHANGE CHALLENGE SETTINGS
# -------------------------------------------------------------------
DATA_FILE = Path("steps.csv")

TEAMS = [
    "WA",
    "SA",
    "Vic & Tas",
    "NSW",
    "North Qld",
    "South Qld",
    "Interactive",
    "International - PNP & NPL",
]

# Starter values only — change these when the 2027 challenge targets are confirmed.
CHALLENGE_TARGET_STEPS = 50_000_000
KM_PER_STEP = 0.00073  # approx. 0.73 metres per step

# Branding placeholders. These are deliberately easy to replace with exact brand colours.
BRAND_PRIMARY = "#0C6E6D"
BRAND_DARK = "#123B43"
BRAND_LIGHT = "#EAF5F3"
BRAND_ACCENT = "#D7A64A"

# -------------------------------------------------------------------
# STYLING
# -------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, #F7FBFA 0%, #FFFFFF 38%);
        }}

        .block-container {{
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1250px;
        }}

        .hero {{
            background: linear-gradient(120deg, {BRAND_DARK} 0%, {BRAND_PRIMARY} 100%);
            border-radius: 24px;
            padding: 34px 38px;
            color: white;
            margin-bottom: 22px;
            box-shadow: 0 10px 30px rgba(18,59,67,0.15);
        }}

        .hero-kicker {{
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-size: 0.8rem;
            font-weight: 700;
            opacity: 0.82;
            margin-bottom: 8px;
        }}

        .hero h1 {{
            color: white;
            margin: 0 0 8px 0;
            font-size: clamp(2rem, 4vw, 3.8rem);
            line-height: 1.02;
        }}

        .hero p {{
            margin: 0;
            font-size: 1.08rem;
            opacity: 0.92;
            max-width: 760px;
        }}

        .section-title {{
            color: {BRAND_DARK};
            font-size: 1.55rem;
            font-weight: 750;
            margin: 0.4rem 0 0.8rem;
        }}

        .callout {{
            background: {BRAND_LIGHT};
            border-left: 5px solid {BRAND_PRIMARY};
            border-radius: 12px;
            padding: 16px 18px;
            margin: 8px 0 18px;
        }}

        .rank-card {{
            background: white;
            border: 1px solid #DDE8E6;
            border-radius: 18px;
            padding: 20px;
            min-height: 145px;
            box-shadow: 0 5px 18px rgba(18,59,67,0.07);
        }}

        .rank-medal {{
            font-size: 2rem;
            margin-bottom: 4px;
        }}

        .rank-team {{
            color: {BRAND_DARK};
            font-weight: 750;
            font-size: 1.18rem;
        }}

        .rank-steps {{
            color: {BRAND_PRIMARY};
            font-weight: 800;
            font-size: 1.45rem;
            margin-top: 6px;
        }}

        .small-muted {{
            color: #627277;
            font-size: 0.86rem;
        }}

        div[data-testid="stMetric"] {{
            background: white;
            border: 1px solid #DDE8E6;
            border-radius: 16px;
            padding: 14px 16px;
            box-shadow: 0 4px 16px rgba(18,59,67,0.06);
        }}

        div[data-testid="stMetricLabel"] {{
            color: #5A6C70;
        }}

        div[data-testid="stMetricValue"] {{
            color: {BRAND_DARK};
        }}

        .stButton > button[kind="primary"],
        .stFormSubmitButton > button {{
            border-radius: 12px;
            font-weight: 700;
        }}

        div[data-baseweb="tab-list"] {{
            gap: 6px;
        }}

        button[data-baseweb="tab"] {{
            border-radius: 10px;
            padding-left: 16px;
            padding-right: 16px;
        }}

        footer {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------------
# BRAND ASSET
# -------------------------------------------------------------------
LOGO_FILE = Path("viridian_foundation_logo.png")

def image_as_data_uri(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

logo_uri = image_as_data_uri(LOGO_FILE)

# -------------------------------------------------------------------
# DATA HELPERS
# -------------------------------------------------------------------
def load_data():
    columns = ["name", "team", "date", "steps"]
    if not DATA_FILE.exists():
        return pd.DataFrame(columns=columns)

    df = pd.read_csv(DATA_FILE)

    if df.empty:
        return pd.DataFrame(columns=columns)

    for col in columns:
        if col not in df.columns:
            df[col] = None

    df = df[columns]
    df["name"] = df["name"].fillna("").astype(str).str.strip()
    df["team"] = df["team"].fillna("").astype(str).str.strip()
    df["steps"] = pd.to_numeric(df["steps"], errors="coerce").fillna(0).astype(int)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    return df


def save_entry(name, team, entry_date, steps):
    existing = load_data()

    new_row = pd.DataFrame(
        [{
            "name": name.strip(),
            "team": team,
            "date": entry_date.isoformat(),
            "steps": int(steps),
        }]
    )

    combined = pd.concat([existing, new_row], ignore_index=True)
    combined["date"] = combined["date"].astype(str)
    combined.to_csv(DATA_FILE, index=False)


def format_number(value):
    return f"{int(value):,}"


def team_summary(df):
    if df.empty:
        return pd.DataFrame(columns=["team", "steps", "participants", "average_steps"])

    totals = (
        df.groupby("team")
        .agg(
            steps=("steps", "sum"),
            participants=("name", "nunique"),
        )
        .reset_index()
    )

    totals["average_steps"] = (
        totals["steps"] / totals["participants"].replace(0, pd.NA)
    ).fillna(0)

    return totals.sort_values("steps", ascending=False).reset_index(drop=True)


# -------------------------------------------------------------------
# APP DATA
# -------------------------------------------------------------------
df = load_data()

total_steps = int(df["steps"].sum()) if not df.empty else 0
total_km = total_steps * KM_PER_STEP
participants = int(df["name"].nunique()) if not df.empty else 0
active_teams = int(df["team"].nunique()) if not df.empty else 0
progress = min(total_steps / CHALLENGE_TARGET_STEPS, 1.0) if CHALLENGE_TARGET_STEPS else 0
team_totals = team_summary(df)

# -------------------------------------------------------------------
# HERO
# -------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        {f'<img class="hero-logo" src="{logo_uri}" alt="Viridian Foundation">' if logo_uri else ''}
        <div class="hero-kicker">2027 Step Challenge</div>
        <h1>Walk for Resilience</h1>
        <p>Every step makes a difference. Log your movement, support your team and see how far we can travel together.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# TOP METRICS
# -------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("👟 Total Steps", format_number(total_steps))
m2.metric("🌏 Distance Travelled", f"{total_km:,.0f} km")
m3.metric("🙋 Participants", participants)
m4.metric("🤝 Active Teams", active_teams)

st.write("")
st.markdown('<div class="section-title">Challenge progress</div>', unsafe_allow_html=True)
st.progress(progress)

remaining = max(CHALLENGE_TARGET_STEPS - total_steps, 0)
if total_steps < CHALLENGE_TARGET_STEPS:
    st.caption(
        f"{format_number(total_steps)} of {format_number(CHALLENGE_TARGET_STEPS)} steps "
        f"• {format_number(remaining)} steps to the starter target"
    )
else:
    st.caption(
        f"🎉 Target reached — {format_number(total_steps)} total steps and counting."
    )

# -------------------------------------------------------------------
# LEADERSHIP SNAPSHOT
# -------------------------------------------------------------------
st.markdown('<div class="section-title">🏆 Team podium</div>', unsafe_allow_html=True)

if team_totals.empty:
    st.markdown(
        '<div class="callout"><b>The podium is waiting.</b><br>Add the first step entry to start the 2027 leaderboard.</div>',
        unsafe_allow_html=True,
    )
else:
    podium_cols = st.columns(3)
    medals = ["🥇", "🥈", "🥉"]

    for idx, col in enumerate(podium_cols):
        if idx < len(team_totals):
            row = team_totals.iloc[idx]
            team = html.escape(str(row["team"]))
            steps = format_number(row["steps"])
            km = row["steps"] * KM_PER_STEP

            with col:
                st.markdown(
                    f"""
                    <div class="rank-card">
                        <div class="rank-medal">{medals[idx]}</div>
                        <div class="rank-team">{team}</div>
                        <div class="rank-steps">{steps} steps</div>
                        <div class="small-muted">{km:,.0f} km travelled</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

st.write("")

# -------------------------------------------------------------------
# MAIN TABS
# -------------------------------------------------------------------
home_tab, entry_tab, team_tab, individual_tab, activity_tab = st.tabs(
    [
        "🏠 Dashboard",
        "➕ Enter Steps",
        "🏆 Teams",
        "🥇 Individuals",
        "📅 Activity",
    ]
)

with home_tab:
    st.markdown('<div class="section-title">Challenge snapshot</div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85])

    with left:
        st.subheader("Total steps by team")

        if team_totals.empty:
            st.info("The team chart will appear after steps are entered.")
        else:
            chart_df = team_totals.set_index("team")[["steps"]]
            st.bar_chart(chart_df)

    with right:
        st.subheader("Fair-play view")

        if team_totals.empty:
            st.info("Average steps per participant will appear here.")
        else:
            fair = team_totals.sort_values("average_steps", ascending=False).copy()
            fair["Average steps"] = fair["average_steps"].round(0).astype(int)
            fair = fair[["team", "participants", "Average steps"]]
            fair.columns = ["Team", "Participants", "Average steps / person"]

            st.dataframe(
                fair,
                hide_index=True,
                use_container_width=True,
            )

            st.caption(
                "This view helps smaller teams compete fairly by comparing average steps per participant."
            )

    st.markdown(
        """
        <div class="callout">
            <b>Next build:</b> We can add the Viridian Foundation and charity logos,
            a challenge countdown, fundraising information, and a visual journey showing
            how far the combined kilometres have travelled.
        </div>
        """,
        unsafe_allow_html=True,
    )

with entry_tab:
    st.subheader("Log your steps")
    st.caption("Enter one daily total at a time.")

    with st.form("step_entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Your name",
                placeholder="e.g. Toni Brownlee",
            )
            team = st.selectbox(
                "Team / Region",
                TEAMS,
            )

        with col2:
            entry_date = st.date_input(
                "Date",
                value=date.today(),
            )
            steps = st.number_input(
                "Steps",
                min_value=0,
                max_value=200_000,
                step=100,
                value=10_000,
            )

        submitted = st.form_submit_button(
            "👟 Submit my steps",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not name.strip():
                st.error("Please enter your name.")
            elif steps <= 0:
                st.error("Please enter a step total greater than zero.")
            else:
                save_entry(name, team, entry_date, steps)
                st.success(
                    f"Added {steps:,} steps for {name.strip()} — {team}."
                )
                st.rerun()

    st.info(
        "Testing version: entries are currently stored in a local CSV. "
        "For the live challenge we'll switch this to shared database storage."
    )

with team_tab:
    st.subheader("Team leaderboard")

    if team_totals.empty:
        st.info("No team results yet.")
    else:
        board = team_totals.copy()
        board["Rank"] = range(1, len(board) + 1)
        board["Steps"] = board["steps"].map(format_number)
        board["Kilometres"] = (board["steps"] * KM_PER_STEP).round(0).astype(int)
        board["Average steps / person"] = board["average_steps"].round(0).astype(int)

        board = board[
            [
                "Rank",
                "team",
                "participants",
                "Steps",
                "Kilometres",
                "Average steps / person",
            ]
        ]
        board.columns = [
            "Rank",
            "Team",
            "Participants",
            "Total Steps",
            "Kilometres",
            "Average Steps / Person",
        ]

        st.dataframe(
            board,
            hide_index=True,
            use_container_width=True,
        )

with individual_tab:
    st.subheader("Individual leaderboard")

    if df.empty:
        st.info("No individual results yet.")
    else:
        person_board = (
            df.groupby(["name", "team"], as_index=False)["steps"]
            .sum()
            .sort_values("steps", ascending=False)
            .reset_index(drop=True)
        )
        person_board["Rank"] = range(1, len(person_board) + 1)
        person_board["Kilometres"] = (person_board["steps"] * KM_PER_STEP).round(1)
        person_board["Total Steps"] = person_board["steps"].map(format_number)

        person_board = person_board[
            ["Rank", "name", "team", "Total Steps", "Kilometres"]
        ]
        person_board.columns = [
            "Rank",
            "Participant",
            "Team",
            "Total Steps",
            "Kilometres",
        ]

        st.dataframe(
            person_board,
            hide_index=True,
            use_container_width=True,
        )

with activity_tab:
    st.subheader("Recent activity")

    if df.empty:
        st.info("No activity yet.")
    else:
        recent = df.copy()
        recent = recent.sort_values("date", ascending=False).head(50)
        recent["steps"] = recent["steps"].map(format_number)
        recent.columns = ["Participant", "Team", "Date", "Steps"]

        st.dataframe(
            recent,
            hide_index=True,
            use_container_width=True,
        )

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download challenge data (CSV)",
            data=csv_bytes,
            file_name="w4r_step_challenge_data.csv",
            mime="text/csv",
        )

st.divider()
st.caption(
    "2027 Walk for Resilience • Viridian Foundation • Prototype dashboard"
)
