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
# HEADER
# --------------------------------------------------

st.title("McKinnon Basketball Association")
st.subheader("Club Affiliation Explorer")
st.caption("Explore how players are distributed across schools and clubs.")

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

st.divider()

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

        # School Context
        st.markdown(f"### {selected_school}")
        st.caption(f"{int(primary['Total Players'])} total players from this school")

        st.markdown("")

        # Most Common Club
        st.markdown("#### Most Common Club")
        st.markdown(f"**{primary['Club']}**")
        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        st.markdown("")

        # Top 3 Summary (clean columns)
        st.markdown("#### Top 3 Clubs")

        top_3 = school_data.head(3)
        cols = st.columns(3)

        for i in range(len(top_3)):
            with cols[i]:
                st.markdown(f"**{top_3.loc[i, 'Club']}**")
                st.markdown(f"{int(top_3.loc[i, 'Club Players'])} players")
                st.markdown(f"{top_3.loc[i, 'Affiliation %']}%")

        st.markdown("")

        # Clickable Breakdown Table
        st.markdown("#### Full Breakdown (Click a club to explore)")

        display_table = school_data[[
            "Club",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players at Club"
        })

        selection = st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun"
        )

        if selection.selection.rows:
            selected_row = selection.selection.rows[0]
            selected_club = display_table.iloc[selected_row]["Club"]

            st.session_state.mode = "Club"
            st.session_state.selected_club = selected_club
            st.rerun()

        st.markdown("")

        st.markdown("#### Affiliation Share by Club")
        st.bar_chart(school_data.set_index("Club")["Affiliation %"])


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

        st.markdown(f"### {selected_club}")
        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        st.markdown("")

        # Top 3 Schools
        st.markdown("#### Top 3 Schools")

        top_3 = club_data.head(3)
        cols = st.columns(3)

        for i in range(len(top_3)):
            with cols[i]:
                st.markdown(f"**{top_3.loc[i, 'School']}**")
                st.markdown(f"{int(top_3.loc[i, 'Club Players'])} players")
                st.markdown(f"{top_3.loc[i, 'Affiliation %']}%")

        st.markdown("")

        # Clickable Breakdown Table
        st.markdown("#### Full Breakdown (Click a school to explore)")

        display_table = club_data[[
            "School",
            "Club Players",
            "Affiliation %"
        ]].rename(columns={
            "Club Players": "Players from School"
        })

        selection = st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun"
        )

        if selection.selection.rows:
            selected_row = selection.selection.rows[0]
            selected_school = display_table.iloc[selected_row]["School"]

            st.session_state.mode = "School"
            st.session_state.selected_school = selected_school
            st.rerun()

        st.markdown("")

        st.markdown("#### Players by School")
        st.bar_chart(club_data.set_index("School")["Club Players"])


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
