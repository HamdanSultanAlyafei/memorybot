"""
MemoryBotChain — the main entry point for the application.

Wires together:
  ChatGroq       ←  LLM (free, fast — Llama 3.3 70B via Groq)
  MemoryManager  ←  short-term buffer + Pinecone long-term
  SQLite         ←  raw message persistence
  Summarization  ←  triggered automatically every N messages

Usage
-----
    bot = MemoryBotChain.from_env(user_name="Hamdan")
    reply = bot.chat("What was my favourite colour again?")
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from memorybot.database import init_db, get_or_create_user, save_message
from memorybot.vector_store import get_or_create_index
from memorybot.memory_manager import MemoryManager


# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------

SYSTEM_TEMPLATE = """\
You are MemoryBot, a personal AI assistant with persistent memory.
You remember the user across sessions — their name, preferences, past \
conversations, and important facts they've shared.

User's name: {user_name}

{context}

Instructions:
- Greet the user by name when appropriate.
- Proactively reference past memories when they're relevant.
- Be warm, concise, and helpful.
- If a user shares a new fact about themselves (preference, goal, opinion),
  acknowledge it explicitly so they know you've noted it.
"""


# ---------------------------------------------------------------------------
# Main chain class
# ---------------------------------------------------------------------------

@dataclass
class ChatResult:
    reply: str
    summary_created: str | None   # set if a Pinecone summary was triggered


class MemoryBotChain:
    """
    High-level interface: call .chat(user_input) and get a reply.
    All persistence (SQLite save, Pinecone upsert) happens automatically.
    """

    def __init__(self, llm, memory_manager, db_conn, user_id, user_name):
        self.llm     = llm
        self.memory  = memory_manager
        self.conn    = db_conn
        self.user_id = user_id
        self.name    = user_name

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_env(cls, user_name: str, db_path: str | None = None) -> "MemoryBotChain":
        """
        Construct a MemoryBotChain from environment variables.
        Reads: GROQ_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME,
               BUFFER_WINDOW_K, PINECONE_TOP_K, SUMMARIZE_EVERY, SQLITE_DB_PATH
        """
        load_dotenv()

        groq_key     = os.environ["GROQ_API_KEY"]
        pinecone_key = os.environ["PINECONE_API_KEY"]
        index_name   = os.getenv("PINECONE_INDEX_NAME", "memorybot-memories")
        db_path      = db_path or os.getenv("SQLITE_DB_PATH", "memorybot.db")
        buffer_k     = int(os.getenv("BUFFER_WINDOW_K", "6"))
        top_k        = int(os.getenv("PINECONE_TOP_K", "3"))
        summarize_n  = int(os.getenv("SUMMARIZE_EVERY", "10"))

        # LLM — Groq free tier: llama-3.3-70b-versatile
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=groq_key,
            temperature=0.7,
            max_tokens=1024,
        )

        # SQLite
        conn    = init_db(db_path)
        user_id = get_or_create_user(conn, user_name)

        # Pinecone
        index = get_or_create_index(pinecone_key, index_name)

        # Memory manager
        memory = MemoryManager(
            db_conn=conn,
            pinecone_index=index,
            llm=llm,
            user_id=user_id,
            user_name=user_name,
            buffer_k=buffer_k,
            top_k=top_k,
            summarize_every=summarize_n,
        )

        return cls(llm=llm, memory_manager=memory, db_conn=conn,
                   user_id=user_id, user_name=user_name)

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(self, user_input: str) -> ChatResult:
        """
        Send a message and return a ChatResult with the reply.
        Steps: build context → call LLM → save to SQLite → update buffer → maybe summarize
        """
        context  = self.memory.build_context(user_input)
        system   = SYSTEM_TEMPLATE.format(user_name=self.name, context=context)
        messages = [SystemMessage(content=system), HumanMessage(content=user_input)]

        response = self.llm.invoke(messages)
        reply    = response.content.strip()

        save_message(self.conn, self.user_id, role="human", content=user_input)
        save_message(self.conn, self.user_id, role="ai",    content=reply)

        self.memory.add_exchange(user_input, reply)
        summary = self.memory.maybe_summarize()

        return ChatResult(reply=reply, summary_created=summary)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def clear_session_memory(self) -> None:
        self.memory.clear()

    def get_recent_messages(self, limit: int = 20) -> list[dict]:
        from memorybot.database import load_recent_messages
        return load_recent_messages(self.conn, self.user_id, limit=limit)
