import tkinter as tk
from datetime import datetime
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import webbrowser
import time
import os
import subprocess
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Initialize speech engine
engine = pyttsx3.init()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Global variable for Selenium WebDriver
driver = None

# Function to greet the user
def greet_user():
    hour = datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"
    return f"{greeting} How can I help you, Darshan and Lohith?"

# Function to search on Chrome
def search_on_chrome(query):
    search_url = f"https://www.google.com/search?q={query}"
    speak(f"Searching for {query} on Google Chrome")
    webbrowser.open(search_url)

# Function to play Spotify song
def play_on_spotify(song_name):
    spotify_path = r"C:\Program Files\Google\Chrome\Application\chrome_proxy.exe"  # Update this path if needed
    os.startfile(spotify_path)
    time.sleep(2)
    subprocess.run(f'start spotify:search:{song_name}', shell=True)
    time.sleep(2)
    pyautogui.press('tab', presses=3)
    pyautogui.press('enter')
    speak(f"Playing {song_name} on Spotify")

# Function to play YouTube video
def play_youtube_video(query):
    global driver
    try:
        chrome_options = Options()
        chrome_options.add_argument("--log-level=3")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        search_url = f"https://www.youtube.com/results?search_query={query}"
        driver.get(search_url)
        time.sleep(2)
        video = driver.find_element("xpath", '//*[@id="video-title"]')
        video.click()
        speak(f"Playing {query} on YouTube")
    except Exception as e:
        speak(f"An error occurred: {str(e)}")
        if driver:
            driver.quit()

# Function to add message to chat interface
def add_message(frame, message, alignment):
    bubble = tk.Frame(frame, bg="#FFF", bd=0)
    color = "#D1F8E8" if alignment == "right" else "#E5E5E5"
    anchor = "e" if alignment == "right" else "w"
    justify = "right" if alignment == "right" else "left"
    msg_label = tk.Label(
        bubble, text=message, bg=color, fg="black", wraplength=450, justify=justify, font=("Arial", 12), padx=10, pady=5
    )
    msg_label.pack(anchor="w" if alignment == "left" else "e")
    bubble.pack(anchor=anchor, padx=10, pady=5, fill="x", expand=True)
    frame.update_idletasks()

# Function to handle commands
def handle_command(command, chat_frame):
    if "wikipedia" in command:
        query = command.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(query, sentences=2)
            response = f"According to Wikipedia: {result}"
        except Exception as e:
            response = f"Could not fetch data: {str(e)}"
    elif "play on spotify" in command:
        song_name = command.replace("play on spotify", "").strip()
        response = f"Playing {song_name} on Spotify."
        play_on_spotify(song_name)
    elif 'play' in query and 'youtube' in query:
        query = query.replace("play", "").replace("on youtube", "").strip()
        response = f"Playing {query} on YouTube."
        play_youtube_video(query)
    elif "search on chrome" in command:
        query = command.replace("search on chrome", "").strip()
        response = f"Searching {query} on Chrome."
        search_on_chrome(query)
    elif "time" in command:
        current_time = datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {current_time}."
    elif "exit" in command or "thank you" in command:
        response = "Thank you! Have a great day!"
        if driver:
            driver.quit()
        speak(response)
        exit()
    else:
        response = "Sorry, I didn't understand that."

    add_message(chat_frame, response, "left")
    speak(response)

# Function to process text commands
def process_text_command(entry, chat_frame):
    command = entry.get().strip().lower()
    if command:
        add_message(chat_frame, command, "right")
        handle_command(command, chat_frame)
    entry.delete(0, tk.END)

# Function to process voice commands
def process_voice_command(chat_frame):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("I'm listening. What would you like me to do?")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            add_message(chat_frame, command, "right")
            handle_command(command, chat_frame)
        except sr.UnknownValueError:
            response = "Sorry, I didn't catch that."
            add_message(chat_frame, response, "left")
            speak(response)
        except sr.RequestError:
            response = "Network error. Please check your connection."
            add_message(chat_frame, response, "left")
            speak(response)

# Function to create chat interface
def create_chat_interface():
    root = tk.Tk()
    root.title("Voice Learning Assistant")
    root.geometry("500x700")
    root.config(bg="#FFF")

    chat_canvas = tk.Canvas(root, bg="#FFF", highlightthickness=0)
    chat_frame = tk.Frame(chat_canvas, bg="#FFF")
    chat_scrollbar = tk.Scrollbar(root, command=chat_canvas.yview)
    chat_canvas.configure(yscrollcommand=chat_scrollbar.set)
    chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    chat_canvas.create_window((0, 0), window=chat_frame, anchor="nw")
    chat_frame.bind(
        "<Configure>", lambda event: chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
    )

    input_frame = tk.Frame(root, bg="#FFF")
    input_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)
    entry = tk.Entry(input_frame, font=("Arial", 14), bg="#F3F3F3", fg="#000", insertbackground="#000")
    entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5, pady=5)
    send_button = tk.Button(
        input_frame, text="Send", bg="#128C7E", fg="white", font=("Arial", 12),
        command=lambda: process_text_command(entry, chat_frame)
    )
    send_button.pack(side=tk.LEFT, padx=5)
    mic_button = tk.Button(
        input_frame, text="🎤", bg="#128C7E", fg="white", font=("Arial", 12),
        command=lambda: process_voice_command(chat_frame)
    )
    mic_button.pack(side=tk.LEFT, padx=5)

    welcome_message = greet_user()
    add_message(chat_frame, welcome_message, "left")
    root.mainloop()

if __name__ == "__main__":
    create_chat_interface()
