import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation",
    layout="centered"
)

# --------------------------------------------------
# DATA LOADING
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
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "mode" not in st.session_state:
    st.session_state.mode = "School"

if "selected_school" not in st.session_state:
    st.session_state.selected_school = None

if "selected_club" not in st.session_state:
    st.session_state.selected_club = None

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("McKinnon Basketball Association")
st.subheader("Club Affiliation Explorer")
st.caption("Explore how players are distributed across schools and clubs.")

st.markdown("")

# --------------------------------------------------
# MODE SELECTOR
# --------------------------------------------------

mode = st.radio(
    "Search by",
    ["School", "Club"],
    index=0 if st.session_state.mode == "School" else 1,
    horizontal=True
)

st.session_state.mode = mode

st.markdown("")

# ==================================================
# SCHOOL MODE
# ==================================================

if st.session_state.mode == "School":

    school_list = sorted(df["School"].unique())
    selected_school = st.selectbox(
        "School",
        ["Select a School"] + school_list,
        index=0 if st.session_state.selected_school is None else school_list.index(st.session_state.selected_school) + 1
    )

    if selected_school != "Select a School":

        st.session_state.selected_school = selected_school

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        st.caption(f"{int(primary['Total Players'])} total players from this school")

        st.markdown("")

        # Most Common Club (Clickable)
        st.markdown("### Most Common Club")

        if st.button(primary["Club"], key="primary_club"):
            st.session_state.mode = "Club"
            st.session_state.selected_club = primary["Club"]
            st.rerun()

        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        st.markdown("")

        # Top 3 Clubs
        st.markdown("### Top 3 Clubs")

        top_3 = school_data.head(3)

        for i, row in top_3.iterrows():
            col1, col2 = st.columns([3, 1])

            if col1.button(row["Club"], key=f"club_{i}"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.rerun()

            col2.write(f"{row['Affiliation %']}%")

        st.markdown("")

        # Full Breakdown
        st.markdown("### Full Breakdown")

        for i, row in school_data.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])

            if col1.button(row["Club"], key=f"club_full_{i}"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.rerun()

            col2.write(int(row["Club Players"]))
            col3.write(f"{row['Affiliation %']}%")

# ==================================================
# CLUB MODE
# ==================================================

if st.session_state.mode == "Club":

    club_list = sorted(df["Club"].unique())
    selected_club = st.selectbox(
        "Club",
        ["Select a Club"] + club_list,
        index=0 if st.session_state.selected_club is None else club_list.index(st.session_state.selected_club) + 1
    )

    if selected_club != "Select a Club":

        st.session_state.selected_club = selected_club

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        st.markdown("")

        # Top 3 Schools
        st.markdown("### Top 3 Schools")

        for i, row in club_data.head(3).iterrows():
            col1, col2 = st.columns([3, 1])

            if col1.button(row["School"], key=f"school_{i}"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.rerun()

            col2.write(int(row["Club Players"]))

        st.markdown("")

        # Full Breakdown
        st.markdown("### Full Breakdown")

        for i, row in club_data.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])

            if col1.button(row["School"], key=f"school_full_{i}"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.rerun()

            col2.write(int(row["Club Players"]))
            col3.write(f"{row['Affiliation %']}%")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("")
st.caption("Data reflects registered player distribution by school and club.")
