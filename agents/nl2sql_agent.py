from langchain_core.messages import HumanMessage

from database import DBConnection
from core import BaseAgent
from core import SQL_SCHEMA_DESCRIPTION, SQL_FEW_SHOT_EXAMPLES

class NL2SQLAgent(BaseAgent):
    """Agent for natural language to SQL translation and execution."""

    def __init__(self):
        super().__init__()
        self.agent_name = "nl2sql_agent"
        self.system_prompt = f"{SQL_SCHEMA_DESCRIPTION}\n\n" + "\n\n".join(
            f"Q: {ex['q']}\nSQL:\n{ex['sql']}" for ex in SQL_FEW_SHOT_EXAMPLES
        )
        self.agent = self._build_agent()

    async def call_nl2sql_agent(self, input: dict) -> dict:
        """Process the input question by generating SQL and executing it."""
        question = input.get("input", "")
        if not question:
            return {"output": "No question provided."}
        
        attempts= 0
        generated_sql = ''

        while(attempts <= 1):
            try:
                messages = [HumanMessage(content=question)]

                agent_input = {'messages': messages}

                response = await self.agent.ainvoke(agent_input)
                generated_sql = response['messages'][-1].content

                print(f"GENERATED SQL: {generated_sql}")

                if generated_sql.startswith("```"):
                    lines = generated_sql.split("\n")
                    generated_sql = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

                db_conn = DBConnection()

                with db_conn.get_connection() as conn:
                    cols, rows = db_conn.execute_query(conn, generated_sql)

                if not rows:
                    return {"output": "Query executed successfully but returned no results."}

                result_lines = []
                for row in rows:
                    row_data = ", ".join(f"{col}: {val}" for col, val in zip(cols, row))
                    result_lines.append(row_data)

                return {"output": f"Query Results:\n" + "\n".join(result_lines)}
            except Exception as e:
                if(attempts <=1):
                    question = f"Your previous query {generated_sql} had a mistake that resulted on an error: {e}. Fix the mistakes and consider the examples provided to solve the user question."
                else:
                    return {"output": f"Error executing NL2SQL: {str(e)}"}
            finally:
                attempts = attempts + 1


def create_nl2sql_agent():
    """Instantiate to call"""
    return NL2SQLAgent()