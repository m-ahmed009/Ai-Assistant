from AppOpener import close, open as appopen
from webbrowser import open as webopen
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings
urllib3.disable_warnings()

# Configure retry strategy for requests
session = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET", "POST"]
)
session.mount('https://', HTTPAdapter(max_retries=retries))
session.mount('http://', HTTPAdapter(max_retries=retries))

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Common CSS classes for web scraping (if needed)
classes = [
    "zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", 
    "gsrt vk_bk FzvWSb YwPhnf", "pclqee",
    "tw-Data-text tw-text-small tw-ta", "IZ6rdc", 
    "05uR6d LTKOO", "vlzY6d", 
    "webanswers-webanswers_table_webanswers-table", 
    "dDoNo ikb48b gsrt", "sXLa0e", 
    "LWkfKe", "VQF4g", "qv3Wpe", 
    "kno-rdesc", "SPZz6b"
]

# User agent for web requests
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Initialize Groq client if API key is available
client = None
if GroqAPIKey:
    try:
        client = Groq(api_key=GroqAPIKey)
    except Exception as e:
        print(f"[red]Failed to initialize Groq client:[/red] {e}")

# Professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]

messages = []
username = os.environ.get("USERNAME", "User")
SystemChatbot = [{
    "role": "system", 
    "content": f"Hello, I'm {username}. You're a content writer. You have to write content like letter, codes, applications, essays, notes, songs, poem etc."
}]

def GoogleSearch(Topic):
    """Perform a Google search with fallback mechanism"""
    try:
        # Try direct URL approach first
        search_url = f"https://www.google.com/search?q={Topic}"
        webbrowser.open(search_url)
    except Exception as e:
        print(f"[red]Google search failed:[/red] {e}")
        # Ultimate fallback - just open Google
        webbrowser.open("https://www.google.com")

def Content(Topic):
    """Generate content using AI and save to a file"""
    if not client:
        print("[red]Groq client not initialized. Cannot generate content.[/red]")
        return False

    def OpenNotepad(File):
        """Open file in default text editor"""
        try:
            subprocess.Popen(['notepad.exe', File])
        except Exception as e:
            print(f"[red]Failed to open file:[/red] {e}")

    def ContentWriterAI(prompt):
        """Generate content using Groq AI"""
        messages.append({"role": "user", "content": prompt})
        
        try:
            completion = client.chat.completions.create(
                # model="mixtral-8x7b-32768",
                model="llama-3.3-70b-versatile",
                messages=SystemChatbot + messages,
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
            return Answer.replace("</s>", "")
        except Exception as e:
            print(f"[red]AI content generation failed:[/red] {e}")
            return None

    try:
        Topic = Topic.replace("Content", "").strip()
        ContentByAI = ContentWriterAI(Topic)
        
        if not ContentByAI:
            return False

        os.makedirs("Data", exist_ok=True)
        filename = f"Data/{Topic.lower().replace(' ', '')}.txt"
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
        
        OpenNotepad(filename)
        return True
    except Exception as e:
        print(f"[red]Content creation failed:[/red] {e}")
        return False

def YoutubeSearch(Topic):
    """Search YouTube with error handling"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={Topic}"
        webbrowser.open(search_url)
        return True
    except Exception as e:
        print(f"[red]YouTube search failed:[/red] {e}")
        return False

def PlayYoutube(query):
    """Play YouTube video with error handling"""
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return True
    except Exception as e:
        print(f"[red]Failed to play YouTube video:[/red] {e}")
        return False

def OpenApp(app):
    """Open application with multiple fallback methods"""
    try:
        # Try AppOpener first
        appopen(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"[yellow]AppOpener failed for {app}, trying alternative methods...[/yellow]")
        
        try:
            # Try direct web search
            search_url = f"https://www.google.com/search?q={app}"
            webbrowser.open(search_url)
            return True
        except Exception as e:
            print(f"[red]All methods failed to open {app}:[/red] {e}")
            return False

def CloseApp(app):
    """Close application with error handling"""
    try:
        if "chrome" not in app.lower():
            close(app, match_closest=True, output=False, throw_error=True)
        return True
    except Exception as e:
        print(f"[red]Failed to close {app}:[/red] {e}")
        return False


def System(command):
    """System controls with error handling"""
    try:
        command = command.lower()
        if command == "mute":
            keyboard.press_and_release("volume mute")
        elif command == "unmute":
            keyboard.press_and_release("volume mute")  # Toggle mute
        elif command == "volume_up":
            keyboard.press_and_release("volume up")
        elif command == "volume_down":
            keyboard.press_and_release("volume down")
        return True
    except Exception as e:
        print(f"[red]System command failed:[/red] {e}")
        return False

async def TranslateAndExecute(commands: list[str]):
    """Execute commands asynchronously with proper error handling"""
    funcs = []
    for command in commands:
        command = command.strip().lower()
        try:
            if command.startswith("open "):
                app = command[5:].strip()
                if app and app not in ["it", "file"]:
                    funcs.append(asyncio.to_thread(OpenApp, app))
            
            elif command.startswith("close "):
                app = command[6:].strip()
                if app:
                    funcs.append(asyncio.to_thread(CloseApp, app))
            
            elif command.startswith("play "):
                query = command[5:].strip()
                if query:
                    funcs.append(asyncio.to_thread(PlayYoutube, query))
            
            elif command.startswith("content "):
                topic = command[8:].strip()
                if topic:
                    funcs.append(asyncio.to_thread(Content, topic))
            
            elif command.startswith("google search "):
                query = command[14:].strip()
                if query:
                    funcs.append(asyncio.to_thread(GoogleSearch, query))
            
            elif command.startswith("youtube search "):
                query = command[15:].strip()
                if query:
                    funcs.append(asyncio.to_thread(YoutubeSearch, query))
            
            elif command.startswith("system "):
                cmd = command[7:].strip()
                if cmd:
                    funcs.append(asyncio.to_thread(System, cmd))
            
            else:
                print(f"[yellow]No handler for command: {command}[/yellow]")
        
        except Exception as e:
            print(f"[red]Error processing command '{command}':[/red] {e}")

    # Execute all functions concurrently
    if funcs:
        results = await asyncio.gather(*funcs, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                print(f"[red]Command execution error:[/red] {result}")
            elif result:
                yield result

async def Automation(commands: list[str]):
    """Main automation function"""
    try:
        async for result in TranslateAndExecute(commands):
            if result:
                print(f"[green]Command executed successfully[/green]")
        return True
    except Exception as e:
        print(f"[red]Automation failed:[/red] {e}")
        return False


if __name__ == "__main__":
    test_commands = [
        # "google search Python documentation",
        # "youtube search Python tutorials",
        # "close settings",
        # "google search Elon Musk",
        # "content application for leaving the country",
        # "play relaxing music",
        # "system volume_down",
        # "open facebook",
        # "open instagram",
    ]
    
    asyncio.run(Automation(test_commands))