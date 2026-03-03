import textwrap
from langchain_core.messages import HumanMessage

from core.base_agent import BaseAgent
from database.sql.connections import DBConnection

SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator. The user asks questions about
    the bank schema which contains:

      • BANK_ACCOUNTS(id, name, balance)
      • BANK_TRANSFERS(txn_id, src_acct_id, dst_acct_id, description, amount)

    Joins:
      BANK_TRANSFERS.src_acct_id = BANK_ACCOUNTS.id
      BANK_TRANSFERS.dst_acct_id = BANK_ACCOUNTS.id

    Return valid SQL only. Your output will be directly fed to the oracle database.
    dont include backquotes as they would interfere
    """
)

FEW_SHOT_EXAMPLES = [
    {
        "q": "How many accounts are there?",
        "sql": "SELECT COUNT(*) AS account_count FROM BANK_ACCOUNTS;",
    },
    {
        "q": "What is the total amount transferred?",
        "sql": "SELECT SUM(amount) AS total_amount FROM BANK_TRANSFERS;",
    },
    {
        "q": "Top 5 accounts by balance",
        "sql": (
            "SELECT name, balance\n"
            "FROM BANK_ACCOUNTS\n"
            "ORDER BY balance DESC FETCH FIRST 5 ROWS ONLY;"
        ),
    },
    {
        "q": "Accounts with more than 20 incoming transfers",
        "sql": (
            "SELECT a.name, COUNT(t.txn_id) AS incoming_transfers\n"
            "FROM BANK_ACCOUNTS a JOIN BANK_TRANSFERS t ON a.id = t.dst_acct_id\n"
            "GROUP BY a.name\n"
            "HAVING COUNT(t.txn_id) > 20\n"
            "ORDER BY incoming_transfers DESC;"
        ),
    },
]


class NL2SQLAgent(BaseAgent):
    """Agent for natural language to SQL translation and execution."""

    def __init__(self):
        super().__init__()
        self.agent_name = "nl2sql_agent"
        self.system_prompt = f"{SCHEMA_DESCRIPTION}\n\n" + "\n\n".join(
            f"Q: {ex['q']}\nSQL:\n{ex['sql']}" for ex in FEW_SHOT_EXAMPLES
        )
        self.agent = self._build_agent()

    async def call_nl2sql_agent(self, input: dict) -> dict:
        """Process the input question by generating SQL and executing it."""
        question = input.get("input", "")
        if not question:
            return {"output": "No question provided."}

        try:
            messages = [HumanMessage(content=question)]

            agent_input = {'messages': messages}

            response = await self.agent.ainvoke(agent_input)
            generated_sql = response['messages'][-1].content

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
            return {"output": f"Error executing NL2SQL: {str(e)}"}


def create_nl2sql_agent():
    """Instantiate to call"""
    return NL2SQLAgent()