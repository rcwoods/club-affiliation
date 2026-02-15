import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL STYLING (Clean + Mobile Safe)
# --------------------------------------------------

st.markdown("""
<style>

/* Page spacing */
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

/* Section headings larger */
h3 {
    font-size: 1.6rem !important;
    margin-top: 2rem !important;
    margin-bottom: 0.8rem !important;
}

/* Clickable names */
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

/* Subtext styling */
.sub-text {
    font-size: 14px;
    opacity: 0.75;
    margin-bottom: 14px;
}

/* Row spacing */
.breakdown-row {
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

/* Hide Streamlit footer */
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
    horizontal=True,
    index=0 if st.session_state.mode == "School" else 1
)

st.session_state.mode = mode
st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    schools = sorted(df["School"].unique())
    school_options = ["Select a School"] + schools

    selected_school = st.selectbox(
        "Select a School",
        school_options,
        index=0 if st.session_state.selected_school is None
              else school_options.index(st.session_state.selected_school),
        key="selected_school"
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

        # ---------------- MOST COMMON ----------------
        st.markdown("### Most Common Club")

        if st.button(primary["Club"], key="primary_club", type="secondary"):
            st.session_state.mode = "Club"
            st.session_state.selected_club = primary["Club"]
            st.session_state.selected_school = None
            st.rerun()

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Affiliation %']}%</div>",
            unsafe_allow_html=True
        )

        # ---------------- TOP 3 ----------------
        st.markdown("### Top 3 Clubs")

        for i in range(min(3, len(school_data))):
            row = school_data.iloc[i]

            if st.button(row["Club"], key=f"top_club_{i}", type="secondary"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.session_state.selected_school = None
                st.rerun()

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
                unsafe_allow_html=True
            )

        # ---------------- FULL BREAKDOWN ----------------
        st.markdown("### Full Breakdown")

        for i, row in school_data.iterrows():

            if st.button(row["Club"], key=f"club_full_{i}", type="secondary"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.session_state.selected_school = None
                st.rerun()

            st.markdown(
                f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Affiliation %']}%</div>",
                unsafe_allow_html=True
            )

        # ---------------- CHART ----------------
        st.markdown("### Distribution")

        fig = px.bar(
            school_data.head(10),
            x="Club Players",
            y="Club",
            orientation="h",
            text="Affiliation %"
        )

        fig.update_layout(
            height=400,
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())
    club_options = ["Select a Club"] + clubs

    selected_club = st.selectbox(
        "Select a Club",
        club_options,
        index=0 if st.session_state.selected_club is None
              else club_options.index(st.session_state.selected_club),
        key="selected_club"
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

        primary = breakdown.iloc[0]

        # ---------------- MOST COMMON ----------------
        st.markdown("### Most Common School")

        if st.button(primary["School"], key="primary_school", type="secondary"):
            st.session_state.mode = "School"
            st.session_state.selected_school = primary["School"]
            st.session_state.selected_club = None
            st.rerun()

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players • {primary['Share %']}%</div>",
            unsafe_allow_html=True
        )

        # ---------------- TOP 3 ----------------
        st.markdown("### Top 3 Schools")

        for i in range(min(3, len(breakdown))):
            row = breakdown.iloc[i]

            if st.button(row["School"], key=f"top_school_{i}", type="secondary"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.session_state.selected_club = None
                st.rerun()

            st.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
                unsafe_allow_html=True
            )

        # ---------------- FULL BREAKDOWN ----------------
        st.markdown("### Full Breakdown")

        for i, row in breakdown.iterrows():

            if st.button(row["School"], key=f"school_full_{i}", type="secondary"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.session_state.selected_club = None
                st.rerun()

            st.markdown(
                f"<div class='sub-text breakdown-row'>{int(row['Club Players'])} players • {row['Share %']}%</div>",
                unsafe_allow_html=True
            )

        # ---------------- CHART ----------------
        st.markdown("### Distribution")

        fig = px.bar(
            breakdown.head(10),
            x="Club Players",
            y="School",
            orientation="h",
            text="Share %"
        )

        fig.update_layout(
            height=400,
            yaxis=dict(autorange="reversed"),
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
