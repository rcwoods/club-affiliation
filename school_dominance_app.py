import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="centered"
)

# --------------------------------------------------
# GLOBAL STYLING
# --------------------------------------------------

st.markdown("""
<style>

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

.header-row {
    font-weight: 600;
    opacity: 0.75;
    padding-bottom: 4px;
}
.compact-row {
    padding: 2px 0px;
}
.divider-line {
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin: 4px 0 6px 0;
}

.block-container {
    padding-top: 2rem;
}

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

st.title("Club Affiliation Explorer")
st.caption("McKinnon Basketball Association")

mode = st.radio(
    "Search by",
    ["School", "Club"],
    horizontal=True
)

st.session_state.mode = mode
st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    schools = sorted(df["School"].unique())

    selected = st.multiselect(
        "Select a School",
        schools,
        default=[st.session_state.selected_school] if st.session_state.selected_school else [],
        max_selections=1
    )

    if selected:

        selected_school = selected[0]
        st.session_state.selected_school = selected_school

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        st.caption(f"{int(primary['Total Players'])} total players from this school")

        st.markdown("### Most Common Club")

        if st.button(primary["Club"], key="primary_club", type="secondary"):
            st.session_state.mode = "Club"
            st.session_state.selected_club = primary["Club"]
            st.rerun()

        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        st.markdown("### Full Breakdown")

        h1, h2, h3 = st.columns([5,1,1], gap="small")
        h1.markdown('<div class="header-row">Club</div>', unsafe_allow_html=True)
        h2.markdown('<div class="header-row" style="text-align:right;">Players</div>', unsafe_allow_html=True)
        h3.markdown('<div class="header-row" style="text-align:right;">% Share</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

        for i, row in school_data.iterrows():
            c1, c2, c3 = st.columns([5,1,1], gap="small")

            if c1.button(row["Club"], key=f"club_{i}", type="secondary"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.rerun()

            c2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='text-align:right'>{row['Affiliation %']}%</div>", unsafe_allow_html=True)

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())

    selected = st.multiselect(
        "Select a Club",
        clubs,
        default=[st.session_state.selected_club] if st.session_state.selected_club else [],
        max_selections=1
    )

    if selected:

        selected_club = selected[0]
        st.session_state.selected_club = selected_club

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        st.markdown("### Full Breakdown")

        breakdown = club_data.copy()
        breakdown["Share %"] = (
            breakdown["Club Players"] / total_players * 100
        ).round(2)

        h1, h2, h3 = st.columns([5,1,1], gap="small")
        h1.markdown('<div class="header-row">School</div>', unsafe_allow_html=True)
        h2.markdown('<div class="header-row" style="text-align:right;">Players</div>', unsafe_allow_html=True)
        h3.markdown('<div class="header-row" style="text-align:right;">% Share</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

        for i, row in breakdown.iterrows():
            c1, c2, c3 = st.columns([5,1,1], gap="small")

            if c1.button(row["School"], key=f"school_{i}", type="secondary"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.rerun()

            c2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            c3.markdown(f"<div style='text-align:right'>{row['Share %']}%</div>", unsafe_allow_html=True)

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
