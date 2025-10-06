import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from groq import Groq
import os
from dotenv import load_dotenv
from utils import get_response_from_llm


load_dotenv()

server_params = StdioServerParameters(
    command="uv",
    args=["run", "mcp_server.py"],
    env=None,
    )

async def main():

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:

            await session.initialize()

            tools_response = await session.list_tools()
            print("Available tools:", [t.name for t in tools_response.tools])

            query = "How to use publish a package with uv on gitlab"
            library = "uv"
            res = await session.call_tool("get_docs", arguments = {"query": query, "library": library})

            context = res.content
            user_prompt_with_context = f"Query: {query}, Context {context}"

            # LLM function to create a human readable response
            SYSTEM_PROMPT= """
            Answer ONLY using the provided context. If info is missing say you don't know.
            Keep every 'SOURCE:' line exactly; list sources at the end.
            """
            answer = get_response_from_llm(user_prompt=user_prompt_with_context, system_prompt=SYSTEM_PROMPT, model="openai/gpt-oss-20b")
            print("ANSWER: ", answer)

if __name__ == "__main__":
    asyncio.run(main())