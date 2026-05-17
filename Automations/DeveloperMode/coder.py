import asyncio
from Backend.Chatbot import ChatBot


async def generate_project_code(plan, root):

    for file in plan["files"]:

        prompt = f"""
        Write full production code for {file}
        Project language: {plan['language']}
        Framework: {plan.get('framework','none')}
        """

        code = await asyncio.to_thread(ChatBot, prompt)

        with open(f"{root}/{file}", "w", encoding="utf-8") as f:
            f.write(code)
