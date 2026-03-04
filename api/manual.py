from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import DBConnection

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/sql/query")
async def execute_sql_query(request: QueryRequest):
    """Execute a manual SQL query."""
    try:
        db_conn = DBConnection()
        with db_conn.get_connection() as conn:
            cols, rows = db_conn.execute_query(conn, request.query)
        return {"columns": cols, "rows": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/graph/query")
async def execute_graph_query(request: QueryRequest):
    """Execute a manual PGQL query."""
    try:
        graph_conn = DBConnection()
        with graph_conn.get_connection() as conn:
            cols, rows = graph_conn.execute_pgql_query(conn, request.query)
        return {"columns": cols, "rows": rows}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))