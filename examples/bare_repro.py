import asyncio
from os import getenv
from openai import AsyncOpenAI

async def main():
    client = AsyncOpenAI(base_url="https://api.deepseek.com", api_key=getenv("DEEPSEEK_API_KEY"))
    stream = await client.chat.completions.create(
        model="deepseek-chat", messages=[{"role": "user", "content": "hi"}], stream=True
    )
    async with stream:
        async for chunk in stream:
            pass
    await client.close()

asyncio.run(main())