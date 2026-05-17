from Backend.Chatbot import ChatBot


def generate_ideas():

    ideas = ChatBot("""
    Generate 3 useful software project ideas
    Return as python list only
    """)

    try:
        return eval(ideas)
    except:
        return ["Build AI tool"]
