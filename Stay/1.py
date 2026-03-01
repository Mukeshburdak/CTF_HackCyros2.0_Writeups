import scipy.io.wavfile as wav
import numpy as np
from scipy import signal
from itertools import groupby
import base64

# --- Load & normalize ---
rate, data = wav.read('chall.wav')
normalized = data.astype(float) - 128.0  # uint8 center at 0

# --- Spectrogram & energy detection ---
f, t_spec, Sxx = signal.spectrogram(normalized, rate, nperseg=256, noverlap=230)
dt = t_spec[1] - t_spec[0]
energy = np.sum(Sxx, axis=0)
is_tone = energy > (np.max(energy) * 0.1)

# --- Build tone/silence runs ---
runs = [(k, sum(1 for _ in v)) for k, v in groupby(is_tone)]

# --- Morse code lookup ---
MORSE = {
    '.-':'A',  '-...':'B', '-.-.':'C', '-..':'D',  '.':'E',   '..-.':'F',
    '--.':'G', '....':'H', '..':'I',   '.---':'J', '-.-':'K', '.-..':'L',
    '--':'M',  '-.':'N',   '---':'O',  '.--.':'P', '--.-':'Q', '.-.':'R',
    '...':'S', '-':'T',    '..-':'U',  '...-':'V', '.--':'W',  '-..-':'X',
    '-.--':'Y','--..':'Z', '-----':'0','.----':'1','..---':'2','...--':'3',
    '....-':'4','.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
    '-...-':'='
}

# --- Decode Morse (include preamble dot as first symbol) ---
current_morse = []
letters = []

for is_t, count in runs:
    dur_ms = count * dt * 1000
    if is_t:
        current_morse.append('.' if dur_ms < 130 else '-')
    elif dur_ms > 100:          # letter boundary
        if current_morse:
            ms = ''.join(current_morse)
            letters.append(MORSE.get(ms, ms))
            current_morse = []

if current_morse:
    ms = ''.join(current_morse)
    letters.append(MORSE.get(ms, ms))

b32_string = ''.join(letters)
print(f"Morse decoded : {b32_string}")
# LEZWY6LCGNHDOYSUIJJU4VKWMZLVIQRRKVVFK6SUI5NDSRCRN46Q====

# --- Base32 decode ---
b64_string = base64.b32decode(b32_string)
print(f"Base32 decoded: {b64_string.decode()}")
# Y3lyb3N7bTBSNUVfWTB1UjUzTGZ9DQo=

# --- Base64 decode ---
flag = base64.b64decode(b64_string).decode().strip()
print(f"Flag: {flag}")
# cyros{m0R5E_Y0uR53Lf}