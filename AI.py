import google.generativeai as genai
import assemblyai as aai
from pvrecorder import PvRecorder  # type: ignore[no-any-return]
import struct
import wave
import csv

genai.configure(api_key="AIzaSyBw9tX-VEuZIWegD1gVrv50CTzKCGZKm-Y")

path = "query.wav"
path_convo = "output_live_chat.mp3"

# AI functions


class Chat:
    def __init__(self):
        model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = model.start_chat(history=AI_context())

    def send_message(self, message):
        try:
            response = self.chat.send_message(message)
        except ValueError:
            return "Recording empty"
        AI_context(info=[message, response.text])  # Update the AI context
        return response.text


# AI context system, Get or add context
def AI_context(info=[]):
    if info != []:
        for i in range(len(info)):
            with open("AI_context.csv", "a", encoding="utf-8") as context_csv:
                writer = csv.DictWriter(context_csv, fieldnames=["role", "parts"])
                writer.writerow({"role": "model", "parts": info[i].strip("\n")})
        return True
    else:
        context = []
        with open("AI_context.csv", "r", encoding="utf-8") as context_csv:
            reader = csv.DictReader(context_csv, fieldnames=["role", "parts"])
            i = 0
            for row in reader:
                if i == 0:
                    i += 1
                else:
                    context.append(row)
        return context


def record_query(time):
    recorder = PvRecorder(device_index=-1, frame_length=512)
    audio = []
    recorder.start()
    while True:
        frame = recorder.read()
        audio.extend(frame)
        if len(audio) >= 16000 * time:
            break
    recorder.stop()
    with wave.open(path, "w") as f:
        f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
        f.writeframes(struct.pack("h" * len(audio), *audio))

    aai.settings.api_key = "fbb69376d32647e981881efae327b4d3"
    transcriber = aai.Transcriber()

    transcript = transcriber.transcribe("./query.wav")

    recorder.delete()
    return transcript.text


# Example chat
def live_chat(query=None, record=5):
    chat = Chat()
    ###
    if query == "EXIT":
        reset_context()
        return False
    ###
    elif query == "RESET":
        reset_context()
    ###
    elif "RECORD" in query:
        recording = record_query(record)
        ###
        response = chat.send_message(recording)
        if response == "Recording empty":
            return False
        return f"BOT: {response}"
    ###
    else:
        response = chat.send_message(query)
        return f"BOT: {response}"
        ###


# Reset the AI context when user leaves the page
def reset_context():
    with open("AI_context.csv", "w") as context_csv:
        writer = csv.DictWriter(context_csv, fieldnames=["role", "parts"])
        writer.writeheader()


# Get the chat log
def get_chat_log(count):
    messages_list = []
    context = AI_context()
    for message in context:
        if count % 2 == 0:
            if count == 0:
                count += 1
            else:
                txt = message["parts"]
                style, new_message = format_message(f"AI: {txt}")
                messages_list.append({style: new_message})
                count += 1
        else:
            txt = message["parts"]
            style, new_message = format_message(f"User: {txt}")
            messages_list.append({style: new_message})
            count += 1
    ###
    return messages_list
    ###


# format message
def format_message(message):
    style = ""
    new_message = ""
    if "AI" in message:
        style = "background-color: #50727B; text-align: left;"
    else:
        style = "background-color: #78A083; text-align: left;"
    new_message = message.replace("*", " ").replace(".", ".\n")
    return (style, new_message)


# read dicts
def read_dict(dict):
    dict_list = []
    for item in dict:
        dict_list.append(item)
    return dict_list
