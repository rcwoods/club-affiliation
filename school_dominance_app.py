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
# STYLING
# --------------------------------------------------

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 5rem;
}

button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 0 !important;
    color: inherit !important;
    font-weight: 600 !important;
    text-align: left !important;
}
button[kind="secondary"]:hover {
    text-decoration: underline;
}

h3 {
    margin-top: 2rem !important;
    margin-bottom: 0.8rem !important;
    font-size: 1.4rem !important;
}

.sub-text {
    font-size: 0.9rem;
    opacity: 0.75;
    margin-bottom: 1.2rem;
}

.breakdown-row {
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

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
# SESSION STATE INIT
# --------------------------------------------------

if "mode_state" not in st.session_state:
    st.session_state["mode_state"] = "School"

if "selected_school" not in st.session_state:
    st.session_state["selected_school"] = None

if "selected_club" not in st.session_state:
    st.session_state["selected_club"] = None

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("Club Affiliation Explorer")
st.caption("McKinnon Basketball Association")

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True,
    index=0 if st.session_state["mode_state"] == "School" else 1
)

st.session_state["mode_state"] = mode

st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if st.session_state["mode_state"] == "School":

    schools = sorted(df["School"].unique())

    selected_school = st.selectbox(
        "Select a School",
        schools,
        index=schools.index(st.session_state["selected_school"])
        if st.session_state["selected_school"] in schools else 0,
        placeholder="Start typing your school..."
    )

    st.session_state["selected_school"] = selected_school

    school_data = (
        df[df["School"] == selected_school]
        .sort_values("Affiliation %", ascending=False)
        .reset_index(drop=True)
    )

    total_players = int(school_data["Total Players"].iloc[0])
    primary = school_data.iloc[0]

    st.caption(f"{total_players} total players from this school")

    st.markdown("### Most Common Club")

    if st.button(primary["Club"], type="secondary"):
        st.session_state["mode_state"] = "Club"
        st.session_state["selected_club"] = primary["Club"]
        st.rerun()

    st.markdown(
        f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Affiliation %']}%</div>",
        unsafe_allow_html=True
    )

    st.markdown("### Top 3 Clubs")

    for i in range(min(3, len(school_data))):
        row = school_data.iloc[i]

        if st.button(row["Club"], key=f"top_club_{i}", type="secondary"):
            st.session_state["mode_state"] = "Club"
            st.session_state["selected_club"] = row["Club"]
            st.rerun()

        st.markdown(
            f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Full Breakdown")

    for i, row in school_data.iterrows():
        if st.button(row["Club"], key=f"club_full_{i}", type="secondary"):
            st.session_state["mode_state"] = "Club"
            st.session_state["selected_club"] = row["Club"]
            st.rerun()

        st.markdown(
            f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Distribution Chart")
    st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if st.session_state["mode_state"] == "Club":

    clubs = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        clubs,
        index=clubs.index(st.session_state["selected_club"])
        if st.session_state["selected_club"] in clubs else 0,
        placeholder="Start typing your club..."
    )

    st.session_state["selected_club"] = selected_club

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

    primary = breakdown.iloc[0]

    st.markdown("### Most Common School")

    if st.button(primary["School"], type="secondary"):
        st.session_state["mode_state"] = "School"
        st.session_state["selected_school"] = primary["School"]
        st.rerun()

    st.markdown(
        f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Share %']}%</div>",
        unsafe_allow_html=True
    )

    st.markdown("### Top 3 Schools")

    for i in range(min(3, len(breakdown))):
        row = breakdown.iloc[i]

        if st.button(row["School"], key=f"top_school_{i}", type="secondary"):
            st.session_state["mode_state"] = "School"
            st.session_state["selected_school"] = row["School"]
            st.rerun()

        st.markdown(
            f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Full Breakdown")

    for i, row in breakdown.iterrows():
        if st.button(row["School"], key=f"school_full_{i}", type="secondary"):
            st.session_state["mode_state"] = "School"
            st.session_state["selected_school"] = row["School"]
            st.rerun()

        st.markdown(
            f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
            unsafe_allow_html=True
        )

    st.markdown("### Distribution Chart")
    st.bar_chart(breakdown.set_index("School")["Share %"])

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
