import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL STYLING
# --------------------------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 5rem;
}

/* Clean clickable buttons */
button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 0 !important;
    color: inherit !important;
    font-weight: 600 !important;
    text-align: left !important;
}
button[kind="secondary"]:hover {
    text-decoration: underline;
}

.section-title {
    font-size: 26px;
    font-weight: 700;
    margin-top: 35px;
    margin-bottom: 10px;
}

.sub-text {
    font-size: 15px;
    opacity: 0.75;
    margin-bottom: 14px;
}

footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("Schools per Club.csv")
    df = df.dropna(subset=["School Details"])

    df = df.rename(columns={
        "School Details": "School",
        "Count": "Total Players",
        "Count.1": "Club Players"
    })

    df["Affiliation %"] = (
        df["Club Players"] / df["Total Players"] * 100
    ).round(2)

    return df

df = load_data()

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "mode" not in st.session_state:
    st.session_state.mode = "School"

if "selected_school" not in st.session_state:
    st.session_state.selected_school = None

if "selected_club" not in st.session_state:
    st.session_state.selected_club = None

# --------------------------------------------------
# SAFE NAVIGATION FUNCTION
# --------------------------------------------------

def go_to_school(school):
    st.session_state.mode = "School"
    st.session_state.selected_school = school
    st.session_state.selected_club = None
    st.rerun()

def go_to_club(club):
    st.session_state.mode = "Club"
    st.session_state.selected_club = club
    st.session_state.selected_school = None
    st.rerun()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("Club Affiliation Explorer")
st.caption("McKinnon Basketball Association")

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True,
    index=0 if st.session_state.mode == "School" else 1
)

st.session_state.mode = mode
st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    schools = sorted(df["School"].unique())

    selected_school = st.selectbox(
        "Select a School",
        ["Choose an option"] + schools,
        index=(
            schools.index(st.session_state.selected_school) + 1
            if st.session_state.selected_school in schools
            else 0
        )
    )

    if selected_school != "Choose an option":

        st.session_state.selected_school = selected_school

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        if school_data.empty:
            st.warning("No data available.")
            st.stop()

        total_players = int(school_data["Total Players"].iloc[0])
        primary = school_data.iloc[0]

        st.caption(f"{total_players} total players from this school")

        # Most Common Club
        st.markdown('<div class="section-title">Most Common Club</div>', unsafe_allow_html=True)

        if st.button(primary["Club"], key="primary_club", type="secondary"):
            go_to_club(primary["Club"])

        st.markdown(
            f'<div class="sub-text">{int(primary["Club Players"])} players • {primary["Affiliation %"]}%</div>',
            unsafe_allow_html=True
        )

        # Top 3
        st.markdown('<div class="section-title">Top 3 Clubs</div>', unsafe_allow_html=True)

        for i in range(min(3, len(school_data))):
            row = school_data.iloc[i]

            if st.button(row["Club"], key=f"top_club_{i}", type="secondary"):
                go_to_club(row["Club"])

            st.markdown(
                f'<div class="sub-text">{int(row["Club Players"])} players • {row["Affiliation %"]}%</div>',
                unsafe_allow_html=True
            )

        # Full Breakdown
        st.markdown('<div class="section-title">Full Breakdown</div>', unsafe_allow_html=True)

        for i, row in school_data.iterrows():

            if st.button(row["Club"], key=f"club_full_{i}", type="secondary"):
                go_to_club(row["Club"])

            st.markdown(
                f'<div class="sub-text">{int(row["Club Players"])} players • {row["Affiliation %"]}%</div>',
                unsafe_allow_html=True
            )

        # Chart
        st.markdown('<div class="section-title">Distribution Chart</div>', unsafe_allow_html=True)

        fig = px.bar(
            school_data.head(10),
            x="Club",
            y="Affiliation %",
            text="Affiliation %",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        ["Choose an option"] + clubs,
        index=(
            clubs.index(st.session_state.selected_club) + 1
            if st.session_state.selected_club in clubs
            else 0
        )
    )

    if selected_club != "Choose an option":

        st.session_state.selected_club = selected_club

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        if club_data.empty:
            st.warning("No data available.")
            st.stop()

        total_players = club_data["Club Players"].sum()

        breakdown = club_data.copy()
        breakdown["Share %"] = (
            breakdown["Club Players"] / total_players * 100
        ).round(2)

        st.caption(f"{total_players} total players across {breakdown.shape[0]} schools")

        primary = breakdown.iloc[0]

        # Most Common School
        st.markdown('<div class="section-title">Most Common School</div>', unsafe_allow_html=True)

        if st.button(primary["School"], key="primary_school", type="secondary"):
            go_to_school(primary["School"])

        st.markdown(
            f'<div class="sub-text">{int(primary["Club Players"])} players • {primary["Share %"]}%</div>',
            unsafe_allow_html=True
        )

        # Top 3
        st.markdown('<div class="section-title">Top 3 Schools</div>', unsafe_allow_html=True)

        for i in range(min(3, len(breakdown))):
            row = breakdown.iloc[i]

            if st.button(row["School"], key=f"top_school_{i}", type="secondary"):
                go_to_school(row["School"])

            st.markdown(
                f'<div class="sub-text">{int(row["Club Players"])} players • {row["Share %"]}%</div>',
                unsafe_allow_html=True
            )

        # Full Breakdown
        st.markdown('<div class="section-title">Full Breakdown</div>', unsafe_allow_html=True)

        for i, row in breakdown.iterrows():

            if st.button(row["School"], key=f"school_full_{i}", type="secondary"):
                go_to_school(row["School"])

            st.markdown(
                f'<div class="sub-text">{int(row["Club Players"])} players • {row["Share %"]}%</div>',
                unsafe_allow_html=True
            )

        # Chart
        st.markdown('<div class="section-title">Distribution Chart</div>', unsafe_allow_html=True)

        fig = px.bar(
            breakdown.head(10),
            x="School",
            y="Share %",
            text="Share %",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
