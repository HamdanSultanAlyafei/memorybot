"""
MemoryManager — combines short-term buffer with long-term Pinecone retrieval.

Responsibilities
----------------
1. Short-term  A simple rolling list keeps the last K exchanges in-process
               (no external dependency, no deprecated LangChain memory module).
2. Long-term   After every SUMMARIZE_EVERY messages, MemoryManager asks the
               LLM to write a compact summary of the unsummarized messages,
               embeds it, and upserts it into Pinecone.
3. Retrieval   build_context(user_input) returns a combined context string
               to prepend to every Claude prompt.
"""

from collections import deque
from typing import Optional

from memorybot.database import (
    get_unsummarized_messages,
    mark_messages_summarized,
    count_unsummarized,
    load_recent_messages,
)
from memorybot.vector_store import store_memory, retrieve_memories


# ---------------------------------------------------------------------------
# Summarizer prompt
# ---------------------------------------------------------------------------

SUMMARIZE_PROMPT = """\
You are a memory encoder. Below is a conversation excerpt.
Write a single concise paragraph (<=80 words) capturing:
- The user's name and any stated personal details
- Preferences, opinions, or facts about the user
- Key topics discussed and conclusions reached

Be specific. Omit filler. Use third-person ("The user said...").

CONVERSATION:
{conversation}

SUMMARY:"""


class MemoryManager:
    """
    Hybrid memory: short-term rolling buffer + long-term Pinecone retrieval.

    Parameters
    ----------
    db_conn         : open sqlite3.Connection
    pinecone_index  : Pinecone Index object
    llm             : LangChain chat model (used for summarization)
    user_id         : integer DB user ID
    user_name       : display name
    buffer_k        : number of recent exchanges to keep (each = 1 human + 1 ai)
    top_k           : long-term memories to retrieve per turn
    summarize_every : trigger summarization after this many un-summarized messages
    """

    def __init__(
        self,
        db_conn,
        pinecone_index,
        llm,
        user_id: int,
        user_name: str,
        buffer_k: int = 6,
        top_k: int = 3,
        summarize_every: int = 10,
    ):
        self.conn            = db_conn
        self.index           = pinecone_index
        self.llm             = llm
        self.user_id         = user_id
        self.user_name       = user_name
        self.top_k           = top_k
        self.summarize_every = summarize_every
        self.buffer_k        = buffer_k

        # Short-term buffer: deque of {"role": "human"|"ai", "content": str}
        # max length = buffer_k exchanges * 2 messages each
        self._buffer: deque = deque(maxlen=buffer_k * 2)
        self._seed_buffer()

    # ------------------------------------------------------------------
    # Seed buffer from DB on startup
    # ------------------------------------------------------------------

    def _seed_buffer(self) -> None:
        """Load the last (buffer_k * 2) messages from SQLite into the buffer."""
        recent = load_recent_messages(
            self.conn, self.user_id, limit=self.buffer_k * 2
        )
        for msg in recent:
            self._buffer.append({"role": msg["role"], "content": msg["content"]})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_exchange(self, human_text: str, ai_text: str) -> None:
        """Add a completed exchange to the short-term buffer."""
        self._buffer.append({"role": "human", "content": human_text})
        self._buffer.append({"role": "ai",    "content": ai_text})

    def build_context(self, user_input: str) -> str:
        """
        Return a context string to inject into the system prompt.
        Includes retrieved long-term memories + recent short-term buffer.
        Called BEFORE the LLM responds.
        """
        parts = []

        # Long-term memories from Pinecone
        memories = retrieve_memories(
            self.index,
            user_id=str(self.user_id),
            query=user_input,
            top_k=self.top_k,
        )
        if memories:
            parts.append("=== LONG-TERM MEMORIES (from past sessions) ===")
            for i, mem in enumerate(memories, 1):
                parts.append(f"{i}. {mem}")
            parts.append("")

        # Short-term buffer
        if self._buffer:
            parts.append("=== RECENT CONVERSATION (this session) ===")
            for msg in self._buffer:
                role = "User" if msg["role"] == "human" else "Assistant"
                parts.append(f"{role}: {msg['content']}")
            parts.append("")

        return "\n".join(parts)

    def maybe_summarize(self) -> Optional[str]:
        """
        If there are >= SUMMARIZE_EVERY un-summarized messages, generate a
        summary, store in Pinecone, mark rows done. Returns summary or None.
        """
        if count_unsummarized(self.conn, self.user_id) < self.summarize_every:
            return None

        rows = get_unsummarized_messages(self.conn, self.user_id)
        if not rows:
            return None

        transcript = "\n".join(
            f"{'User' if r['role'] == 'human' else 'Assistant'}: {r['content']}"
            for r in rows
        )

        prompt   = SUMMARIZE_PROMPT.format(conversation=transcript)
        response = self.llm.invoke(prompt)
        summary  = response.content.strip()

        store_memory(self.index, user_id=str(self.user_id), summary=summary)
        mark_messages_summarized(self.conn, [r["id"] for r in rows])

        return summary

    def clear(self) -> None:
        """Wipe the in-memory buffer (SQLite and Pinecone stay intact)."""
        self._buffer.clear()
