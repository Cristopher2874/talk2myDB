import asyncio
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from agents import create_nl2sql_agent

async def test_sql_queries():
    # Bring test data from the queries file
    with open('database/test/relational_queries.sql', 'r') as f:
        content = f.read()

    # Split by -- Question:
    parts = re.split(r'-- Question:\s*', content)
    questions = []
    for part in parts[1:]:
        lines = part.split('\n', 1)
        question = lines[0].strip()
        rest = lines[1] if len(lines) > 1 else ''
        # Find the SELECT query to start
        match = re.search(r'(SELECT.*?);', rest, re.DOTALL)
        if match:
            query = match.group(1).strip() + ';'
            questions.append((question, query))
            
    agent = create_nl2sql_agent()
    for question, expected_query in questions:
        print(f"Question: {question}")
        print(f"Expected Query: {expected_query}")
        try:
            result = await agent.call_nl2sql_agent({"input": question})
            print(f"Agent Result: {result['output']}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_sql_queries())