import asyncio

from .planner import plan_project
from .builder import build_structure
from .coder import generate_project_code
from .debugger import auto_debug
from .git_manager import init_git
from .memory import remember_project
from .dependency_installer import install_dependencies


async def developer_mode(prompt):

    # 1️⃣ PLAN PROJECT
    plan = plan_project(prompt)

    # 2️⃣ BUILD STRUCTURE
    root = build_structure(plan)

    # 3️⃣ GENERATE CODE
    await generate_project_code(plan, root)

    # 4️⃣ INSTALL DEPENDENCIES
    install_dependencies(plan, root)

    # 5️⃣ AUTO DEBUG
    await auto_debug(root)

    # 6️⃣ GIT INIT
    init_git(root)

    # 7️⃣ MEMORY SAVE
    remember_project(plan)

    return f"Developer Mode completed → {plan['name']}"
