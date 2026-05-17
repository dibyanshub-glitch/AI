from Backend.Chatbot import ChatBot
import json


def plan_project(prompt):

    ai_plan = ChatBot(f"""
    Create project plan JSON for:
    {prompt}

    Include:
    name
    language
    framework
    files
    dependencies
    """)

    try:
        return json.loads(ai_plan)
    except:
        return {
            "name": "AI_Project",
            "language": "python",
            "files": ["main.py"],
            "dependencies": []
        }
