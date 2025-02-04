import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import subprocess
import pyautogui

# Initialize text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def search_on_chrome(query):
    search_url = f"https://www.google.com/search?q={query}"
    speak(f"Searching for {query} on Google Chrome")
    webbrowser.open(search_url)

def greetUser():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning!")
    elif hour >= 12 and hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("How can i help you darshan and lohith?")

def play_on_spotify(song_name):
    # Open Spotify app
    spotify_path = r"C:\Program Files\Google\Chrome\Application\chrome_proxy.exe" # Update this path if needed
    os.startfile(spotify_path)
    time.sleep(2)  # Wait for the app to fully open

    # Search for the song in Spotify using URI scheme
    subprocess.run(f'start spotify:search:{song_name}', shell=True)
    time.sleep(2)  # Allow time for search to open

    # Simulate keyboard actions to play the first result
    pyautogui.press('tab', presses=3)  # Navigate to search results
    pyautogui.press('enter')  # Play the first song
    speak(f"Playing {song_name} on Spotify")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("How can I help?")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-UK')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Speak it again please...")
        return "None"
    return query

# Declare driver as a global variable
driver = None

def play_youtube_video(query):
    global driver  # Access the global driver variable

    # Set up Chrome options (optional)
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")  # Suppresses ChromeDriver logs

    # Initialize the Chrome driver with webdriver_manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Search and play the video on YouTube
    search_url = f"https://www.youtube.com/results?search_query={query}"
    driver.get(search_url)
    time.sleep(2)

    # Click on the first video result
    video = driver.find_element("xpath", '//*[@id="video-title"]')
    video.click()
    speak(f"Playing {query} on YouTube")

if __name__ == "__main__":
    greetUser()
    while True:
        query = takeCommand().lower()
        
        # Logic for executing tasks based on query
        if 'wikipedia' in query:
            speak('Searching in Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'play' in query and 'youtube' in query:
            query = query.replace("play", "").replace("on youtube", "")
            play_youtube_video(query)
        
        elif 'search' in  query:
            search_query = query.replace("search", "").replace("on chrome", "").strip()
            search_on_chrome(search_query)
            
        elif 'play' in query and 'spotify' in query:
          song_name = query.replace("play", "").replace("spotify", "").strip()
          play_on_spotify(song_name)

        elif 'pause youtube' in query or 'pause video' in query:
            if driver:
                driver.find_element("tag name", 'body').send_keys('k')  # 'k' key pauses/resumes YouTube video
                speak("Video paused.")

        elif 'resume youtube' in query or 'resume video' in query:
            if driver:
                driver.find_element("tag name", 'body').send_keys('k')
                speak("Video resumed.")

        elif 'stop youtube' in query or 'stop video' in query:
            if driver:
                driver.quit()
                driver = None
                speak("YouTube video stopped.")

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open university website' in query:
            webbrowser.open("https://newhorizoncollegeofengineering.in/")

        elif 'open stack overflow' in query or 'open stackoverflow' in query:
            speak("Here you go to Stack Overflow. Happy coding!")
            webbrowser.open("stackoverflow.com")


        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'open chrome' in query:
            codePath = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
            os.startfile(codePath)

        elif 'open git' in query:
            codePath = "C:\\Program Files\\Git\\git-bash.exe"
            os.startfile(codePath)

        elif 'thank you' in query or 'exit' in query:
            speak("Thanks for giving me your time")
            if driver:
                driver.quit()
            exit()
