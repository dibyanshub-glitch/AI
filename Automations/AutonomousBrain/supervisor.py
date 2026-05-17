import asyncio

from .idea_generator import generate_ideas
from .task_manager import create_tasks
from .worker_agent import execute_task
from .learning_agent import learn_from_result


async def run_autonomous_cycle():

    # 1️⃣ Generate AI ideas
    ideas = generate_ideas()

    # 2️⃣ Convert to tasks
    tasks = create_tasks(ideas)

    # 3️⃣ Execute tasks
    for task in tasks:
        result = await execute_task(task)
        learn_from_result(task, result)

    return "Autonomous cycle completed"
