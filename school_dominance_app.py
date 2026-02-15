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

st.caption(
    "Explore how players are distributed across schools and clubs."
)

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

    selected_school = st.selectbox(
        "Select a School",
        sorted(df["School"].unique())
    )

    school_data = (
        df[df["School"] == selected_school]
        .sort_values("Affiliation %", ascending=False)
        .reset_index(drop=True)
    )

    primary = school_data.iloc[0]

    # ---- Summary Section ----
    st.markdown("### Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Most Common Club", primary["Club"])
    col2.metric("Affiliation Share", f"{primary['Affiliation %']}%")
    col3.metric("Total Players", int(primary["Total Players"]))

    st.markdown("")

    # ---- Top 3 Section ----
    st.markdown("### Top 3 Clubs")

    top_3 = school_data.head(3)

    cols = st.columns(3)
    for i in range(len(top_3)):
        cols[i].metric(
            top_3.loc[i, "Club"],
            f"{int(top_3.loc[i, 'Club Players'])} players",
            f"{top_3.loc[i, 'Affiliation %']}%"
        )

    st.markdown("")

    # ---- Table ----
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

    # ---- Chart ----
    st.markdown("### Affiliation Share by Club")
    st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    selected_club = st.selectbox(
        "Select a Club",
        sorted(df["Club"].unique())
    )

    club_data = (
        df[df["Club"] == selected_club]
        .sort_values("Club Players", ascending=False)
        .reset_index(drop=True)
    )

    total_players = club_data["Club Players"].sum()
    total_schools = club_data.shape[0]

    # ---- Summary Section ----
    st.markdown("### Overview")

    col1, col2 = st.columns(2)

    col1.metric("Total Players", int(total_players))
    col2.metric("Schools Represented", total_schools)

    st.markdown("")

    # ---- Top 3 Schools ----
    st.markdown("### Top 3 Schools")

    top_3 = club_data.head(3)

    cols = st.columns(3)
    for i in range(len(top_3)):
        cols[i].metric(
            top_3.loc[i, "School"],
            f"{int(top_3.loc[i, 'Club Players'])} players"
        )

    st.markdown("")

    # ---- Table ----
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

    # ---- Chart ----
    st.markdown("### Players by School")
    st.bar_chart(club_data.set_index("School")["Club Players"])

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("")
st.caption("Data reflects registered player distribution by school and club.")
