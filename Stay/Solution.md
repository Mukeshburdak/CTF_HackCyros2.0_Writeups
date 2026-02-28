# 🎧 CTF Writeup — Stay (Crypto)

> **"It says Stayyyy....."**

| Field | Details |
|-------|---------|
| **Challenge** | Stay |
| **Category** | Crypto |
| **File** | `chall.wav` |
| **Flag** | `cyros{m0R5E_Y0uR53Lf}` |

---

## 🧠 TL;DR

The audio file encodes **Morse code via frequency-shift keying (FSK)** — different tones represent dots and dashes rather than the classic beep/silence approach. Decode the frequencies → get Morse → get flag.

---

## 🔍 Analysis

### Step 1 — Identify the Encoding

Opening `chall.wav` in Audacity or inspecting it with Python reveals a ~14 second audio file. Looking at the **waveform alone won't help** — the amplitude stays roughly constant throughout.

The key insight: run a **spectrogram** to inspect frequency over time.

```python
import scipy.io.wavfile as wav
import numpy as np
from scipy import signal

rate, data = wav.read('chall.wav')
normalized = data.astype(float) / 32767.0

f, t, Sxx = signal.spectrogram(normalized, rate, nperseg=2048, noverlap=1536)
dominant_freq = f[np.argmax(Sxx, axis=0)]
```

### Step 2 — Spot the Frequencies

Three distinct frequency bands appear:

| Frequency | Meaning |
|-----------|---------|
| ~1206 Hz | **Dot** (`.`) |
| ~1335 Hz | **Dash** (`-`) |
| ~1486 Hz | Carrier / preamble (ignore) |
| <1000 Hz / silence | Gap |

### Step 3 — Decode Gap Timing

Silence duration encodes structure:

| Gap Duration | Meaning |
|-------------|---------|
| ~35 ms | Inter-symbol (same letter) |
| ~200–270 ms | Inter-letter |
| ~500+ ms | Inter-word |

### Step 4 — Extract Morse Sequence

Classifying each time window by dominant frequency and grouping by silence boundaries gives:

```
-- / ----- / .-. / ..... / . / -.-- / --- / ..- / .-. / ..... / ...-- / .-.. / ..-.
```

### Step 5 — Decode Morse → Flag

| Morse | Char | Note |
|-------|------|------|
| `--` | M | |
| `-----` | 0 | leet for **O** |
| `.-.` | R | |
| `.....` | 5 | leet for **S** |
| `.` | E | |
| `-.--` | Y | |
| `---` | O | |
| `..-` | U | |
| `.-.` | R | |
| `.....` | 5 | leet for **S** |
| `...--` | 3 | leet for **E** |
| `.-..` | L | |
| `..-.` | F | |

**Result:** `M0R5E_Y0uR53Lf` → **MORSE YOURSELF** 🎉

---

## 🚩 Flag

```
cyros{m0R5E_Y0uR53Lf}
```

---

## 🛠️ Solve Script

```python
import scipy.io.wavfile as wav
import numpy as np
from scipy import signal
from itertools import groupby

rate, data = wav.read('chall.wav')
normalized = data.astype(float) / 32767.0

# Spectrogram
f, t_spec, Sxx = signal.spectrogram(normalized, rate, nperseg=2048, noverlap=1536)
dt = t_spec[1] - t_spec[0]
dominant_freq = f[np.argmax(Sxx, axis=0)]

# Classify frequencies
def classify(freq):
    if freq < 1000:   return 'S'   # silence
    if freq < 1270:   return '.'   # dot  (~1206 Hz)
    if freq < 1400:   return '-'   # dash (~1335 Hz)
    return 'X'                     # carrier/preamble

classified = [classify(fr) for fr in dominant_freq]

# Group into runs
runs = [(k, len(list(v))) for k, v in groupby(classified)]

# Decode letters using gap timing
MORSE = {
    '.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F',
    '--.':'G','....':'H','..':'I','.---':'J','-.-':'K','.-..':'L',
    '--':'M','-.':'N','---':'O','.--.':'P','--.-':'Q','.-.':'R',
    '...':'S','-':'T','..-':'U','...-':'V','.--':'W','-..-':'X',
    '-.--':'Y','--..':'Z','-----':'0','.----':'1','..---':'2',
    '...--':'3','....-':'4','.....':'5','-....':'6','--...':'7',
    '---..':'8','----.':'9'
}

letters, current = [], []
tones = [(k, n) for k, n in runs if k != 'X']  # strip carrier

for i, (sym, count) in enumerate(tones):
    dur_ms = count * dt * 1000
    if sym == 'S':
        if dur_ms >= 400:            # word gap
            if current: letters.append(''.join(current)); current = []
            letters.append(' ')
        elif dur_ms >= 150:          # letter gap
            if current: letters.append(''.join(current)); current = []
    else:
        current.append(sym)

if current:
    letters.append(''.join(current))

decoded = ''.join(MORSE.get(l, l) for l in letters)
print(f"cyros{{{decoded}}}")
```

---

## 💡 Key Takeaways

- **Don't just look at amplitude** — FSK-encoded Morse hides in the frequency domain
- Always run a **spectrogram** on audio crypto challenges
- The flag itself is the hint: `M0R5E` = leet for **MORSE**

---

## 📦 Requirements

```bash
pip install scipy numpy
```
