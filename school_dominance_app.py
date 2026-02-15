import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE CONFIG (MUST BE FIRST)
# --------------------------------------------------

st.set_page_config(
    page_title="Club Affiliation Explorer",
    layout="centered"
)

# --------------------------------------------------
# CLEAN CLICKABLE STYLE
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

    selected_school = st.selectbox(
        "Select a School",
        ["Select a School"] + schools,
        index=(
            schools.index(st.session_state.selected_school) + 1
            if st.session_state.selected_school in schools
            else 0
        )
    )

    if selected_school != "Select a School":

        st.session_state.selected_school = selected_school

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        primary = school_data.iloc[0]

        st.caption(f"{int(primary['Total Players'])} total players from this school")

        # Most Common Club
        st.markdown("### Most Common Club")

        if st.button(primary["Club"], key="primary_club", type="secondary"):
            st.session_state.mode = "Club"
            st.session_state.selected_club = primary["Club"]
            st.rerun()

        st.metric("Affiliation Share", f"{primary['Affiliation %']}%")

        # Top 3 Clubs
        st.markdown("### Top 3 Clubs")

        for i, row in school_data.head(3).iterrows():
            col1, col2, col3 = st.columns([4, 1, 1])

            if col1.button(row["Club"], key=f"club_top_{i}", type="secondary"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.rerun()

            col2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='text-align:right'>{row['Affiliation %']}%</div>", unsafe_allow_html=True)

        # Full Breakdown
        st.markdown("### Full Breakdown")

        header1, header2, header3 = st.columns([4, 1, 1])
        header1.markdown("**Club**")
        header2.markdown("**Players**")
        header3.markdown("**% Share**")

        st.markdown("---")

        for i, row in school_data.iterrows():

            col1, col2, col3 = st.columns([4, 1, 1])

            if col1.button(row["Club"], key=f"club_full_{i}", type="secondary"):
                st.session_state.mode = "Club"
                st.session_state.selected_club = row["Club"]
                st.rerun()

            col2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='text-align:right'>{row['Affiliation %']}%</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:6px 0; opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("### Affiliation Share")
        st.bar_chart(school_data.set_index("Club")["Affiliation %"])

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        ["Select a Club"] + clubs,
        index=(
            clubs.index(st.session_state.selected_club) + 1
            if st.session_state.selected_club in clubs
            else 0
        )
    )

    if selected_club != "Select a Club":

        st.session_state.selected_club = selected_club

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = club_data["Club Players"].sum()
        primary = club_data.iloc[0]

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        # Most Represented School
        st.markdown("### Most Represented School")

        if st.button(primary["School"], key="primary_school", type="secondary"):
            st.session_state.mode = "School"
            st.session_state.selected_school = primary["School"]
            st.rerun()

        share = round((primary["Club Players"] / total_players) * 100, 2)
        st.metric("Share of Club Players", f"{share}%")

        # Top 3 Schools
        st.markdown("### Top 3 Schools")

        for i, row in club_data.head(3).iterrows():
            col1, col2, col3 = st.columns([4, 1, 1])

            if col1.button(row["School"], key=f"school_top_{i}", type="secondary"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.rerun()

            col2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='text-align:right'>{round((row['Club Players']/total_players)*100, 2)}%</div>", unsafe_allow_html=True)

        # Full Breakdown
        st.markdown("### Full Breakdown")

        breakdown = club_data.copy()
        breakdown["Share %"] = (
            breakdown["Club Players"] / total_players * 100
        ).round(2)

        header1, header2, header3 = st.columns([4, 1, 1])
        header1.markdown("**School**")
        header2.markdown("**Players**")
        header3.markdown("**% Share**")

        st.markdown("---")

        for i, row in breakdown.iterrows():

            col1, col2, col3 = st.columns([4, 1, 1])

            if col1.button(row["School"], key=f"school_full_{i}", type="secondary"):
                st.session_state.mode = "School"
                st.session_state.selected_school = row["School"]
                st.rerun()

            col2.markdown(f"<div style='text-align:right'>{int(row['Club Players'])}</div>", unsafe_allow_html=True)
            col3.markdown(f"<div style='text-align:right'>{row['Share %']}%</div>", unsafe_allow_html=True)

            st.markdown("<hr style='margin:6px 0; opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("### Players by School")
        st.bar_chart(club_data.set_index("School")["Club Players"])

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
