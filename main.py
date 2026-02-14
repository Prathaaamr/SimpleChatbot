import uvicorn
from fastapi import FastAPI
from langgraph.graph import StateGraph, END
from agent import AgentState, agent_node
from typing import TypedDict, List
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

app = FastAPI()

conversations = {}

@app.get("/")
def runAgent(user_input : str, session_id : str = "default"):
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    compiled_graph = graph.compile()

    if session_id not in conversations:
        conversations[session_id] = []
    
    conversations[session_id].append(HumanMessage(content=user_input))
    result = compiled_graph.invoke({"messages": conversations[session_id]})
    assistant_msg = result["messages"][-1]
    conversations[session_id].append(assistant_msg)
    
    return {"response": assistant_msg.content}

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)