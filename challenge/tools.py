import random

from django.conf import settings
from pydub import AudioSegment


class Enigma:

    def __init__(self, ref, r1, r2, r3, key="AAA", plugs="", ring="AAA"):
        """Initialization of the Enigma machine."""
        self.reflector = ref
        self.rotor1 = r1
        self.rotor2 = r2
        self.rotor3 = r3

        self.rotor1.state = key[0]
        self.rotor2.state = key[1]
        self.rotor3.state = key[2]
        self.rotor1.ring = ring[0]
        self.rotor2.ring = ring[1]
        self.rotor3.ring = ring[2]
        self.reflector.state = "A"

        plugboard_settings = [(elem[0], elem[1]) for elem in plugs.split()]

        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        alpha_out = [" "] * 26
        for i in range(len(alpha)):
            alpha_out[i] = alpha[i]
        for k, v in plugboard_settings:
            alpha_out[ord(k) - ord("A")] = v
            alpha_out[ord(v) - ord("A")] = k

        self.transtab = str.maketrans(alpha, "".join(alpha_out))

    def encipher(self, plaintext_in):
        """Encrypt 'plaintext_in'."""
        ciphertext = ""
        plaintext_in_upper = plaintext_in.upper()
        plaintext = plaintext_in_upper.translate(self.transtab)
        for c in plaintext:
            # ignore non alphabetic char
            if not c.isalpha():
                ciphertext += c
                continue

            if self.rotor1.is_in_turnover_pos() and self.rotor2.is_in_turnover_pos():
                self.rotor3.notch()
            if self.rotor1.is_in_turnover_pos():
                self.rotor2.notch()

            self.rotor1.notch()

            t = self.rotor1.encipher_right(c)
            t = self.rotor2.encipher_right(t)
            t = self.rotor3.encipher_right(t)
            t = self.reflector.encipher(t)
            t = self.rotor3.encipher_left(t)
            t = self.rotor2.encipher_left(t)
            t = self.rotor1.encipher_left(t)
            ciphertext += t

        res = ciphertext.translate(self.transtab)

        fres = ""
        for idx, char in enumerate(res):
            if plaintext_in[idx].islower():
                fres += char.lower()
            else:
                fres += char
        return fres

    def __str__(self):
        """Pretty display."""
        return """
        Reflector: {}

        Rotor 1: {}

        Rotor 2: {}

        Rotor 3: {}""".format(
            self.reflector, self.rotor1, self.rotor2, self.rotor3
        )


class Reflector:
    """Represents a reflector."""

    def __init__(self, wiring=None, name=None, model=None, date=None):
        if wiring is not None:
            self.wiring = wiring
        else:
            self.wiring = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.name = name
        self.model = model
        self.date = date

    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def encipher(self, key):
        shift = ord(self.state) - ord("A")
        index = (ord(key) - ord("A")) % 26  # true index
        index = (index + shift) % 26  # actual connector hit

        letter = self.wiring[index]  # rotor letter generated
        out = chr(
            ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26
        )  # actual output
        # return letter
        return out

    def __eq__(self, rotor):
        return self.name == rotor.name

    def __str__(self):
        """Pretty display."""
        return """
        Name: {}
        Model: {}
        Date: {}
        Wiring: {}""".format(
            self.name, self.model, self.date, self.wiring
        )


class Rotor:
    """Represents a rotor."""

    def __init__(
        self,
        wiring=None,
        notchs=None,
        name=None,
        model=None,
        date=None,
        state="A",
        ring="A",
    ):
        """
        Initialization of the rotor.
        """
        if wiring is not None:
            self.wiring = wiring
        else:
            self.wiring = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.rwiring = ["0"] * 26
        for i in range(0, len(self.wiring)):
            self.rwiring[ord(self.wiring[i]) - ord("A")] = chr(ord("A") + i)
        if notchs is not None:
            self.notchs = notchs
        else:
            self.notchs = ""
        self.name = name
        self.model = model
        self.date = date
        self.state = state
        self.ring = ring

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "wiring":
            self.rwiring = ["0"] * 26
            for i in range(0, len(self.wiring)):
                self.rwiring[ord(self.wiring[i]) - ord("A")] = chr(ord("A") + i)

    def encipher_right(self, key):
        shift = ord(self.state) - ord(self.ring)
        index = (ord(key) - ord("A")) % 26  # true index
        index = (index + shift) % 26  # actual connector hit

        letter = self.wiring[index]  # rotor letter generated
        out = chr(
            ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26
        )  # actual output
        # return letter
        return out

    def encipher_left(self, key):
        shift = ord(self.state) - ord(self.ring)
        index = (ord(key) - ord("A")) % 26
        index = (index + shift) % 26
        # index = (index )%26
        letter = self.rwiring[index]
        # letter = chr((ord(self.rwiring[index]) -ord('A') + 26 -shift)%26+ord('A'))
        out = chr(ord("A") + (ord(letter) - ord("A") + 26 - shift) % 26)
        # return letter
        return out

    def notch(self, offset=1):
        self.state = chr((ord(self.state) + offset - ord("A")) % 26 + ord("A"))
        # notchnext = self.state in self.notchs
        # return notchnext

    def is_in_turnover_pos(self):
        return chr((ord(self.state) + 1 - ord("A")) % 26 + ord("A")) in self.notchs

    def __eq__(self, rotor):
        return self.name == rotor.name

    def __str__(self):
        """
        Pretty display.
        """
        return """
        Name: {}
        Model: {}
        Date: {}
        Wiring: {}
        State: {}""".format(
            self.name, self.model, self.date, self.wiring, self.state
        )


# 1924 Rotors
ROTOR_IC = Rotor(
    wiring="DMTWSILRUYQNKFEJCAZBPGXOHV",
    name="IC",
    model="Commercial Enigma A, B",
    date="1924",
)
ROTOR_IIC = Rotor(
    wiring="HQZGPJTMOBLNCIFDYAWVEUSRKX",
    name="IIC",
    model="Commercial Enigma A, B",
    date="1924",
)
ROTOR_IIIC = Rotor(
    wiring="UQNTLSZFMREHDPXKIBVYGJCWOA",
    name="IIIC",
    model="Commercial Enigma A, B",
    date="1924",
)


# German Railway Rotors
ROTOR_GR_I = Rotor(
    wiring="JGDQOXUSCAMIFRVTPNEWKBLZYH",
    name="I",
    model="German Railway (Rocket)",
    date="7 February 1941",
)
ROTOR_GR_II = Rotor(
    wiring="NTZPSFBOKMWRCJDIVLAEYUXHGQ",
    name="II",
    model="German Railway (Rocket)",
    date="7 February 1941",
)
ROTOR_GR_III = Rotor(
    wiring="JVIUBHTCDYAKEQZPOSGXNRMWFL",
    name="III",
    model="German Railway (Rocket)",
    date="7 February 1941",
)
ROTOR_GR_UKW = Reflector(
    wiring="QYHOGNECVPUZTFDJAXWMKISRBL",
    name="UTKW",
    model="German Railway (Rocket)",
    date="7 February 1941",
)
ROTOR_GR_ETW = Rotor(
    wiring="QWERTZUIOASDFGHJKPYXCVBNML",
    name="ETW",
    model="German Railway (Rocket)",
    date="7 February 1941",
)

# Swiss K Rotors
ROTOR_I_K = Rotor(
    wiring="PEZUOHXSCVFMTBGLRINQJWAYDK",
    name="I-K",
    model="Swiss K",
    date="February 1939",
)
ROTOR_II_K = Rotor(
    wiring="ZOUESYDKFWPCIQXHMVBLGNJRAT",
    name="II-K",
    model="Swiss K",
    date="February 1939",
)
ROTOR_III_K = Rotor(
    wiring="EHRVXGAOBQUSIMZFLYNWKTPDJC",
    name="III-K",
    model="Swiss K",
    date="February 1939",
)
ROTOR_UKW_K = Reflector(
    wiring="IMETCGFRAYSQBZXWLHKDVUPOJN",
    name="UKW-K",
    model="Swiss K",
    date="February 1939",
)
ROTOR_ETW_K = Rotor(
    wiring="QWERTZUIOASDFGHJKPYXCVBNML",
    name="ETW-K",
    model="Swiss K",
    date="February 1939",
)

# Enigma
ROTOR_I = Rotor(
    wiring="EKMFLGDQVZNTOWYHXUSPAIBRCJ",
    notchs="R",
    name="I",
    model="Enigma 1",
    date="1930",
)
ROTOR_II = Rotor(
    wiring="AJDKSIRUXBLHWTMCQGZNPYFVOE",
    notchs="F",
    name="II",
    model="Enigma 1",
    date="1930",
)
ROTOR_III = Rotor(
    wiring="BDFHJLCPRTXVZNYEIWGAKMUSQO",
    notchs="W",
    name="III",
    model="Enigma 1",
    date="1930",
)
ROTOR_IV = Rotor(
    wiring="ESOVPZJAYQUIRHXLNFTGKDCMWB",
    notchs="K",
    name="IV",
    model="M3 Army",
    date="December 1938",
)
ROTOR_V = Rotor(
    wiring="VZBRGITYUPSDNHLXAWMJQOFECK",
    notchs="A",
    name="V",
    model="M3 Army",
    date="December 1938",
)
ROTOR_VI = Rotor(
    wiring="JPGVOUMFYQBENHZRDKASXLICTW",
    notchs="AN",
    name="VI",
    model="M3 & M4 Naval(February 1942)",
    date="1939",
)
ROTOR_VII = Rotor(
    wiring="NZJHGRCXMYSWBOUFAIVLPEKQDT",
    notchs="AN",
    name="VII",
    model="M3 & M4 Naval(February 1942)",
    date="1939",
)
ROTOR_VIII = Rotor(
    wiring="FKQHTLXOCBJSPDZRAMEWNIUYGV",
    notchs="AN",
    name="VIII",
    model="M3 & M4 Naval(February 1942)",
    date="1939",
)

# misc & reflectors
ROTOR_Beta = Rotor(
    wiring="LEYJVCNIXWPBQMDRTAKZGFUHOS", name="Beta", model="M4 R2", date="Spring 1941"
)
ROTOR_Gamma = Rotor(
    wiring="FSOKANUERHMBTIYCWLQPZXVGJD", name="Gamma", model="M4 R2", date="Spring 1941"
)
ROTOR_Reflector_A = Reflector(wiring="EJMZALYXVBWFCRQUONTSPIKHGD", name="Reflector A")
ROTOR_Reflector_B = Reflector(wiring="YRUHQSLDPXNGOKMIEBFZCWVJAT", name="Reflector B")
ROTOR_Reflector_C = Reflector(wiring="FVPJIAOYEDRZXWGCTKUQSBNMHL", name="Reflector C")
ROTOR_Reflector_B_Thin = Reflector(
    wiring="ENKQAUYWJICOPBLMDXZVFTHRGS",
    name="Reflector_B_Thin",
    model="M4 R1 (M3 + Thin)",
    date="1940",
)
ROTOR_Reflector_C_Thin = Reflector(
    wiring="RDOBJNTKVEHMLFCWZAXGYIPSUQ",
    name="Reflector_C_Thin",
    model="M4 R1 (M3 + Thin)",
    date="1940",
)
ROTOR_ETW = Rotor(wiring="ABCDEFGHIJKLMNOPQRSTUVWXYZ", name="ETW", model="Enigma 1")


class Encryptor:
    def __init__(self):
        self.rotors = {
            "I": ROTOR_I,
            "II": ROTOR_II,
            "III": ROTOR_III,
            "IV": ROTOR_IV,
            "V": ROTOR_V,
            "VI": ROTOR_VI,
            "VII": ROTOR_VII,
        }
        self.reflectors = {
            "A": ROTOR_Reflector_A,
            "B": ROTOR_Reflector_B,
            "C": ROTOR_Reflector_C,
        }

        self.key = "ABC"
        self.ref = "A"
        self.r1 = "I"
        self.r2 = "II"
        self.r3 = "III"
        self.plugs = "AV BS CG DL FU HZ IN KM OW RX"

    def encrypt(self, message):

        engr = Enigma(
            self.reflectors[self.ref],
            self.rotors[self.r1],
            self.rotors[self.r2],
            self.rotors[self.r3],
            key=self.key,
            plugs=self.plugs,
        )
        return engr.encipher(message)


base_dir = str(settings.BASE_DIR).replace("\\", "/")


def text_to_morse(text):
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
    }

    morse_text = " ".join([morse_code.get(char.upper(), char) for char in text])

    return morse_text


def morse_to_mp3(morse_text, output_filename="output.mp3"):
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

    mp3.export(output_filename, format="mp3")


def morse_run(text: str, output_file: str):
    morse_text = text_to_morse(text)
    morse_to_mp3(morse_text, output_file)


def affine(text):
    a = random.randint(27, 99)
    b = random.randint(0, 25)
    plain = text
    cipher = ""
    for letter in plain:
        temp = chr((a * (ord(letter) - 97) + b) % 26 + 97)
        cipher += temp
    return cipher


import base64
import os
import struct
from binascii import hexlify


def xorstrings(a, b):
    result = b""
    for i in range(len(a)):
        result += struct.pack("B", (ord(a[i]) ^ ord(b[i])))
    return result


def one_time_pad(flag):
    a = "IN SUYJI DONDURMA TAGAMY SOKOLADYDYR"
    b = "IN GOWY DONDURMA TAGAMY YERTUDANADYR"
    p = flag

    aCipher = xorstrings(a, p)
    bCipher = xorstrings(b, p)

    return (
        aCipher.hex(),
        bCipher.hex(),
    )
