import datetime
import os
import sys
import webbrowser
import pyttsx3
import requests
import speech_recognition as sr
import wolframalpha

# Replace with your actual WolframAlpha API App ID
WOLFRAM_APP_ID = "YOUR_WOLFRAMALPHA_APP_ID" 

class VoiceAssistant:
    def __init__(self):
        # Initialize Text-to-Speech Engine
        self.engine = pyttsx3.init()
        self.configure_voice()
        
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        
        # Initialize WolframAlpha Client
        try:
            self.wolfram_client = wolframalpha.Client(WOLFRAM_APP_ID)
        except Exception as e:
            print(f"WolframAlpha Init Error: {e}. Fallback systems will be used.")
            self.wolfram_client = None

        # Simple In-Memory Schedule/Reminders Store
        self.schedule = []

    def configure_voice(self):
        """Sets up clear, natural voice rates and paths."""
        voices = self.engine.getProperty('voices')
        # Index 0 is typically male, 1 is female. Adjust as preferred.
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 175)  # Natural speaking speed

    def speak(self, text):
        """Converts text output to spoken audio feedback."""
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Captures audio data from the microphone and converts it to text string."""
        with sr.Microphone() as source:
            print("\nListening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                print("Processing speech pattern...")
                query = self.recognizer.recognize_google(audio, language='en-US')
                print(f"User Said: {query}")
                return query.lower()
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                self.speak("I didn't quite catch that. Could you repeat it?")
                return ""
            except sr.RequestError:
                self.speak("My speech processing service appears to be offline.")
                return ""

    def process_command(self, command):
        """Core parsing matrix router matching intents to technical modules."""
        if not command:
            return "No command detected."

        # 1. Conversational Basics
        if any(greet in command for greet in ["hello", "hi", "hey", "wake up"]):
            response = "Hello! I am up and ready. How can I help you today?"
            self.speak(response)
            return response

        elif "how are you" in command:
            response = "I am operating at peak efficiency, thank you for checking in."
            self.speak(response)
            return response

        # 2. Scheduling & Time Management
        elif any(t_word in command for t_word in ["time", "what time is it"]):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}."
            self.speak(response)
            return response

        elif "schedule" in command or "reminder" in command:
            if "add" in command or "create" in command:
                # Basic string parsing snippet for a reminder
                item = command.replace("add to schedule", "").replace("add reminder", "").strip()
                if item:
                    self.schedule.append(item)
                    response = f"I've added '{item}' to your task list."
                else:
                    response = "What would you like me to add to your schedule?"
            else:
                if self.schedule:
                    response = "Here are your upcoming items: " + ", ".join(self.schedule)
                else:
                    response = "Your schedule is currently clear."
            self.speak(response)
            return response

        # 3. Web Navigation & Deep Web Search
        elif "search for" in command or "google" in command:
            search_query = command.replace("search for", "").replace("google", "").strip()
            url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(url)
            response = f"Opening browser results for {search_query}."
            self.speak(response)
            return response

        elif "open website" in command or "go to" in command:
            domain = command.replace("open website", "").replace("go to", "").strip()
            if not domain.startswith("http"):
                domain = "https://" + domain.replace(" ", "")
            webbrowser.open(domain)
            response = f"Navigating to {domain}."
            self.speak(response)
            return response

        # 4. Computational Queries & Weather (WolframAlpha Core Engine)
        else:
            if self.wolfram_client:
                try:
                    res = self.wolfram_client.query(command)
                    answer = next(res.results).text
                    self.speak(answer)
                    return answer
                except Exception:
                    # Fallback out of WolframAlpha formatting anomalies
                    return self.google_fallback_search(command)
            else:
                return self.google_fallback_search(command)

    def google_fallback_search(self, command):
        """Final safety layer if API limits are broken or calls fail."""
        response = "I couldn't calculate that directly, but I am pulling up search web options for you."
        self.speak(response)
        webbrowser.open(f"https://www.google.com/search?q={command}")
        return response

    def run(self):
        """Initial loop framework for standalone desktop application testing."""
        self.speak("Voice systems activated initialization complete.")
        while True:
            command = self.listen()
            if "exit" in command or "shutdown" in command or "stop" in command:
                self.speak("Shutting down engine matrix. Goodbye.")
                sys.exit()
            if command:
                self.process_command(command)

if __name__ == "__main__":
    assistant = VoiceAssistant()
    # Uncomment the line below to run exclusively as a local python desktop terminal app
    # assistant.run()