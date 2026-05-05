<img width="232" height="150" alt="architecture" src="https://github.com/user-attachments/assets/cb7aee28-37d8-49fe-ae38-e193998def5b" />
# memorybot<svg viewBox="0 0 960 620" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace, 'Cascadia Code', 'Fira Code', monospace">
  <defs>
    <marker id="arrowBlue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#3b82f6"/>
    </marker>
    <marker id="arrowGreen" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#10b981"/>
    </marker>
    <marker id="arrowAmber" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#f59e0b"/>
    </marker>
    <marker id="arrowGray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
    </marker>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#00000044"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="960" height="620" fill="#0f1117"/>

  <!-- Title -->
  <text x="480" y="42" text-anchor="middle" font-size="20" font-weight="bold" fill="#e2e8f0">MemoryBot — Architecture</text>
  <text x="480" y="62" text-anchor="middle" font-size="12" fill="#64748b">Hybrid short-term buffer + long-term vector memory</text>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- LAYER LABELS                                                        -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <text x="26" y="168" font-size="10" fill="#475569" transform="rotate(-90,26,168)">UI LAYER</text>
  <text x="26" y="320" font-size="10" fill="#475569" transform="rotate(-90,26,320)">CHAIN LAYER</text>
  <text x="26" y="500" font-size="10" fill="#475569" transform="rotate(-90,26,500)">MEMORY LAYER</text>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- ROW 1: USER + STREAMLIT                                            -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->

  <!-- User bubble -->
  <circle cx="120" cy="148" r="34" fill="#1e293b" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <text x="120" y="143" text-anchor="middle" font-size="22">👤</text>
  <text x="120" y="162" text-anchor="middle" font-size="10" fill="#94a3b8">User</text>

  <!-- Arrow: User → Streamlit -->
  <line x1="156" y1="148" x2="218" y2="148" stroke="#3b82f6" stroke-width="1.8" marker-end="url(#arrowBlue)"/>
  <text x="187" y="141" text-anchor="middle" font-size="9" fill="#3b82f6">input</text>

  <!-- Streamlit box -->
  <rect x="222" y="116" width="160" height="64" rx="10" fill="#1e293b" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <text x="302" y="140" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🖥️ Streamlit</text>
  <text x="302" y="156" text-anchor="middle" font-size="10" fill="#94a3b8">app.py</text>
  <text x="302" y="170" text-anchor="middle" font-size="9" fill="#475569">st.session_state buffer</text>

  <!-- Arrow: Streamlit → reply (back to user) -->
  <line x1="222" y1="162" x2="156" y2="162" stroke="#10b981" stroke-width="1.8" marker-end="url(#arrowGreen)"/>
  <text x="187" y="177" text-anchor="middle" font-size="9" fill="#10b981">reply</text>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- ROW 2: MEMORYBOTCHAIN + CLAUDE                                     -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->

  <!-- Arrow: Streamlit → Chain -->
  <line x1="302" y1="180" x2="302" y2="232" stroke="#3b82f6" stroke-width="1.8" marker-end="url(#arrowBlue)"/>
  <text x="318" y="210" font-size="9" fill="#3b82f6">user_input</text>

  <!-- MemoryBotChain box -->
  <rect x="192" y="236" width="220" height="80" rx="10" fill="#172033" stroke="#3b82f6" stroke-width="2" filter="url(#shadow)"/>
  <text x="302" y="260" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">⛓️ MemoryBotChain</text>
  <text x="302" y="276" text-anchor="middle" font-size="10" fill="#94a3b8">chain.py</text>
  <text x="302" y="292" text-anchor="middle" font-size="9" fill="#475569">1. build_context() → system prompt</text>
  <text x="302" y="305" text-anchor="middle" font-size="9" fill="#475569">2. llm.invoke() → reply</text>

  <!-- Arrow: Chain → Claude -->
  <line x1="414" y1="276" x2="476" y2="276" stroke="#3b82f6" stroke-width="1.8" marker-end="url(#arrowBlue)"/>
  <text x="444" y="268" text-anchor="middle" font-size="9" fill="#3b82f6">messages[]</text>

  <!-- Claude box -->
  <rect x="480" y="244" width="180" height="64" rx="10" fill="#1e293b" stroke="#a78bfa" stroke-width="2" filter="url(#shadow)"/>
  <text x="570" y="268" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🤖 Claude</text>
  <text x="570" y="284" text-anchor="middle" font-size="10" fill="#94a3b8">ChatAnthropic</text>
  <text x="570" y="299" text-anchor="middle" font-size="9" fill="#475569">claude-3-5-haiku</text>

  <!-- Arrow: Claude → Chain (reply) -->
  <line x1="480" y1="292" x2="414" y2="292" stroke="#10b981" stroke-width="1.8" marker-end="url(#arrowGreen)"/>
  <text x="447" y="306" text-anchor="middle" font-size="9" fill="#10b981">content</text>

  <!-- Arrow: Chain reply → Streamlit -->
  <line x1="302" y1="236" x2="302" y2="180" stroke="#10b981" stroke-width="1.8" marker-end="url(#arrowGreen)"/>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- ROW 3: MEMORY MANAGER                                              -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->

  <!-- Arrow: Chain → MemoryManager -->
  <line x1="250" y1="316" x2="250" y2="378" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arrowAmber)"/>
  <text x="200" y="350" font-size="9" fill="#f59e0b">save + update</text>

  <!-- MemoryManager box -->
  <rect x="145" y="382" width="310" height="90" rx="10" fill="#1a1f2e" stroke="#f59e0b" stroke-width="2" filter="url(#shadow)"/>
  <text x="300" y="406" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🧠 MemoryManager</text>
  <text x="300" y="422" text-anchor="middle" font-size="10" fill="#94a3b8">memory_manager.py</text>
  <rect x="160" y="430" width="130" height="30" rx="6" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
  <text x="225" y="448" text-anchor="middle" font-size="9" fill="#93c5fd">Short-term Buffer</text>
  <text x="225" y="458" text-anchor="middle" font-size="8" fill="#475569">BufferWindowMemory k=6</text>
  <rect x="310" y="430" width="130" height="30" rx="6" fill="#1a3322" stroke="#10b981" stroke-width="1"/>
  <text x="375" y="448" text-anchor="middle" font-size="9" fill="#6ee7b7">Long-term Retrieval</text>
  <text x="375" y="458" text-anchor="middle" font-size="8" fill="#475569">Pinecone top_k=3</text>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- ROW 4: SQLITE + PINECONE + EMBEDDINGS                             -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->

  <!-- Arrow: MemoryManager → SQLite -->
  <line x1="200" y1="472" x2="160" y2="526" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrowGray)"/>

  <!-- SQLite box -->
  <rect x="60" y="530" width="150" height="64" rx="10" fill="#1e293b" stroke="#64748b" stroke-width="2" filter="url(#shadow)"/>
  <text x="135" y="554" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🗄️ SQLite</text>
  <text x="135" y="570" text-anchor="middle" font-size="10" fill="#94a3b8">database.py</text>
  <text x="135" y="584" text-anchor="middle" font-size="9" fill="#475569">users · messages</text>

  <!-- Arrow: MemoryManager → Pinecone -->
  <line x1="370" y1="472" x2="420" y2="526" stroke="#10b981" stroke-width="1.8" marker-end="url(#arrowGreen)"/>
  <text x="420" y="505" font-size="9" fill="#10b981">upsert</text>

  <!-- Pinecone box -->
  <rect x="390" y="530" width="170" height="64" rx="10" fill="#1e293b" stroke="#10b981" stroke-width="2" filter="url(#shadow)"/>
  <text x="475" y="554" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🌲 Pinecone</text>
  <text x="475" y="570" text-anchor="middle" font-size="10" fill="#94a3b8">vector_store.py</text>
  <text x="475" y="584" text-anchor="middle" font-size="9" fill="#475569">cosine · 384-dim vectors</text>

  <!-- Embedder box -->
  <rect x="630" y="530" width="200" height="64" rx="10" fill="#1e293b" stroke="#a78bfa" stroke-width="2" filter="url(#shadow)"/>
  <text x="730" y="554" text-anchor="middle" font-size="13" font-weight="bold" fill="#e2e8f0">🔢 Embeddings</text>
  <text x="730" y="570" text-anchor="middle" font-size="10" fill="#94a3b8">sentence-transformers</text>
  <text x="730" y="584" text-anchor="middle" font-size="9" fill="#475569">all-MiniLM-L6-v2 (local)</text>

  <!-- Arrow: Embedder → Pinecone -->
  <line x1="628" y1="562" x2="562" y2="562" stroke="#a78bfa" stroke-width="1.8" marker-end="url(#arrowGray)"/>
  <text x="595" y="554" text-anchor="middle" font-size="9" fill="#a78bfa">384-dim</text>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- SUMMARIZATION LOOP (dashed)                                        -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <rect x="680" y="300" width="200" height="70" rx="10" fill="#1a1a2e" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="6,3" filter="url(#shadow)"/>
  <text x="780" y="322" text-anchor="middle" font-size="11" font-weight="bold" fill="#fbbf24">⏱ Auto-Summarize</text>
  <text x="780" y="339" text-anchor="middle" font-size="9" fill="#94a3b8">every 10 messages →</text>
  <text x="780" y="352" text-anchor="middle" font-size="9" fill="#94a3b8">Claude writes summary →</text>
  <text x="780" y="365" text-anchor="middle" font-size="9" fill="#94a3b8">embedded → Pinecone</text>

  <!-- Arrow: Chain → Summarize trigger -->
  <line x1="660" y1="276" x2="738" y2="300" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrowAmber)"/>

  <!-- Arrow: Summarizer → Pinecone -->
  <line x1="780" y1="370" x2="650" y2="530" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arrowAmber)"/>

  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <!-- LEGEND                                                             -->
  <!-- ═══════════════════════════════════════════════════════════════════ -->
  <rect x="60" y="90" width="430" height="18" rx="4" fill="#0f1117"/>
  <line x1="65"  y1="99" x2="95"  y2="99" stroke="#3b82f6" stroke-width="1.8"/>
  <text x="100" y="103" font-size="10" fill="#64748b">request / response</text>
  <line x1="190" y1="99" x2="220" y2="99" stroke="#10b981" stroke-width="1.8"/>
  <text x="225" y="103" font-size="10" fill="#64748b">reply / retrieval</text>
  <line x1="310" y1="99" x2="340" y2="99" stroke="#f59e0b" stroke-width="1.8" stroke-dasharray="5,3"/>
  <text x="345" y="103" font-size="10" fill="#64748b">async / background</text>
</svg>

A chatbot that remembers everything across sessions — user preferences, past conversations, important facts  using a hybrid memory system (vector + structured).
