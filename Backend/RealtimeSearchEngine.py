from googlesearch import search
from groq import Groq
from json import load , dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

try:
    with open(r"Data\Chat.json", "r") as file:
        messages = load(file)
except:
    with open(r"Data\Chat.json", "w") as file:
        dump([], file)

def GoogleSearch(Querry):
    results = list(search(Querry, advanced=True, num_results=5))
    Answer = f"The search results for '{Querry}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnserModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatbot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"},
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-Time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data
    

def RealtimeSearchEngine(prompt):
    global SystemChatbot, messages

    with open(r"Data\Chat.json", "r") as file:
        messages = load(file)

    messages.append({"role": "user", "content": f"{prompt}"})

    SystemChatbot.append({"role": "system", "content": GoogleSearch(prompt)})

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatbot + [{"role": "system", "content": Information()}] + messages,
        max_tokens=2048,
        temperature=0.7,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    Answer = Answer.replace("</s>", "")

    messages.append({"role": "assistant", "content": Answer})

    with open(r"Data\Chat.json", "w") as file:
        dump(messages, file, indent=4)

    SystemChatbot.pop()
    return AnserModifier(Answer=Answer)

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Querry:")
        print(RealtimeSearchEngine(user_input))