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
# MODE SELECTOR
# --------------------------------------------------

mode = st.radio(
    "",
    ["School", "Club"],
    horizontal=True
)

st.divider()

# --------------------------------------------------
# SCHOOL MODE
# --------------------------------------------------

if mode == "School":

    selected_school = st.selectbox(
        "Select a School",
        options=["Select a School"] + sorted(df["School"].unique())
    )

    if selected_school != "Select a School":

        school_data = (
            df[df["School"] == selected_school]
            .sort_values("Affiliation %", ascending=False)
            .reset_index(drop=True)
        )

        total_players = int(school_data["Total Players"].iloc[0])
        primary = school_data.iloc[0]

        # Title
        st.markdown(f"# {selected_school}")
        st.caption(f"{total_players} total players from this school")

        st.divider()

        # Most Common Club
        st.markdown("## Most Common Club")

        if st.button(primary["Club"], key="primary_club"):
            st.session_state.mode = "Club"
            st.experimental_rerun()

        st.markdown(f"### {primary['Affiliation %']:.2f}%")

        st.divider()

        # Top 3 Clubs
        st.markdown("## Top 3 Clubs")

        for i in range(min(3, len(school_data))):
            row = school_data.iloc[i]

            col1, col2 = st.columns([4,1])

            with col1:
                if st.button(row["Club"], key=f"top_club_{i}"):
                    st.session_state.mode = "Club"
                    st.experimental_rerun()

            with col2:
                st.markdown(f"**{row['Affiliation %']:.2f}%**")

        st.divider()

        # Full Breakdown (Mobile Friendly)
        st.markdown("## Full Breakdown")

        for _, row in school_data.iterrows():
            st.markdown(
                f"""
                <div style="
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.08);
                ">
                    <div style="font-weight: 500; font-size: 16px;">
                        {row['Club']}
                    </div>
                    <div style="
                        font-size: 14px;
                        color: rgba(255,255,255,0.7);
                        margin-top: 4px;
                    ">
                        {int(row['Club Players'])} players • {row['Affiliation %']:.2f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# --------------------------------------------------
# CLUB MODE
# --------------------------------------------------

if mode == "Club":

    selected_club = st.selectbox(
        "Select a Club",
        options=["Select a Club"] + sorted(df["Club"].unique())
    )

    if selected_club != "Select a Club":

        club_data = (
            df[df["Club"] == selected_club]
            .sort_values("Club Players", ascending=False)
            .reset_index(drop=True)
        )

        total_players = int(club_data["Club Players"].sum())
        total_schools = club_data["School"].nunique()
        primary_school = club_data.iloc[0]

        # Title
        st.markdown(f"# {selected_club}")
        st.caption(f"{total_players} total players across {total_schools} schools")

        st.divider()

        # Most Common School
        st.markdown("## Most Common School")

        if st.button(primary_school["School"], key="primary_school"):
            st.session_state.mode = "School"
            st.experimental_rerun()

        st.markdown(
            f"### {int(primary_school['Club Players'])} players • "
            f"{primary_school['Affiliation %']:.2f}%"
        )

        st.divider()

        # Top 3 Schools
        st.markdown("## Top 3 Schools")

        for i in range(min(3, len(club_data))):
            row = club_data.iloc[i]

            col1, col2 = st.columns([4,1])

            with col1:
                if st.button(row["School"], key=f"top_school_{i}"):
                    st.session_state.mode = "School"
                    st.experimental_rerun()

            with col2:
                st.markdown(f"**{row['Affiliation %']:.2f}%**")

        st.divider()

        # Full Breakdown (Mobile Friendly)
        st.markdown("## Full Breakdown")

        for _, row in club_data.iterrows():
            st.markdown(
                f"""
                <div style="
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(255,255,255,0.08);
                ">
                    <div style="font-weight: 500; font-size: 16px;">
                        {row['School']}
                    </div>
                    <div style="
                        font-size: 14px;
                        color: rgba(255,255,255,0.7);
                        margin-top: 4px;
                    ">
                        {int(row['Club Players'])} players • {row['Affiliation %']:.2f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Data reflects registered player distribution by school and club.")
