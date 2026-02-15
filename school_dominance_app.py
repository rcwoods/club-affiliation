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

st.title("McKinnon Basketball Association Club Affiliation Explorer")
st.markdown(
    """
Explore how players are distributed across schools and clubs.
You can search by school or by club.
"""
)

st.divider()

# --------------------------------------------------
# SEARCH MODE
# --------------------------------------------------

mode = st.radio(
    "Search by:",
    ["School", "Club"],
    horizontal=True
)

st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    selected_school = st.selectbox(
        "Search or Select Your School",
        sorted(df["School"].unique())
    )

    school_data = (
        df[df["School"] == selected_school]
        .sort_values("Affiliation %", ascending=False)
        .reset_index(drop=True)
    )

    primary_affiliation = school_data.iloc[0]

    st.markdown("### Most Common Club for This School")
    st.markdown(f"**{primary_affiliation['Club']}**")

    st.markdown(
        f"{int(primary_affiliation['Club Players'])} of "
        f"{int(primary_affiliation['Total Players'])} players "
        f"from this school currently play at this club "
        f"({primary_affiliation['Affiliation %']}%)."
    )

    st.divider()

    st.markdown("### Top 3 Clubs from This School")

    top_3 = school_data.head(3)

    for i, row in top_3.iterrows():
        st.markdown(
            f"**{i+1}. {row['Club']}**  \n"
            f"{int(row['Club Players'])} players "
            f"({row['Affiliation %']}%)"
        )

    st.divider()

    st.subheader("Full School Affiliation Breakdown")

    display_table = school_data[[
        "Club",
        "Club Players",
        "Affiliation %"
    ]].rename(columns={
        "Club Players": "Players at Club"
    })

    st.dataframe(display_table, use_container_width=True, hide_index=True)

    st.subheader("Affiliation Share by Club")
    st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    selected_club = st.selectbox(
        "Search or Select a Club",
        sorted(df["Club"].unique())
    )

    club_data = (
        df[df["Club"] == selected_club]
        .sort_values("Club Players", ascending=False)
        .reset_index(drop=True)
    )

    total_players_club = club_data["Club Players"].sum()
    total_schools = club_data.shape[0]

    st.markdown("### School Representation at This Club")
    st.markdown(f"**{selected_club}**")

    st.markdown(
        f"{int(total_players_club)} total players "
        f"from {total_schools} schools are registered at this club."
    )

    st.divider()

    st.markdown("### Top 3 Schools at This Club")

    top_3_schools = club_data.head(3)

    for i, row in top_3_schools.iterrows():
        st.markdown(
            f"**{i+1}. {row['School']}**  \n"
            f"{int(row['Club Players'])} players "
            f"({row['Affiliation %']}% of that school)"
        )

    st.divider()

    st.subheader("Full School Breakdown")

    display_table = club_data[[
        "School",
        "Club Players",
        "Affiliation %"
    ]].rename(columns={
        "Club Players": "Players from School"
    })

    st.dataframe(display_table, use_container_width=True, hide_index=True)

    st.subheader("Players by School")
    st.bar_chart(club_data.set_index("School")["Club Players"])

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Data reflects registered player distribution by school and club."
)
