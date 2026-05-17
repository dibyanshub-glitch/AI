import re

def extract_whatsapp_details(command: str):
    name_match = re.search(r"send message to (\w+)", command)
    msg_match = re.search(r"saying (.+)", command)

    name = name_match.group(1) if name_match else None
    message = msg_match.group(1) if msg_match else "Hello"

def extract_whatsapp_details(command: str):
    command = command.lower()

    if "send message" in command:
        return {
            "action": "send_message",
            "name": "ankit",
            "message": "hello"
        }

    if "create project" in command:
        return {
            "action": "create_project",
            "project": "mywebsite"
        }

    if "write code" in command:
        return {
            "action": "write_code",
            "prompt": command
        }

    return {
        "action": "chat",
        "text": command
    }

