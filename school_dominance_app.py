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
This tool shows where students from your school currently play basketball.  
It can help families understand which clubs have the strongest presence from their school community.
"""
)

st.divider()

# --------------------------------------------------
# SCHOOL SELECTION (Built-in searchable selectbox)
# --------------------------------------------------

selected_school = st.selectbox(
    "Search or Select Your School",
    sorted(df["School"].unique())
)

# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if selected_school:

    school_data = (
        df[df["School"] == selected_school]
        .sort_values("Affiliation %", ascending=False)
        .reset_index(drop=True)
    )

    primary_affiliation = school_data.iloc[0]

    # --------------------------------------------------
    # MOST COMMON CLUB SECTION
    # --------------------------------------------------

    st.markdown("### Most Common Club for This School")

    st.markdown(f"**{primary_affiliation['Club']}**")

    st.markdown(
        f"{int(primary_affiliation['Club Players'])} of "
        f"{int(primary_affiliation['Total Players'])} players "
        f"from this school currently play at this club "
        f"({primary_affiliation['Affiliation %']}%)."
    )

    # Interpretation guidance
    if primary_affiliation["Affiliation %"] >= 50:
        st.info("This club has a majority of players from this school.")
    elif primary_affiliation["Affiliation %"] >= 30:
        st.info("This club has the largest share of players from this school.")
    else:
        st.info("Players from this school are spread across multiple clubs.")

    st.divider()

    # --------------------------------------------------
    # TOP 3 CLUBS
    # --------------------------------------------------

    st.markdown("### Top 3 Clubs from This School")

    top_3 = school_data.head(3)

    for i, row in top_3.iterrows():
        st.markdown(
            f"**{i+1}. {row['Club']}**  \n"
            f"{int(row['Club Players'])} players "
            f"({row['Affiliation %']}%)"
        )

    st.divider()

    # --------------------------------------------------
    # FULL BREAKDOWN
    # --------------------------------------------------

    st.subheader("Full School Affiliation Breakdown")

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

    # --------------------------------------------------
    # BAR CHART
    # --------------------------------------------------

    st.subheader("Affiliation Share by Club")

    chart_data = school_data.set_index("Club")["Affiliation %"]
    st.bar_chart(chart_data)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "Data reflects registered player distribution by school and club."
)
