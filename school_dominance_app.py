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
# HEADER
# --------------------------------------------------

st.title("McKinnon Basketball Association")
st.subheader("Club Affiliation Explorer")
st.caption("Explore how players are distributed across schools and clubs.")

st.markdown("")

# --------------------------------------------------
# SEARCH MODE
# --------------------------------------------------

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True
)

st.markdown("")

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    school_options = ["Select a School"] + sorted(df["School"].unique())

    selected_school = st.selectbox(
        "School",
        school_options,
        index=0
    )

    if selected_school != "Select a School":

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        # Subtle context line
        st.caption(f"{int(primary['Total Players'])} total players from this school")

        st.markdown("")

        # --------------------------------------------------
        # MOST COMMON CLUB
        # --------------------------------------------------

        st.markdown("### Most Common Club")
        st.markdown(f"#### {primary['Club']}")
        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        st.markdown("")

        # --------------------------------------------------
        # TOP 3 CLUBS
        # --------------------------------------------------

        st.markdown("### Top 3 Clubs")

        top_3 = school_data.head(3)
        cols = st.columns(3)

        for i in range(len(top_3)):
            with cols[i]:
                st.markdown(f"**{top_3.loc[i, 'Club']}**")
                st.markdown(f"{int(top_3.loc[i, 'Club Players'])} players")
                st.markdown(f"{top_3.loc[i, 'Affiliation %']}%")

        st.markdown("")

        # --------------------------------------------------
        # FULL BREAKDOWN
        # --------------------------------------------------

        st.markdown("### Full Breakdown")

        display_table = school_data[[
            "Club",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players at Club"
        })

        st.dataframe(display_table, use_container_width=True, hide_index=True)

        st.markdown("")

        # --------------------------------------------------
        # CHART
        # --------------------------------------------------

        st.markdown("### Affiliation Share by Club")
        st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    club_options = ["Select a Club"] + sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Club",
        club_options,
        index=0
    )

    if selected_club != "Select a Club":

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()
        total_schools = club_data.shape[0]

        # --------------------------------------------------
        # CLUB HEADER
        # --------------------------------------------------

        st.markdown(f"## {selected_club}")
        st.caption(f"{total_players} total players across {total_schools} schools")

        st.markdown("")

        # --------------------------------------------------
        # TOP 3 SCHOOLS
        # --------------------------------------------------

        st.markdown("### Top 3 Schools")

        top_3 = club_data.head(3)
        cols = st.columns(3)

        for i in range(len(top_3)):
            with cols[i]:
                st.markdown(f"**{top_3.loc[i, 'School']}**")
                st.markdown(f"{int(top_3.loc[i, 'Club Players'])} players")
                st.markdown(f"{top_3.loc[i, 'Affiliation %']}%")

        st.markdown("")

        # --------------------------------------------------
        # FULL BREAKDOWN
        # --------------------------------------------------

        st.markdown("### Full Breakdown")

        display_table = club_data[[
            "School",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players from School"
        })

        st.dataframe(display_table, use_container_width=True, hide_index=True)

        st.markdown("")

        # --------------------------------------------------
        # CHART
        # --------------------------------------------------

        st.markdown("### Players by School")
        st.bar_chart(club_data.set_index("School")["Club Players"])

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("")
st.caption("Data reflects registered player distribution by school and club.")
