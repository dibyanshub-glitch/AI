import subprocess
import asyncio
from Backend.Chatbot import ChatBot


async def auto_debug(root):

    try:
        result = subprocess.run(
            ["python", f"{root}/main.py"],
            capture_output=True,
            text=True
        )

        if result.stderr:

            fix = await asyncio.to_thread(
                ChatBot,
                f"Fix this error:\n{result.stderr}"
            )

            with open(f"{root}/main.py", "w") as f:
                f.write(fix)

    except:
        pass
