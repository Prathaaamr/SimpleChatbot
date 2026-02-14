import os
from dotenv import load_dotenv
from typing import TypedDict, List
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

# =====================================================
# Load environment variables
# =====================================================
load_dotenv()

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY not found in environment")

# =====================================================
# Agent State
# =====================================================
class AgentState(TypedDict):
    messages: List[BaseMessage]

# =====================================================
# Groq LLM
# =====================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,
)

# =====================================================
# System Prompt (IMMUTABLE)
# =====================================================
SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are a helpful AI assistant. "
        "Maintain conversation context and answer follow-up questions correctly."
    )
)

# =====================================================
# Agent Node
# =====================================================
def agent_node(state: AgentState) -> AgentState:
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": state["messages"] + [response]}

# =====================================================
# LangGraph
# =====================================================
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.set_entry_point("agent")
graph.add_edge("agent", END)
app = graph.compile()

# =====================================================
# Run with MEMORY
# =====================================================
if __name__ == "__main__":
    chat_history: List[BaseMessage] = []

    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        chat_history.append(HumanMessage(content=user_input))

        result = app.invoke({"messages": chat_history})

        assistant_msg = result["messages"][-1]
        chat_history.append(assistant_msg)

        print(f"AI: {assistant_msg.content}\n")
