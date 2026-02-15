import streamlit as st
import pandas as pd
import urllib.parse

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

st.divider()

# --------------------------------------------------
# URL PARAMS
# --------------------------------------------------

params = st.query_params
selected_school = params.get("school")
selected_club = params.get("club")

# --------------------------------------------------
# MODE SELECTOR
# --------------------------------------------------

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True,
    index=0 if selected_school or not selected_club else 1
)

st.markdown("")

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    school_list = sorted(df["School"].unique())

    selected_school_dropdown = st.selectbox(
        "Select a School",
        ["Select a School"] + school_list,
        index=(
            school_list.index(selected_school) + 1
            if selected_school in school_list
            else 0
        )
    )

    if selected_school_dropdown != "Select a School":

        # Update URL if dropdown used
        if selected_school_dropdown != selected_school:
            st.query_params.clear()
            st.query_params["school"] = selected_school_dropdown
            st.rerun()

        school_data = (
            df[df["School"] == selected_school_dropdown]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        # School Context
        st.markdown(f"### {selected_school_dropdown}")
        st.caption(f"{int(primary['Total Players'])} total players from this school")

        st.markdown("")

        # Most Common Club
        st.markdown("#### Most Common Club")
        club_link = urllib.parse.quote(primary["Club"])
        st.markdown(f"[**{primary['Club']}**](?club={club_link})")
        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        st.markdown("")

        # Top 3 Clubs
        st.markdown("#### Top 3 Clubs")

        for _, row in school_data.head(3).iterrows():
            club_encoded = urllib.parse.quote(row["Club"])
            st.markdown(
                f"[{row['Club']}](?club={club_encoded}) — "
                f"{int(row['Club Players'])} players — "
                f"{row['Affiliation %']}%"
            )

        st.markdown("")

        st.markdown("#### Affiliation Share by Club")
        st.bar_chart(school_data.set_index("Club")["Affiliation %"])


# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    club_list = sorted(df["Club"].unique())

    selected_club_dropdown = st.selectbox(
        "Select a Club",
        ["Select a Club"] + club_list,
        index=(
            club_list.index(selected_club) + 1
            if selected_club in club_list
            else 0
        )
    )

    if selected_club_dropdown != "Select a Club":

        # Update URL if dropdown used
        if selected_club_dropdown != selected_club:
            st.query_params.clear()
            st.query_params["club"] = selected_club_dropdown
            st.rerun()

        club_data = (
            df[df["Club"] == selected_club_dropdown]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()

        st.markdown(f"### {selected_club_dropdown}")
        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        st.markdown("")

        # Top 3 Schools
        st.markdown("#### Top 3 Schools")

        for _, row in club_data.head(3).iterrows():
            school_encoded = urllib.parse.quote(row["School"])
            st.markdown(
                f"[{row['School']}](?school={school_encoded}) — "
                f"{int(row['Club Players'])} players — "
                f"{row['Affiliation %']}%"
            )

        st.markdown("")

        st.markdown("#### Players by School")
        st.bar_chart(club_data.set_index("School")["Club Players"])

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
