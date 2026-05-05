import streamlit as st
from knowledge_gap import run_knowledge_gap_analysis

st.set_page_config(
    page_title="Knowledge Gap Detector",
    page_icon="🔍",
    layout="centered"
)

st.title("🔍 Knowledge Gap Detector")
st.caption("Understand what topics you're missing based on your Notion notes")

st.divider()

# ---- User Context Input ----
st.subheader("Tell us about yourself")
user_context = st.text_area(
    label="What is your field, goal, or role?",
    placeholder="e.g. I am a software engineering student focusing on AI/ML...",
    height=100
)

st.divider()

if st.button("🚀 Run Analysis", use_container_width=True):

    with st.spinner("Analyzing your notes... this may take a minute"):
        results, error = run_knowledge_gap_analysis(user_context=user_context)

    if error:
        st.error(error)

    else:
        # ---- Topics You Cover ----
        st.subheader("Topics You Already Cover")
        cols = st.columns(3)
        for i, cluster in enumerate(results["clusters"]):
            with cols[i % 3]:
                st.metric(
                    label=cluster["name"],
                    value=f"{cluster['chunk_count']} chunks"
                )
                with st.expander("Sources"):
                    for source in cluster["sources"]:
                        st.markdown(f"- {source}")

        st.divider()

        # ---- Blind Spots ----
        st.subheader("Gaps in Your Knowledge")
        if results["blind_spots"]:
            for spot in results["blind_spots"]:
                st.warning(f"📭 **{spot['topic']}**\n\n{spot['description']}")
        else:
            st.success("Great coverage! No major gaps detected.")