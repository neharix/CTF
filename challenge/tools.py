from django.conf import settings
from pydub import AudioSegment


def morse_to_mp3(text: str):
    morse_code = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        " ": " ",
        "{": "",
        "}": "",
    }

    morse_text = " ".join([morse_code.get(char.upper(), char) for char in text])

    base_dir = str(settings.BASE_DIR).replace("\\", "/")
    mp3 = AudioSegment.from_mp3(base_dir + "/main/static/sounds/nothing.mp3")
    short = AudioSegment.from_mp3(base_dir + "/main/static/sounds/short.mp3")
    long = AudioSegment.from_mp3(base_dir + "/main/static/sounds/long.mp3")
    nothing = AudioSegment.from_mp3(base_dir + "/main/static/sounds/nothing.mp3")
    for signal in morse_text:
        if signal == ".":
            mp3 += short
        elif signal == "-":
            mp3 += long
        elif signal == " ":
            mp3 += nothing

    mp3.export(base_dir + f"/media/morse_sounds/{text.replace("{", "").replace("}", "")}.mp3", format="mp3")
