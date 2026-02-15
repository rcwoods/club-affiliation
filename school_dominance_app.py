import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation",
    page_icon="🏀",
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

st.title("🏀 Club Affiliation Explorer")
st.markdown(
    "Explore how players from each school are distributed across basketball clubs."
)

st.divider()

# --------------------------------------------------
# SCHOOL SELECTION
# --------------------------------------------------

school_list = sorted(df["School"].unique())
selected_school = st.selectbox(
    "Select a School",
    school_list
)

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if selected_school:

    school_data = (
        df[df["School"] == selected_school]
        .sort_values("Affiliation %", ascending=False)
    )

    primary_affiliation = school_data.iloc[0]

    # ---- Primary Club Section ----
    st.markdown("### Primary Club Affiliation")
    st.markdown(f"**{primary_affiliation['Club']}**")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Players at This Club",
        int(primary_affiliation["Club Players"])
    )

    col2.metric(
        "Affiliation Share",
        f"{primary_affiliation['Affiliation %']}%"
    )

    col3.metric(
        "Total Players From This School",
        int(primary_affiliation["Total Players"])
    )

    st.divider()

    # ---- Breakdown Table ----
    st.subheader("School Affiliation Breakdown")

    display_table = school_data[[
        "Club",
        "Club Players",
        "Affiliation %"
    ]].rename(columns={
        "Club Players": "Players at Club"
    })

    st.dataframe(
        display_table,
        use_container_width=True,
        hide_index=True
    )

    # ---- Bar Chart ----
    st.subheader("Affiliation Share by Club")

    chart_data = school_data.set_index("Club")["Affiliation %"]
    st.bar_chart(chart_data)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption("Affiliation insights based on registered player distribution.")
