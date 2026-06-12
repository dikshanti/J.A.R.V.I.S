import speech_recognition as sr
import pyttsx3
import subprocess
import datetime
import threading
import time
import pyautogui
import re
import os
import json
import pythoncom

# ---------- Configuration ----------
WAKE_WORD = "hey jarvis"
ACTIVE_MODE_SECONDS = 60
USE_TTS = True
COORD_FILE = "armoury_coords.json"
# -----------------------------------


def set_display_mode(mode):
    mode_map = {
        "duplicate": "/duplicate",
        "extend": "/extend",
        "second only": "/projector",
        "pc only": "/internal"
    }

    if mode not in mode_map:
        return False

    try:
        subprocess.run(
            f"displayswitch.exe {mode_map[mode]}",
            shell=True,
            check=True
        )
        return True
    except:
        return False


class ArmouryCrateController:

    def __init__(self, assistant):
        self.assistant = assistant

        self.ac_path = self._find_armoury_crate()

        self.coords = {
            "aura_tab": (350, 120),
            "static_btn": (600, 400),
            "color_picker": (800, 500),
            "apply_btn": (1500, 950),

            "fan_tab": (350, 180),
            "silent_mode": (600, 400),
            "performance_mode": (600, 500),
            "turbo_mode": (600, 600),

            "device_dropdown": (300, 200),

            "rainbow_btn": (700, 450),
            "breathing_btn": (800, 450)
        }

        self._load_coords()

        if not self.ac_path:
            self.assistant.speak(
                "Armoury Crate not found.",
            )

    def _find_armoury_crate(self):

        possible_paths = [
            r"C:\Program Files\ASUS\ARMOURY CRATE\ArmouryCrate.exe",
            r"C:\Program Files (x86)\ASUS\ARMOURY CRATE\ArmouryCrate.exe",
            r"C:\Program Files\ASUS\ARMOURY CRATE SE\ArmouryCrate.exe",
            r"C:\Program Files (x86)\ASUS\ARMOURY CRATE SE\ArmouryCrate.exe",
            os.path.expanduser(
                r"~\AppData\Local\Programs\ASUS\ARMOURY CRATE\ArmouryCrate.exe"
            ),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"[Armoury] Found: {path}")
                return path

        print("[Armoury] Not found")
        return None

    def _load_coords(self):
        if os.path.exists(COORD_FILE):
            try:
                with open(COORD_FILE, "r") as f:
                    self.coords.update(json.load(f))
            except:
                pass

    def launch_armoury_crate(self):

        if not self.ac_path:
            return False

        try:
            subprocess.Popen(self.ac_path)
            time.sleep(5)

            pyautogui.press("esc")
            time.sleep(1)

            return True

        except Exception as e:
            print(e)
            return False

    def set_rgb_color(self, color_name):

        rgb_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "yellow": (255, 255, 0),
            "purple": (255, 0, 255),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "pink": (255, 192, 203)
        }

        if color_name not in rgb_map:
            self.assistant.speak("Unknown color")
            return

        r, g, b = rgb_map[color_name]

        if not self.launch_armoury_crate():
            return

        pyautogui.click(self.coords["aura_tab"])
        time.sleep(1)

        pyautogui.click(self.coords["static_btn"])
        time.sleep(1)

        pyautogui.click(self.coords["color_picker"])
        time.sleep(0.5)

        pyautogui.write(str(r))
        pyautogui.press("tab")

        pyautogui.write(str(g))
        pyautogui.press("tab")

        pyautogui.write(str(b))
        pyautogui.press("enter")

        time.sleep(0.5)

        pyautogui.click(self.coords["apply_btn"])

        self.assistant.speak(f"RGB set to {color_name}")

    def set_fan_mode(self, mode):

        mode_map = {
            "silent": "silent_mode",
            "performance": "performance_mode",
            "turbo": "turbo_mode"
        }

        if mode not in mode_map:
            self.assistant.speak(
                "Fan mode can be silent performance or turbo"
            )
            return

        if not self.launch_armoury_crate():
            return

        pyautogui.click(self.coords["fan_tab"])

        time.sleep(1)

        pyautogui.click(self.coords[mode_map[mode]])

        time.sleep(0.5)

        pyautogui.click(self.coords["apply_btn"])

        self.assistant.speak(f"{mode} mode activated")


class JarvisAssistant:

    def __init__(self):

        pythoncom.CoInitialize()

        self.engine = pyttsx3.init()

        voices = self.engine.getProperty("voices")

        for voice in voices:
            if "zira" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

        self.engine.setProperty("rate", 185)
        self.engine.setProperty("volume", 1.0)

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 3000
        self.recognizer.dynamic_energy_threshold = True

        self.microphone = sr.Microphone()

        self.running = True

        self.active_mode = False
        self.active_until = 0

        self.timer = None

        self.ac_controller = ArmouryCrateController(self)

        self.adjust_for_ambient_noise()

    def speak(self, text):

        if not USE_TTS:
            print(f"Jarvis: {text}")
            return

        try:

            print(f"Jarvis: {text}")

            self.engine.stop()

            self.engine.say(text)

            self.engine.runAndWait()

        except Exception as e:
            print(f"TTS Error: {e}")

    def adjust_for_ambient_noise(self):

        print("Calibrating microphone...")

        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

        print(f"Ready. Say '{WAKE_WORD}'")

    def activate_mode(self):

        if self.timer:
            self.timer.cancel()

        self.active_mode = True

        self.active_until = (
            time.time() + ACTIVE_MODE_SECONDS
        )

        self.timer = threading.Timer(
            ACTIVE_MODE_SECONDS,
            self.deactivate_mode
        )

        self.timer.start()

        print("[ACTIVE MODE ON]")

    def deactivate_mode(self):

        self.active_mode = False

        self.timer = None

        print("[ACTIVE MODE OFF]")

    def listen_loop(self):

        with self.microphone as source:

            while self.running:

                try:

                    if self.active_mode:
                        print("\nListening (active)...")
                    else:
                        print("\nListening...")

                    audio = self.recognizer.listen(
                        source,
                        timeout=3,
                        phrase_time_limit=6
                    )

                    text = self.recognizer.recognize_google(
                        audio
                    ).lower()

                    print(f"> {text}")

                    # WAKE WORD
                    if WAKE_WORD in text:

                        command = text.split(
                            WAKE_WORD
                        )[-1].strip()

                        if command:

                            self.process_command(command)
                            self.activate_mode()

                        else:

                            self.speak("Yes Ma'am")

                            time.sleep(0.7)

                            self.activate_mode()

                            try:

                                print("Waiting for command...")

                                followup_audio = self.recognizer.listen(
                                    source,
                                    timeout=6,
                                    phrase_time_limit=8
                                )

                                followup = self.recognizer.recognize_google(
                                    followup_audio
                                ).lower()

                                print(f"> {followup}")

                                self.process_command(followup)

                                self.activate_mode()

                            except sr.WaitTimeoutError:
                                self.speak("Still listening")

                            except Exception as e:
                                print(f"Follow-up error: {e}")

                        continue

                    # ACTIVE MODE
                    if (
                        self.active_mode and
                        time.time() < self.active_until
                    ):

                        self.process_command(text)

                        self.activate_mode()

                except sr.WaitTimeoutError:
                    continue

                except sr.UnknownValueError:
                    continue

                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")

                except Exception as e:
                    print(f"Error: {e}")

    def process_command(self, cmd):

        if not cmd:
            return

        print(f"[DEBUG] {cmd}")

        # RGB
        if "rgb" in cmd or "aura" in cmd:

            match = re.search(
                r"(?:set\s+)?(?:rgb|aura)\s+(?:light\s+)?to\s+(\w+)",
                cmd
            )

            if not match:
                match = re.search(r"rgb\s+(\w+)", cmd)

            if match:
                color = match.group(1).lower()

                self.ac_controller.set_rgb_color(color)

                return

            self.speak(
                "Say set rgb to red"
            )

            return

        # FAN MODE
        if "fan mode" in cmd:

            match = re.search(
                r"(?:set\s+)?fan mode to (\w+)",
                cmd
            )

            if match:

                mode = match.group(1).lower()

                self.ac_controller.set_fan_mode(mode)

                return

        # DISPLAY
        if "display" in cmd:

            if "duplicate" in cmd:
                set_display_mode("duplicate")
                self.speak("Display duplicated")

            elif "extend" in cmd:
                set_display_mode("extend")
                self.speak("Display extended")

            elif "second screen" in cmd:
                set_display_mode("second only")
                self.speak("Second screen only")

            elif "pc only" in cmd:
                set_display_mode("pc only")
                self.speak("PC screen only")

            return

        # NOTEPAD
        if "open notepad" in cmd:

            subprocess.Popen("notepad.exe")

            self.speak("Opening notepad")

            return

        if "close notepad" in cmd:

            subprocess.call(
                "taskkill /f /im notepad.exe",
                shell=True
            )

            self.speak("Notepad closed")

            return

        # VS CODE
        if (
            "open vs code" in cmd or
            "visual studio code" in cmd or
            "vs code" in cmd
        ):

            possible_paths = [
                r"C:\Users\diksh\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                r"C:\Program Files\Microsoft VS Code\Code.exe",
                r"C:\Program Files (x86)\Microsoft VS Code\Code.exe"
            ]

            code_path = None

            for p in possible_paths:
                if os.path.exists(p):
                    code_path = p
                    break

            if code_path:

                subprocess.Popen([code_path])

                self.speak("Opening VS Code")

            else:

                try:
                    subprocess.Popen(
                        "code",
                        shell=True
                    )

                    self.speak("Opening VS Code")

                except:
                    self.speak("VS Code not found")

            return

        # CALCULATOR
        if "open calculator" in cmd:

            subprocess.Popen("calc.exe")

            self.speak("Opening calculator")

            return

        # BROWSER
        if "open browser" in cmd:

            subprocess.Popen(
                "start chrome",
                shell=True
            )

            self.speak("Opening browser")

            return

        # TIME
        if "time" in cmd:

            now = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            self.speak(now)

            return

        # WHO MADE YOU
        if "who made you" in cmd:

            self.speak(
                "You did. On this Asus machine."
            )

            return

    def run(self):

        self.speak("Jarvis online")

        self.listen_loop()


if __name__ == "__main__":

    assistant = JarvisAssistant()

    try:
        assistant.run()

    except KeyboardInterrupt:

        print("\nShutting down")

        assistant.running = False