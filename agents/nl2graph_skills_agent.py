import logging

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver

from database import DBConnection
from core import BaseAgent
from core import GRAPH_SCHEMA_DESCRIPTION_SKILLS
from core.skills_loader import SkillMiddleware

logger = logging.getLogger(__name__)

class NL2GraphAgent(BaseAgent):
    """Agent for natural language to PGQL translation and execution."""

    def __init__(self):
        super().__init__()
        self.agent_name = "nl2graph_agent"
        self.system_prompt = GRAPH_SCHEMA_DESCRIPTION_SKILLS
        self.tools.extend(SkillMiddleware.tools)
        self.agent = self.build_agent()

    def build_agent(self):
        """Build the agent with skill middleware"""
        from langchain.agents import create_agent
        return create_agent(
            model=self._client,
            tools=self.tools,
            system_prompt=self.system_prompt,
            name=self.agent_name,
            middleware=[SkillMiddleware()],
            checkpointer=InMemorySaver()
        )

    async def call_nl2graphDB_agent(self, input: dict) -> dict:
        """Process the input question by generating PGQL and executing it."""
        question = input.get("input", "")
        original_question = question
        if not question:
            return {"output": "No question provided."}

        max_attempts = 2
        generated_pgql = ''
        last_error = None

        for attempt in range(max_attempts):
            try:
                messages = [HumanMessage(content=question)]

                agent_input = {'messages': messages}
                config:RunnableConfig = {"configurable": {"thread_id": "1234"}}

                response = await self.agent.ainvoke(agent_input, config)
                generated_pgql = response['messages'][-1].content
                
                #TODO: Validate the generated query that the agent generated with a judge

                logger.info(f"GENERATED PGQL (attempt {attempt + 1}): {generated_pgql}")

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
                last_error = e
                if attempt < max_attempts - 1:
                    question = f"Original question: {original_question}\n\nYour previous query:\n{generated_pgql}\n\nhad a mistake that resulted in an error: {e}. Fix the mistakes and consider the examples provided to solve the user question."
                    logger.warning(f"Retrying due to error: {e}")

        return {"output": f"Error executing NL2Graph after {max_attempts} attempts: {str(last_error)}"}


def create_nl2graph_agent():
    """Instantiate to call"""
    return NL2GraphAgent()
