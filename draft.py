import tkinter as tk
from datetime import datetime
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import webbrowser
import time
import logging
import os

# Initialize speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Set speech rate
logging.basicConfig(level=logging.INFO, filename="assistant.log", format="%(asctime)s - %(message)s")

# Global stop event for wake word listener
stop_listening_event = threading.Event()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to handle commands
def handle_command(command, chat_frame):
    response = ""
    if "play " in command and "on youtube" in command:
        query = command.replace("play", "").replace("on youtube", "").strip()
        if not query:
            response = "Please specify a video or topic to search for on YouTube."
        else:
            response = f"Playing {query} on YouTube."
            pywhatkit.playonyt(query)
            time.sleep(2)  # Pause briefly to allow video to load

    elif "search" in command:
        query = command.replace("search", "").strip()
        if not query:
            response = "Please specify something to search for on the web."
        else:
            response = f"Searching the web for {query}."
            webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "search" in command and "on wikipedia" in command:
        query = command.replace("search", "").replace("on wikipedia", "").strip()
        if not query:
            response = "Please specify a topic to search on Wikipedia."
            print(response)  # Replace with your 'speak' function
            return

        try:
            summary = wikipedia.summary(query, sentences=3)
            response = f"According to Wikipedia: {summary}"
            print(response)  # Replace with your 'speak' function
        except wikipedia.exceptions.DisambiguationError as e:
            options = ', '.join(e.options[:3])
            response = f"Multiple results found on Wikipedia: {options}. Please specify further."
            print(response)  # Replace with your 'speak' function
        except wikipedia.exceptions.PageError:
            response = "No results found on Wikipedia. Please try a different topic."
            print(response)  # Replace with your 'speak' function
        except wikipedia.exceptions.WikipediaException as e:
            response = f"An error occurred while fetching Wikipedia data: {str(e)}"
            logging.error(f"Wikipedia Exception: {str(e)}")
            print(response)  # Replace with your 'speak' function

    elif "search" in command:
        query = command.replace("search", "").strip()
        if not query:
            response = "Please specify something to search for on the web."
        else:
            response = f"Searching the web for {query}."
            webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "hello" in command:
        response = "Hello! How can I assist you today?"

    elif 'time' in command:
        strTime = datetime.now().strftime("%H:%M:%S")
        response = f"The current time is {strTime}"

    elif 'open chrome' in command:
        codePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        response="opening chrome"
        os.startfile(codePath)

    elif 'open google' in command:
        response="opening google"
        webbrowser.open("https://www.google.com")

    elif 'open youtube' in command:
        response="opening youtube"
        webbrowser.open("https://www.youtube.com")

    else:
        response = "Sorry, I didn't understand that."

    # Log, display, and speak the response
    logging.info(f"Response: {response}")
    add_message(chat_frame, response, "left")
    speak(response)

# Function to process text commands
def process_text_command(entry, chat_frame):
    command = entry.get().strip()
    if command:
        add_message(chat_frame, command, "right")
        handle_command(command.lower(), chat_frame)
    entry.delete(0, tk.END)

# Function to process voice commands
def process_voice_command(chat_frame):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.pause_threshold = 1.5
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            command = recognizer.recognize_google(audio).lower()
            add_message(chat_frame, command, "right")
            handle_command(command, chat_frame)
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that. Please repeat.")
        except sr.RequestError:
            speak("Network error. Please check your connection.")
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Please try again.")

# Function to listen for the wake word
def listen_for_wake_word(chat_frame, wake_word="assistant"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("I am ready. Say my wake word to activate me.")
        while not stop_listening_event.is_set():
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                if wake_word in command:
                    add_message(chat_frame, f"Wake word detected: {wake_word}", "left")
                    speak("How can I help you?")
                    process_voice_command(chat_frame)
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                speak("Network error. Please check your connection.")

# Function to add a message bubble
def add_message(frame, message, alignment):
    bubble = tk.Frame(frame, bg="#FFF", bd=0)
    color = "#D1F8E8" if alignment == "right" else "#E5E5E5"
    anchor = "e" if alignment == "right" else "w"
    justify = "right" if alignment == "right" else "left"
    msg_label = tk.Label(
        bubble, text=message, bg=color, fg="black", wraplength=450, justify=justify, font=("Arial", 12), padx=10, pady=5
    )
    msg_label.pack(anchor=anchor)
    bubble.pack(anchor=anchor, padx=10, pady=5, fill="x", expand=True)
    frame.update_idletasks()

# Chat interface
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
    chat_frame.bind("<Configure>", lambda event: chat_canvas.configure(scrollregion=chat_canvas.bbox("all")))

    input_frame = tk.Frame(root, bg="#FFF")
    input_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)

    entry = tk.Entry(input_frame, font=("Arial", 14), bg="#F3F3F3", fg="#000", insertbackground="#000")
    entry.pack(side=tk.LEFT, fill="x", expand=True, padx=5, pady=5)

    send_button = tk.Button(
        input_frame, text="Send", bg="#128C7E", fg="white", font=("Arial", 12), command=lambda: process_text_command(entry, chat_frame)
    )
    send_button.pack(side=tk.LEFT, padx=5)

    mic_button = tk.Button(
        input_frame, text="🎤", bg="#128C7E", fg="white", font=("Arial", 12),
        command=lambda: threading.Thread(target=process_voice_command, args=(chat_frame,)).start()
    )
    mic_button.pack(side=tk.LEFT, padx=5)

    stop_button = tk.Button(
        input_frame, text="Stop Listening", bg="#FF0000", fg="white", font=("Arial", 12),
        command=stop_listening_event.set
    )
    stop_button.pack(side=tk.LEFT, padx=5)

    add_message(chat_frame, "Hello! Say 'Assistant' to get started.", "left")
    threading.Thread(target=listen_for_wake_word, args=(chat_frame,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    create_chat_interface()
