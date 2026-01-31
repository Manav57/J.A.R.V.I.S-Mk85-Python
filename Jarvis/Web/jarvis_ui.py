import eel
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import pyautogui
import os
import time
import datetime
import webbrowser
import pythoncom
import google.generativeai as genai

# --- 1. CONFIGURATION ---
# PASTE YOUR API KEY HERE
GOOGLE_API_KEY = "AIzaSyCKsA4Vdp7lLEhZ9HtU6jq8NTrIEFU26GM"

# --- 2. SETUP ---
if not os.path.exists("index.html"):
    print("ERROR: index.html missing!")
    exit()

try:
    eel.init('.')
except:
    eel.init('web')

# GLOBAL VARIABLES
engine = None
recognizer = sr.Recognizer()
mic = sr.Microphone()
chat_model = None


# --- 3. CONNECT BRAIN (SELF-HEALING) ---
def connect_brain():
    global chat_model
    try:
        genai.configure(api_key=GOOGLE_API_KEY)

        # LIST OF MODELS TO TRY (In order of speed/preference)
        candidate_models = [
            "gemini-2.0-flash",  # Try the newest first
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-pro",
            "gemini-flash-latest"
        ]

        for model_name in candidate_models:
            print(f"DEBUG: Testing model '{model_name}'...")
            try:
                model = genai.GenerativeModel(model_name)
                # FIRE A TEST SHOT to check for Quota/Limit errors
                response = model.generate_content("Hello")

                # If we get here, it WORKED!
                print(f"SUCCESS: '{model_name}' is working! Locking it in.")

                # Configure the Chat Session
                chat_model = model.start_chat(history=[
                    {"role": "user", "parts": ["You are Jarvis. If asked for code, provide it clearly."]},
                    {"role": "model", "parts": ["Yes Sir."]},
                ])
                print("DEBUG: Jarvis Brain is Active.")
                return  # Exit function, success!

            except Exception as e:
                # If it fails (404, 429, Limit 0), we just print and loop to the next one
                print(f"FAILED: '{model_name}' rejected. Reason: {e}")
                time.sleep(1)  # Wait a sec before retrying next

        # If loop finishes and nothing worked:
        print("CRITICAL ERROR: All models failed. Your API Key may be region-locked or invalid.")
        chat_model = None

    except Exception as e:
        print(f"DEBUG: Brain Connection Failed. Error: {e}")
        chat_model = None


# --- 4. VOICE OUTPUT ---
def speak(text):
    print(f"JARVIS: {text}")
    try:
        eel.js_print_terminal(text)
    except:
        pass
    try:
        eel.js_set_status("SPEAKING")
    except:
        pass

    try:
        pythoncom.CoInitialize()
        temp_engine = pyttsx3.init()
        temp_engine.setProperty('rate', 175)
        temp_engine.setProperty('volume', 1.0)
        temp_engine.say(text)
        temp_engine.runAndWait()
    except:
        pass

    try:
        eel.js_set_status("ONLINE")
    except:
        pass


# --- 5. HOLOGRAM PROJECTOR LOGIC (NEW) ---
def handle_ai_response(text):
    """Decides whether to Speak or Show the info"""

    # 1. DETECT CODE
    # Looks for code blocks, function definitions, imports, or HTML tags
    is_code = "```" in text or "def " in text or "import " in text or "class " in text or "<html>" in text

    # 2. DETECT STUDY MATERIAL / LISTS
    # Looks for bullet points (* or -) or numbered lists (1.) inside the text
    # AND checks if the text is long enough to be worth showing (> 250 chars)
    has_structure = ("\n*" in text or "\n-" in text or "\n1." in text)
    is_study_material = len(text) > 250 and has_structure

    # 3. DECISION: SHOW OR SPEAK?
    if is_code or is_study_material:
        print("DEBUG: Projecting to Hologram Screen...")
        eel.js_show_display(text)

        if is_code:
            speak("I have projected the code on your screen, Sir.")
        else:
            speak("I have projected the data on your screen for easier reading.")

    else:
        # PURE CONVERSATION (Voice Only)
        # Even if it is long, if it's just a story or speech, we just speak it.
        # We clean special characters so it sounds better.
        clean_text = text.replace("*", "").replace("#", "").replace("```", "")
        speak(clean_text)


# --- NEW MEDIA FEATURES (PHOTO/VIDEO/3D) ---
def show_media(command):
    # 1. PHOTOS (Uses Pollinations AI for instant results)
    if "photo" in command or "image" in command:
        query = command.replace("show", "").replace("me", "").replace("photo", "").replace("image", "").replace("of",
                                                                                                                "").strip()
        speak(f"Generating image of {query}...")

        # HTML for Image
        html = f"""<div style='text-align:center;'>
            <h2>VISUAL_DATA: {query.upper()}</h2>
            <img src='https://image.pollinations.ai/prompt/{query}' style='width:100%; border:2px solid #00f3ff; border-radius:10px;'>
        </div>"""
        eel.js_show_display(html)

    # 2. VIDEOS (Embeds YouTube)
    elif "video" in command:
        query = command.replace("show", "").replace("me", "").replace("video", "").replace("of", "").strip()
        speak(f"Pulling up video database for {query}...")

        # HTML for YouTube Embed
        html = f"""<div style='text-align:center;'>
            <h2>VIDEO_FEED: {query.upper()}</h2>
            <iframe width="100%" height="400" src="https://www.youtube.com/embed?listType=search&list={query}" frameborder="0" allowfullscreen></iframe>
        </div>"""
        eel.js_show_display(html)

    # 3. 3D MODELS (Embeds Sketchfab)
    elif "3d model" in command or "structure" in command:
        query = command.replace("show", "").replace("me", "").replace("3d model", "").replace("structure", "").replace(
            "of", "").strip()
        speak(f"Rendering 3D schematic of {query}...")

        # HTML for Sketchfab 3D Search Embed
        html = f"""<div style='text-align:center;'>
            <h2>3D_SCHEMATIC: {query.upper()}</h2>
            <p>Interactive Model Loading...</p>
            <iframe title="Sketchfab" width="100%" height="500" src="https://sketchfab.com/search?q={query}&type=models" frameborder="0" allow="autoplay; fullscreen; vr"></iframe>
        </div>"""
        eel.js_show_display(html)
# --- 6. ACTION LOGIC ---
def process_command(command):
    command = command.lower()

    # --- OFFLINE COMMANDS ---
    if "open" in command:
        name = command.replace("open", "").strip()
        speak(f"Opening {name}...")
        pyautogui.press('win')
        time.sleep(0.5)
        pyautogui.write(name)
        time.sleep(0.5)
        pyautogui.press('enter')

    elif "play" in command:
        if "youtube" in command:
            song = command.replace("play", "").replace("on youtube", "").strip()
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)
        else:
            pyautogui.press("playpause")
            speak("Media toggled.")

    elif "time" in command:
        t = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"It is {t}")

    elif "stop" in command:
        speak("Goodbye Sir.")
        os._exit(0)

    # --- TEST SCREEN COMMAND ---
    elif "test screen" in command:
        eel.js_show_display("SYSTEM VISUAL CHECK\n\n[OK] Hologram Interface\n[OK] Data Stream")
        speak("Visual interface check complete.")

    # --- ONLINE AI (Gemini) ---
    elif chat_model:
        try:
            speak("Thinking...")
            # Send message to Gemini
            response = chat_model.send_message(command)

            # USE THE NEW HANDLER INSTEAD OF JUST SPEAKING
            handle_ai_response(response.text)

        except Exception as e:
            print(f"API Error: {e}")
            speak("I am having trouble connecting to the brain.")
    else:
        speak("I am in offline mode.")


# --- 7. LISTENING LOOP ---
def jarvis_loop():
    # Wait for UI
    time.sleep(2)

    pythoncom.CoInitialize()
    connect_brain()
    speak("System Online.")

    while True:
        try:
            with mic as source:
                try:
                    eel.js_set_status("LISTENING")
                except:
                    pass

                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen for up to 5 seconds
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)

                try:
                    eel.js_set_status("PROCESSING")
                except:
                    pass

                command = recognizer.recognize_google(audio).lower()

                # Remove Wake Word
                command = command.replace("jarvis", "").replace("hey", "").strip()

                if command != "":
                    try:
                        eel.js_print_terminal(f"USER: {command}")
                    except:
                        pass
                    process_command(command)

        except Exception:
            pass


@eel.expose
def python_signal_ready():
    threading.Thread(target=jarvis_loop, daemon=True).start()


eel.start('index.html', size=(1280, 800))