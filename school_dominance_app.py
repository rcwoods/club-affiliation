import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="School Club Dominance Search",
    layout="centered"
)

@st.cache_data
def load_data():
    df = pd.read_csv("Schools per Club.csv")
    df = df.dropna(subset=["School Details"])

    # Rename columns for clarity
    df = df.rename(columns={
        "Count": "Total Players",
        "Count.1": "Club Players"
    })

    # Calculate % share correctly
    df["% Share"] = (
        df["Club Players"] / df["Total Players"] * 100
    ).round(2)

    return df


df = load_data()

st.title("🏀 School → Club Dominance Search")
st.write("Search any school to see which basketball club dominates it.")

# Create searchable dropdown
school_list = sorted(df["School Details"].unique())
selected_school = st.selectbox("Select a School", school_list)

if selected_school:
    school_data = df[df["School Details"] == selected_school]
    school_data = school_data.sort_values("% Share", ascending=False)

    dominant = school_data.iloc[0]

    st.subheader("📊 Dominant Club")
    st.success(
        f"{dominant['Club']} dominates {selected_school} "
        f"with {dominant['% Share']}% "
        f"({int(dominant['Club Players'])} of {int(dominant['Total Players'])} players)."
    )

    st.subheader("Full Breakdown")
    st.dataframe(
        school_data[["Club", "Club Players", "Total Players", "% Share"]]
        .rename(columns={"Club Players": "Players at Club"}),
        use_container_width=True
    )

    st.bar_chart(
        school_data.set_index("Club")["% Share"]
    )

st.caption("Built for quick school-club dominance lookup.")
