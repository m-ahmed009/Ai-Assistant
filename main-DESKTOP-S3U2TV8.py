import sys
import os
import json
import threading
import subprocess
from asyncio import run
from time import sleep
from queue import Queue
from dotenv import dotenv_values

# Set up import paths
sys.path.append(os.path.dirname(__file__))

# UI and support functions
from Frontend.Graphics.Gui import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

# Backend modules
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import speechRecognization
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

# Constants and directories
DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]
subprocesses = []

# Setup temporary directory
TempDirPath = "Temp"
os.makedirs(TempDirPath, exist_ok=True)

def TempDirectoryPath(filename):
    return os.path.join(TempDirPath, filename)

def ensure_chatlog_exists():
    os.makedirs("Data", exist_ok=True)
    chatlog_path = "Data/Chatlog.json"
    if not os.path.exists(chatlog_path):
        with open(chatlog_path, "w", encoding="utf-8") as file:
            json.dump([], file)

def ShowDefaultChatIfNoChats():
    ensure_chatlog_exists()
    try:
        with open("Data/Chatlog.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        data = []

    if not data:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
            f.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
            f.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open("Data/Chatlog.json", 'r', encoding='utf-8') as file:
            content = file.read().strip()
            return json.loads(content) if content else []
    except (json.JSONDecodeError, FileNotFoundError):
        print("❗ Error: Invalid or missing Chatlog.json")
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        role = entry.get("role")
        content = entry.get("content")
        if role == "user":
            formatted_chatlog += f"{Username} : {content}\n"
        elif role == "assistant":
            formatted_chatlog += f"{Assistantname} : {content}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            data = file.read()
        if data.strip():
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(data)
    except Exception as e:
        print(f"❗ Error showing chat on GUI: {e}")

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

assistant_busy = False

def MainExecution(Query):
    global assistant_busy
    if assistant_busy:
        ShowTextToScreen(f"{Assistantname} : I'm processing your last command. Please wait.")
        TextToSpeech("I'm processing your last command. Please wait.")
        return
    
    assistant_busy = True
    try:
        SetAssistantStatus("Listening ...")
        Query = speechRecognization()    
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking ...")

        Decision = FirstLayerDMM(Query)
        print(f"\nDecision: {Decision}\n")

        G = any(i.startswith("general") for i in Decision)
        R = any(i.startswith("realtime") for i in Decision)

        Merged_query = " and ".join(
            " ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")
        )

        ImageExecution = False
        TaskExecution = False
        ImageGenerationQuery = next((i for i in Decision if "generate" in i), None)
        if ImageGenerationQuery:
            ImageExecution = True

        for queries in Decision:
            if not TaskExecution and any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

        if ImageExecution:
            try:
                with open(r"Frontend\Files\ImageGeneratoion.data", "w") as file:
                    file.write(f"{ImageGenerationQuery}, True")

                p1 = subprocess.Popen([
                    'python', r'Backend\ImageGeneration.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocesses.append(p1)
            except Exception as e:
                print(f"❗ Error starting ImageGeneration.py: {e}")

        if G and R or R:
            SetAssistantStatus("Searching ...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking...")
                    QueryFinal = Queries.replace("general", "").strip()
                    Answer = Chatbot(QueryModifier(QueryFinal))
                    break
                elif "realtime" in Queries:
                    SetAssistantStatus("Searching...")
                    QueryFinal = Queries.replace("realtime", "").strip()
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    break
                elif "exit" in Queries:
                    Answer = Chatbot(QueryModifier("Okay, Bye!"))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    os._exit(1)
                    return
        
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
    except Exception as e:
        print(f"❗ Error in MainExecution: {e}")
        ShowTextToScreen(f"{Assistantname} : Sorry, I couldn’t understand that.")
        TextToSpeech("Sorry, I couldn’t understand that.")
    finally:
        assistant_busy = False        

command_queue = Queue()

def FirstThread():
    while True:
        if GetMicrophoneStatus() == "True":
            command = speechRecognization()
            command_queue.put(command)
        elif "Available..." not in GetAssistantStatus(""):
            SetAssistantStatus("Available ...")
        sleep(0.1)

# def SecondThread():
#     GraphicalUserInterface()

def CommandExecutor():
    while True:
        if not command_queue.empty():
            command = command_queue.get()
            MainExecution(command)
        sleep(0.1)

# if __name__ == "__main__":
#     # threading.Thread(target=FirstThread, daemon=True).start()
#     threading.Thread(target=CommandExecutor, daemon=True).start()
#     # SecondThread()
if __name__ == "__main__":
    threading.Thread(target=FirstThread, daemon=True).start()
    threading.Thread(target=CommandExecutor, daemon=True).start()
    GraphicalUserInterface()