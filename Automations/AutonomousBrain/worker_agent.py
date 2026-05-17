import asyncio
from Automations.DeveloperMode.brain import developer_mode


async def execute_task(task):

    if task["type"] == "build_project":

        result = await developer_mode(task["idea"])

        return result

