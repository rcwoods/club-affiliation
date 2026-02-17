import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="School–Club Affiliation Explorer",
    layout="wide"
)

# --------------------------------------------------
# GLOBAL STYLING
# --------------------------------------------------

st.markdown("""
<style>

.block-container {
    padding-top: 3rem;
    padding-bottom: 5rem;
}

div[data-baseweb="select"] {
    margin-top: 1.2rem;
}

button[kind="secondary"] {
    background: none !important;
    border: none !important;
    padding: 6px 0 !important;
    color: inherit !important;
    font-weight: 600 !important;
    text-align: left !important;
    font-size: 17px !important;
}

button[kind="secondary"]:hover {
    text-decoration: underline;
}

.section-space {
    margin-top: 2.2rem;
}

.rank-number {
    font-weight: 700;
    opacity: 0.5;
    font-size: 14px;
    margin-top: 0.5rem;
}

.sub-text {
    font-size: 14px;
    opacity: 0.75;
    margin-bottom: 18px;
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
# HEADER
# --------------------------------------------------

st.title("McKinnon Basketball Association")
st.subheader("School–Club Affiliation Explorer")
st.caption("Explore player distribution and % share across schools and clubs")

mode = st.radio("Search by", ["School", "Club"], horizontal=True)

st.divider()

# ==================================================
# SCHOOL MODE
# ==================================================

if mode == "School":

    schools = sorted(df["School"].unique())

    selected_school = st.selectbox(
        "Select a School",
        options=["Choose an option"] + schools
    )

    if selected_school != "Choose an option":

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        if school_data.empty:
            st.stop()

        total_players = int(school_data["Total Players"].iloc[0])
        primary = school_data.iloc[0]

        st.caption(f"{total_players} total players from this school")

        # MOST COMMON
        st.markdown("## Most Common Club")

        if st.button(primary["Club"], type="secondary"):
            st.session_state["mode"] = "Club"
            st.session_state["selected_club_temp"] = primary["Club"]

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players from this school • {primary['Affiliation %']}% Share</div>",
            unsafe_allow_html=True
        )

        # FULL BREAKDOWN
        st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)
        st.markdown("## Full Breakdown")

        for i, row in school_data.iterrows():

            col_rank, col_name = st.columns([1,9])
            col_rank.markdown(f"<div class='rank-number'>#{i+1}</div>", unsafe_allow_html=True)

            if col_name.button(row["Club"], key=f"school_{i}", type="secondary"):
                st.session_state["mode"] = "Club"
                st.session_state["selected_club_temp"] = row["Club"]

            col_name.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players from this school • {row['Affiliation %']}% Share</div>",
                unsafe_allow_html=True
            )

        # CHART
        st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)
        st.markdown("## Distribution Chart")

        fig = px.bar(
            school_data,
            x="Club",
            y="Affiliation %",
            text="Affiliation %",
        )

        fig.update_layout(
            xaxis_title="Club",
            yaxis_title="% Share",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

# ==================================================
# CLUB MODE
# ==================================================

if mode == "Club":

    clubs = sorted(df["Club"].unique())

    selected_club = st.selectbox(
        "Select a Club",
        options=["Choose an option"] + clubs
    )

    # Auto-select from navigation click
    if "selected_club_temp" in st.session_state:
        selected_club = st.session_state["selected_club_temp"]
        del st.session_state["selected_club_temp"]

    if selected_club != "Choose an option":

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        if club_data.empty:
            st.stop()

        total_players = club_data["Club Players"].sum()
        club_data["Share %"] = (
            club_data["Club Players"] / total_players * 100
        ).round(2)

        primary = club_data.iloc[0]

        st.caption(f"{total_players} total players across {club_data.shape[0]} schools")

        # MOST COMMON
        st.markdown("## Most Common School")

        if st.button(primary["School"], type="secondary"):
            st.session_state["mode"] = "School"
            st.session_state["selected_school_temp"] = primary["School"]

        st.markdown(
            f"<div class='sub-text'>{int(primary['Club Players'])} players from this club • {primary['Share %']}% Share</div>",
            unsafe_allow_html=True
        )

        # FULL BREAKDOWN
        st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)
        st.markdown("## Full Breakdown")

        for i, row in club_data.iterrows():

            col_rank, col_name = st.columns([1,9])
            col_rank.markdown(f"<div class='rank-number'>#{i+1}</div>", unsafe_allow_html=True)

            if col_name.button(row["School"], key=f"club_{i}", type="secondary"):
                st.session_state["mode"] = "School"
                st.session_state["selected_school_temp"] = row["School"]

            col_name.markdown(
                f"<div class='sub-text'>{int(row['Club Players'])} players from this club • {row['Share %']}% Share</div>",
                unsafe_allow_html=True
            )

        # CHART
        st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)
        st.markdown("## Distribution Chart")

        fig = px.bar(
            club_data,
            x="School",
            y="Share %",
            text="Share %",
        )

        fig.update_layout(
            xaxis_title="School",
            yaxis_title="% Share",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
