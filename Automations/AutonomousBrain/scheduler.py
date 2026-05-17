import asyncio
from .supervisor import run_autonomous_cycle


async def autonomous_loop():

    while True:

        print("🤖 Autonomous AI thinking...")

        await run_autonomous_cycle()

        await asyncio.sleep(600)  # every 10 min
        
import Backend.state as state


async def autonomous_loop():

    while True:

        if state.AUTONOMOUS_MODE:
            await run_autonomous_cycle()

        await asyncio.sleep(600)
