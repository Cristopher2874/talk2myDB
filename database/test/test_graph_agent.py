import asyncio
import logging
import re
import sys
import os
# Python packjage management seems odd, maybeother solutiuon?
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents import create_nl2graph_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_graph_queries():
    with open('database/test/graph_queries.sql', 'r') as f:
        content = f.read()

    parts = re.split(r'-- Question:\s*', content)
    questions = []
    for part in parts[1:]:
        lines = part.split('\n', 1)
        question = lines[0].strip()
        rest = lines[1] if len(lines) > 1 else ''
        match = re.search(r'(SELECT.*?);', rest, re.DOTALL)
        if match:
            query = match.group(1).strip() + ';'
            questions.append((question, query))

    # test each graphDB exaples
    agent = create_nl2graph_agent()
    for question, expected_query in questions:
        print(f"Question: {question}")
        print(f"Expected Query: {expected_query}")
        try:
            result = await agent.call_nl2graphDB_agent({"input": question})
            print(f"Agent Result: {result['output'][:500]}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_graph_queries())