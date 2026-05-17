from collections import deque

class ConversationMemory:
    def __init__(self, max_turns=8):
        self.history = deque(maxlen=max_turns)

    def add_user(self, text):
        self.history.append({"role": "user", "content": text})

    def add_assistant(self, text):
        self.history.append({"role": "assistant", "content": text})

    def get_context(self):
        return list(self.history)

    def clear(self):
        self.history.clear()
        
memory = ConversationMemory()