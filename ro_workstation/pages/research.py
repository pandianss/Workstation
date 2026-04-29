import streamlit as st

from modules.knowledge.qa import answer_question
from modules.utils.page_helpers import render_page_header
from modules.ui.theme import render_callout


user = render_page_header(
    "AI Research Assistant",
    "Search circulars and knowledge notes with department-aware context, then keep the answer trail visible.",
)

toolbar_left, toolbar_right = st.columns([1, 1])
with toolbar_left:
    st.caption(f"Active search scope: {user['department']}")
with toolbar_right:
    if st.button("Clear Conversation"):
        st.session_state.research_messages = []
        st.rerun()

render_callout(
    "How to use this well",
    "Ask specific operational questions like applicable circular position, return expectations, or note points to watch.",
)

if "research_messages" not in st.session_state:
    st.session_state.research_messages = []

for msg in st.session_state.research_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Sources"):
                for idx, src in enumerate(msg["sources"]):
                    st.write(f"[{idx + 1}] {src.get('title', 'Unknown')} (Page {src.get('page', 'N/A')})")

if prompt := st.chat_input("Ask a banking question..."):
    st.session_state.research_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            result = answer_question(prompt, dept_filter=user["department"])
            st.markdown(result["answer"])
            if result.get("sources"):
                with st.expander("Sources"):
                    for idx, src in enumerate(result["sources"]):
                        st.write(f"[{idx + 1}] {src.get('title', 'Unknown')} (Page {src.get('page', 'N/A')})")

    st.session_state.research_messages.append(
        {"role": "assistant", "content": result["answer"], "sources": result.get("sources", [])}
    )
