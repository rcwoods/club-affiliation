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
# SESSION STATE
# --------------------------------------------------

if "mode" not in st.session_state:
    st.session_state.mode = "School"

if "selected_school" not in st.session_state:
    st.session_state.selected_school = None

if "selected_club" not in st.session_state:
    st.session_state.selected_club = None

# --------------------------------------------------
# HEADER (Compact)
# --------------------------------------------------

st.title("Club Affiliation Explorer")
st.caption("McKinnon Basketball Association")

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True
)

st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    school_list = sorted(df["School"].unique())

    selected_school = st.selectbox(
        "Select a School",
        ["Select a School"] + school_list
    )

    if selected_school != "Select a School":

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        # Context
        st.caption(f"{int(primary['Total Players'])} total players from this school")

        # Most Common Club
        st.markdown("### Most Common Club")
        st.markdown(f"**{primary['Club']}**")
        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        # Top 3 (Vertical for mobile)
        st.markdown("### Top 3 Clubs")

        for _, row in school_data.head(3).iterrows():
            st.markdown(
                f"**{row['Club']}**  \n"
                f"{int(row['Club Players'])} players  \n"
                f"{row['Affiliation %']}%"
            )
            st.markdown("---")

        # Table
        st.markdown("### Full Breakdown (Tap a row)")

        display_table = school_data[[
            "Club",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players"
        })

        selection = st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            height=300
        )

        if selection.selection.rows:
            selected_row = selection.selection.rows[0]
            selected_club = display_table.iloc[selected_row]["Club"]
            st.session_state.mode = "Club"
            st.session_state.selected_club = selected_club
            st.rerun()

        st.markdown("### Affiliation Share")
        st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    club_list = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        ["Select a Club"] + club_list
    )

    if selected_club != "Select a Club":

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        st.markdown("### Top 3 Schools")

        for _, row in club_data.head(3).iterrows():
            st.markdown(
                f"**{row['School']}**  \n"
                f"{int(row['Club Players'])} players  \n"
                f"{row['Affiliation %']}%"
            )
            st.markdown("---")

        st.markdown("### Full Breakdown (Tap a row)")

        display_table = club_data[[
            "School",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players"
        })

        selection = st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            height=300
        )

        if selection.selection.rows:
            selected_row = selection.selection.rows[0]
            selected_school = display_table.iloc[selected_row]["School"]
            st.session_state.mode = "School"
            st.session_state.selected_school = selected_school
            st.rerun()

        st.markdown("### Players by School")
        st.bar_chart(club_data.set_index("School")["Club Players"])

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
