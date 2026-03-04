from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents import create_nl2graph_agent
from agents import create_nl2sql_agent

router = APIRouter()

class AgentRequest(BaseModel):
    question: str

@router.post("/sql/agent")
async def query_sql_agent(request: AgentRequest):
    try:
        agent = create_nl2sql_agent()
        result = await agent.call_nl2sql_agent({"input": request.question})
        return {"response": result['messages'][-1].content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/graph/agent")
async def query_graph_agent(request: AgentRequest):
    try:
        agent = create_nl2graph_agent()
        result = await agent.call_nl2graphDB_agent({"input": request.question})
        return {"response": result['messages'][-1].content}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))