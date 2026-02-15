import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL STYLING (Clean Minimal Layout)
# --------------------------------------------------

st.markdown("""
<style>

/* Page width + padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 5rem;
    max-width: 900px;
}

/* Clean clickable names */
button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 0 !important;
    color: inherit !important;
    font-weight: 600 !important;
    font-size: 16px;
    text-align: left !important;
}
button[kind="secondary"]:hover {
    text-decoration: underline;
}

/* Section headings */
.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-top: 28px;
    margin-bottom: 14px;
}

/* Sub text */
.sub-text {
    font-size: 14px;
    opacity: 0.7;
    margin-top: 4px;
    margin-bottom: 16px;
}

/* Breakdown row */
.breakdown-row {
    padding: 14px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* Remove bottom border on last row */
.breakdown-row:last-child {
    border-bottom: none;
}

/* Clean footer */
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
# HEADER
# --------------------------------------------------

st.title("Club Affiliation Explorer")
st.caption("McKinnon Basketball Association")

mode = st.radio("Search by", ["School", "Club"], horizontal=True)
st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    selected_school = st.selectbox(
        "Select a School",
        ["Select a School"] + sorted(df["School"].unique())
    )

    if selected_school != "Select a School":

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        total_players = int(school_data["Total Players"].iloc[0])
        primary = school_data.iloc[0]

        st.caption(f"{total_players} total players from this school")

        # MOST COMMON
        st.markdown("<div class='section-title'>Most Common Club</div>", unsafe_allow_html=True)

        if st.button(primary["Club"], key="primary_club", type="secondary"):
            pass

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Affiliation %']}%</div>",
            unsafe_allow_html=True
        )

        # TOP 3
        st.markdown("<div class='section-title'>Top 3 Clubs</div>", unsafe_allow_html=True)

        for i in range(min(3, len(school_data))):
            row = school_data.iloc[i]

            if st.button(row["Club"], key=f"top_club_{i}", type="secondary"):
                pass

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
                unsafe_allow_html=True
            )

        # FULL BREAKDOWN
        st.markdown("<div class='section-title'>Full Breakdown</div>", unsafe_allow_html=True)

        for i, row in school_data.iterrows():

            if st.button(row["Club"], key=f"club_full_{i}", type="secondary"):
                pass

            st.markdown(
                f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
                unsafe_allow_html=True
            )

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    selected_club = st.selectbox(
        "Select a Club",
        ["Select a Club"] + sorted(df["Club"].unique())
    )

    if selected_club != "Select a Club":

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()

        breakdown = club_data.copy()
        breakdown["Share %"] = (
            breakdown["Club Players"] / total_players * 100
        ).round(2)

        st.caption(f"{total_players} total players across {breakdown.shape[0]} schools")

        # MOST COMMON
        primary = breakdown.iloc[0]

        st.markdown("<div class='section-title'>Most Common School</div>", unsafe_allow_html=True)

        if st.button(primary["School"], key="primary_school", type="secondary"):
            pass

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Share %']}%</div>",
            unsafe_allow_html=True
        )

        # TOP 3
        st.markdown("<div class='section-title'>Top 3 Schools</div>", unsafe_allow_html=True)

        for i in range(min(3, len(breakdown))):
            row = breakdown.iloc[i]

            if st.button(row["School"], key=f"top_school_{i}", type="secondary"):
                pass

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
                unsafe_allow_html=True
            )

        # FULL BREAKDOWN
        st.markdown("<div class='section-title'>Full Breakdown</div>", unsafe_allow_html=True)

        for i, row in breakdown.iterrows():

            if st.button(row["School"], key=f"school_full_{i}", type="secondary"):
                pass

            st.markdown(
                f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
                unsafe_allow_html=True
            )

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
