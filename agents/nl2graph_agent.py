import textwrap
from langchain_core.messages import HumanMessage

from core.base_agent import BaseAgent
from database.sql.connections import DBConnection


GRAPH_SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator for property graphs. The user asks questions about
    the BANK_GRAPH schema, which contains bank accounts and transfers:

    Nodes (Vertices):
      • BANK_ACCOUNTS(id, name, balance)

    Relationships (Edges):
      • BANK_TRANSFERS(src_acct_id, dst_acct_id, amount)

    The graph represents bank transfers between accounts, where each transfer has a source account, destination account, and amount.

    Use graph_table function with PGQL MATCH syntax for queries. Always return valid SQL only. Your output will be directly fed to the Oracle database.
    Do not include backquotes.
    """
)

GRAPH_FEW_SHOT_EXAMPLES = [
    {
        "q": "How many accounts are there?",
        "pgql": "SELECT COUNT(*) FROM graph_table (BANK_GRAPH MATCH (a) COLUMNS (a.id))",
    },
    {
        "q": "What is the total amount transferred?",
        "pgql": "SELECT SUM(amount) FROM graph_table (BANK_GRAPH MATCH (src) -[e IS BANK_TRANSFERS]-> (dst) COLUMNS (e.amount AS amount))",
    },
    {
        "q": "Top 5 accounts by number of incoming transfers",
        "pgql": (
            "SELECT id, name, COUNT(*) AS incoming_transfers\n"
            "FROM graph_table (BANK_GRAPH MATCH (src) -[e IS BANK_TRANSFERS]-> (a) COLUMNS (a.id AS id, a.name AS name))\n"
            "GROUP BY id, name\n"
            "ORDER BY incoming_transfers DESC FETCH FIRST 5 ROWS ONLY"
        ),
    },
    {
        "q": "Which accounts received transfers from account 387 in 1 to 3 hops?",
        "pgql": (
            "SELECT DISTINCT id, name\n"
            "FROM graph_table (BANK_GRAPH MATCH (src) -[IS BANK_TRANSFERS]->{1,3} (a) WHERE src.id = 387 COLUMNS (a.id AS id, a.name AS name))"
        ),
    },
]


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