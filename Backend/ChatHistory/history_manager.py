import json
import os
import uuid

CHAT_PATH = "Data/ChatLog.json"


def load_chats():
    if not os.path.exists(CHAT_PATH):
        return []

    with open(CHAT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chats(data):
    with open(CHAT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def create_new_chat():

    chats = load_chats()

    new_chat = {
        "chat_id": str(uuid.uuid4()),
        "messages": []
    }

    chats.append(new_chat)
    save_chats(chats)

    return new_chat


def add_message(chat_id, role, content):

    chats = load_chats()

    for chat in chats:
        if chat["chat_id"] == chat_id:
            chat["messages"].append({
                "role": role,
                "content": content
            })

    save_chats(chats)
