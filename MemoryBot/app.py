"""
MemoryBot — Streamlit UI

Run with:
    streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Page config  (must be first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="MemoryBot",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Custom CSS — clean chat bubbles
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── overall ── */
    .stApp { background: #0f1117; }

    /* ── chat bubble helpers ── */
    .bubble-row          { display:flex; margin-bottom:12px; }
    .bubble-row.user     { justify-content:flex-end; }
    .bubble-row.bot      { justify-content:flex-start; }
    .bubble {
        max-width:72%;
        padding:12px 18px;
        border-radius:18px;
        line-height:1.55;
        font-size:0.95rem;
    }
    .bubble.user {
        background:#1d4ed8;
        color:#fff;
        border-bottom-right-radius:4px;
    }
    .bubble.bot {
        background:#1e293b;
        color:#e2e8f0;
        border-bottom-left-radius:4px;
    }

    /* ── sidebar memory cards ── */
    .mem-card {
        background:#1e293b;
        border-left:3px solid #3b82f6;
        border-radius:6px;
        padding:10px 14px;
        margin-bottom:10px;
        font-size:0.85rem;
        color:#cbd5e1;
        line-height:1.45;
    }
    .mem-tag {
        font-size:0.7rem;
        color:#64748b;
        margin-bottom:4px;
        text-transform:uppercase;
        letter-spacing:.06em;
    }

    /* hide Streamlit's default header */
    header[data-testid="stHeader"] { display:none; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session-state initialisation
# ---------------------------------------------------------------------------

def _init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []          # list of {"role", "content"}
    if "bot" not in st.session_state:
        st.session_state.bot = None             # MemoryBotChain instance
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "last_summary" not in st.session_state:
        st.session_state.last_summary = None    # show when Pinecone summarises

_init_state()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_bot(name: str):
    """Instantiate MemoryBotChain and seed messages from SQLite."""
    from memorybot.chain import MemoryBotChain
    from memorybot.database import load_recent_messages

    bot = MemoryBotChain.from_env(user_name=name)
    st.session_state.bot = bot

    # Seed the visible chat history from SQLite so returning users see context
    recent = load_recent_messages(bot.conn, bot.user_id, limit=30)
    st.session_state.messages = [
        {"role": r["role"], "content": r["content"]} for r in recent
    ]


def render_bubble(role: str, content: str):
    bubble_class = "user" if role == "human" else "bot"
    row_class    = "user" if role == "human" else "bot"
    st.markdown(
        f"""
        <div class="bubble-row {row_class}">
            <div class="bubble {bubble_class}">{content}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_memory_sidebar(bot):
    """Show long-term memories retrieved from Pinecone + recent facts."""
    from memorybot.vector_store import retrieve_memories
    from memorybot.database import count_unsummarized

    with st.sidebar:
        st.markdown("## 🧠 MemoryBot")
        st.caption(f"Talking to: **{bot.name}**")
        st.divider()

        # Pinecone memories
        st.markdown("### 📚 Long-term memories")
        memories = retrieve_memories(
            bot.memory.index,
            user_id=str(bot.user_id),
            query=bot.name,
            top_k=5,
        )
        if memories:
            for mem in memories:
                st.markdown(
                    f'<div class="mem-card"><div class="mem-tag">📌 pinecone summary</div>{mem}</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No long-term memories yet. Chat for a while and they'll appear here after 10 messages.")

        st.divider()

        # Un-summarized message count
        pending = count_unsummarized(bot.conn, bot.user_id)
        every   = int(os.getenv("SUMMARIZE_EVERY", "10"))
        st.caption(f"📊 {pending}/{every} messages until next memory snapshot")

        # Last summary that was just created
        if st.session_state.last_summary:
            st.success(f"✅ New memory stored:\n\n{st.session_state.last_summary}")
            st.session_state.last_summary = None

        st.divider()

        # Danger zone
        st.markdown("### ⚙️ Controls")
        if st.button("🗑️ Clear session buffer", use_container_width=True):
            bot.clear_session_memory()
            st.session_state.messages = []
            st.rerun()

        st.caption(
            "Note: 'Clear session' only wipes the in-memory buffer. "
            "SQLite history and Pinecone memories are preserved."
        )


# ---------------------------------------------------------------------------
# Onboarding — collect user name
# ---------------------------------------------------------------------------

def onboarding_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center;padding:60px 0 20px">
                <div style="font-size:64px">🧠</div>
                <h1 style="color:#e2e8f0;margin-bottom:4px">MemoryBot</h1>
                <p style="color:#64748b;font-size:1.05rem">
                    A chatbot that <em>actually</em> remembers you.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form("onboarding"):
            name = st.text_input(
                "What's your name?",
                placeholder="e.g. Hamdan",
                help="MemoryBot will remember you across sessions.",
            )
            submitted = st.form_submit_button("Start chatting →", use_container_width=True)

        if submitted and name.strip():
            st.session_state.user_name = name.strip()
            with st.spinner("Loading your memories…"):
                load_bot(name.strip())
            st.rerun()
        elif submitted:
            st.warning("Please enter your name to continue.")


# ---------------------------------------------------------------------------
# Main chat screen
# ---------------------------------------------------------------------------

def chat_screen():
    bot = st.session_state.bot
    render_memory_sidebar(bot)

    # Header
    st.markdown(
        f"""
        <h2 style="color:#e2e8f0;margin-bottom:2px">
            💬 Chat with MemoryBot
        </h2>
        <p style="color:#64748b;margin-top:0">
            Hi <strong>{bot.name}</strong> — I remember our past conversations.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    # Chat history
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown(
                '<p style="color:#475569;text-align:center;padding:40px 0">'
                "No messages yet. Say hello! 👋"
                "</p>",
                unsafe_allow_html=True,
            )
        for msg in st.session_state.messages:
            render_bubble(msg["role"], msg["content"])

    st.divider()

    # Input box
    with st.form("chat_form", clear_on_submit=True):
        col_input, col_send = st.columns([9, 1])
        with col_input:
            user_input = st.text_input(
                "Message",
                placeholder="Type a message…",
                label_visibility="collapsed",
            )
        with col_send:
            send = st.form_submit_button("Send", use_container_width=True)

    if send and user_input.strip():
        # Optimistically append user message
        st.session_state.messages.append({"role": "human", "content": user_input.strip()})

        with st.spinner("Thinking…"):
            result = bot.chat(user_input.strip())

        st.session_state.messages.append({"role": "ai", "content": result.reply})

        if result.summary_created:
            st.session_state.last_summary = result.summary_created

        st.rerun()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not st.session_state.user_name or st.session_state.bot is None:
        onboarding_screen()
    else:
        chat_screen()


if __name__ == "__main__":
    main()
else:
    # Streamlit runs the module directly — call main() at module level
    main()
