import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG (Better for Mobile)
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="centered"
)

# --------------------------------------------------
# GLOBAL STYLING (Mobile Optimised)
# --------------------------------------------------

st.markdown("""
<style>

/* Reduce excessive padding */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 5rem;
}

/* Larger tap targets */
button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 6px 0 !important;
    color: inherit !important;
    font-weight: 600 !important;
    text-align: left !important;
    font-size: 17px !important;
}

button[kind="secondary"]:hover {
    text-decoration: underline;
}

/* Section spacing */
.section-space {
    margin-top: 2rem;
}

/* Ranking style */
.rank-number {
    font-weight: 700;
    opacity: 0.5;
    font-size: 14px;
}

/* Sub text */
.sub-text {
    font-size: 14px;
    opacity: 0.75;
    margin-bottom: 18px;
}

/* Improve heading spacing */
h2 {
    margin-top: 1.8rem;
    margin-bottom: 0.6rem;
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
# SAFE NAVIGATION
# --------------------------------------------------

def go_to_school(name):
    st.session_state._nav_target = ("School", name)
    st.rerun()

def go_to_club(name):
    st.session_state._nav_target = ("Club", name)
    st.rerun()

if "_nav_target" in st.session_state:
    target_mode, target_value = st.session_state._nav_target
    st.session_state.mode = target_mode

    if target_mode == "School":
        st.session_state.selected_school = target_value
        st.session_state.selected_club = None
    else:
        st.session_state.selected_club = target_value
        st.session_state.selected_school = None

    del st.session_state._nav_target

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("School–Club Affiliation Explorer")
st.caption("Explore player distribution across McKinnon Basketball Association")

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True,
    key="mode"
)

st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    schools = sorted(df["School"].unique())

    selected_school = st.selectbox(
        "Select a School",
        options=["Choose an option"] + schools,
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

        # ---------------- MOST COMMON
        st.markdown("## Most Common Club")

        if st.button(primary["Club"], type="secondary"):
            go_to_club(primary["Club"])

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players from this school • {primary['Affiliation %']}% Share</div>",
            unsafe_allow_html=True
        )

        # ---------------- FULL BREAKDOWN
        st.markdown("## Full Breakdown")

        for i, row in school_data.iterrows():

            st.markdown(
                f"<div class='rank-number'>#{i+1}</div>",
                unsafe_allow_html=True
            )

            if st.button(row["Club"], key=f"club_{i}", type="secondary"):
                go_to_club(row["Club"])

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players from this school • {row['Affiliation %']}% Share</div>",
                unsafe_allow_html=True
            )

        # ---------------- CHART (Horizontal = Better for Mobile)
        st.markdown("## Distribution Chart")

        fig = px.bar(
            school_data,
            y="Club",
            x="Affiliation %",
            orientation="h",
            text="Affiliation %",
        )

        fig.update_layout(
            xaxis_title="% Share",
            yaxis_title="",
            showlegend=False,
            height=400 + (len(school_data) * 20)
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        options=["Choose an option"] + clubs,
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

        club_data["Share %"] = (
            club_data["Club Players"] / total_players * 100
        ).round(2)

        primary = club_data.iloc[0]

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        # ---------------- MOST COMMON
        st.markdown("## Most Common School")

        if st.button(primary["School"], type="secondary"):
            go_to_school(primary["School"])

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players from this club • {primary['Share %']}% Share</div>",
            unsafe_allow_html=True
        )

        # ---------------- FULL BREAKDOWN
        st.markdown("## Full Breakdown")

        for i, row in club_data.iterrows():

            st.markdown(
                f"<div class='rank-number'>#{i+1}</div>",
                unsafe_allow_html=True
            )

            if st.button(row["School"], key=f"school_{i}", type="secondary"):
                go_to_school(row["School"])

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players from this club • {row['Share %']}% Share</div>",
                unsafe_allow_html=True
            )

        # ---------------- CHART (Horizontal)
        st.markdown("## Distribution Chart")

        fig = px.bar(
            club_data,
            y="School",
            x="Share %",
            orientation="h",
            text="Share %",
        )

        fig.update_layout(
            xaxis_title="% Share",
            yaxis_title="",
            showlegend=False,
            height=400 + (len(club_data) * 20)
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
