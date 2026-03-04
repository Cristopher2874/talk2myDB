from langchain_core.messages import HumanMessage

from database import DBConnection
from core import BaseAgent
from core import GRAPH_SCHEMA_DESCRIPTION, GRAPH_FEW_SHOT_EXAMPLES

class NL2GraphAgent(BaseAgent):
    """Agent for natural language to PGQL translation and execution."""

    def __init__(self):
        super().__init__()
        self.agent_name = "nl2graph_agent"
        self.system_prompt = f"{GRAPH_SCHEMA_DESCRIPTION}\n\n" + "\n\n".join(
            f"Q: {ex['q']}\nPGQL:\n{ex['pgql']}" for ex in GRAPH_FEW_SHOT_EXAMPLES
        )
        self.agent = self._build_agent()

    async def call_nl2graphDB_agent(self, input: dict) -> dict:
        """Process the input question by generating PGQL and executing it."""
        question = input.get("input", "")
        if not question:
            return {"output": "No question provided."}

        try:
            messages = [HumanMessage(content=question)]

            agent_input = {'messages': messages}

            response = await self.agent.ainvoke(agent_input)
            generated_pgql = response['messages'][-1].content

            if generated_pgql.startswith("```"):
                lines = generated_pgql.split("\n")
                generated_pgql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            db_conn = DBConnection()

            with db_conn.get_connection() as conn:
                cols, rows = db_conn.execute_query(conn, generated_pgql)

            if not rows:
                return {"output": "Query executed successfully but returned no results."}

            result_lines = []
            for row in rows:
                row_data = ", ".join(f"{col}: {val}" for col, val in zip(cols, row))
                result_lines.append(row_data)

            return {"output": f"Graph Query Results:\n" + "\n".join(result_lines)}
        except Exception as e:
            return {"output": f"Error executing NL2Graph: {str(e)}"}


def create_nl2graph_agent():
    """Instantiate to call"""
    return NL2GraphAgent()