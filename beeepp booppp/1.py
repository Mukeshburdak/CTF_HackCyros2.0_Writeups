import numpy as np
import wave

# Load audio
w = wave.open('chall.wav')
frames = w.readframes(w.getnframes())
sr = w.getframerate()
w.close()
data = np.frombuffer(frames, dtype=np.int16).astype(float)

# ── Step 1: Find silence boundaries to isolate each tone segment ──────────────
chunk_small = 100                          # 100-sample RMS windows
rms_arr = np.array([
    np.sqrt(np.mean(data[i:i+chunk_small]**2))
    for i in range(0, len(data) - chunk_small, chunk_small)
])

threshold = 500
silent = rms_arr < threshold

# Collect silent runs → derive tone segments between them
silent_runs = []
in_sil = False; start = 0
for i, s in enumerate(silent):
    if not in_sil and s:     start = i;  in_sil = True
    elif in_sil and not s:   silent_runs.append((start, i)); in_sil = False
if in_sil: silent_runs.append((start, len(silent)))

tone_segs = []
prev_end = 0
for sil_start, sil_end in silent_runs:
    if sil_start > prev_end:
        tone_segs.append((prev_end, sil_start))
    prev_end = sil_end
if prev_end < len(rms_arr):
    tone_segs.append((prev_end, len(rms_arr)))

# ── Step 2: Decode each tone segment as a DTMF digit ─────────────────────────
DTMF_MAP = {
    (697,1209):'1', (697,1336):'2', (697,1477):'3', (697,1633):'A',
    (770,1209):'4', (770,1336):'5', (770,1477):'6', (770,1633):'B',
    (852,1209):'7', (852,1336):'8', (852,1477):'9', (852,1633):'C',
    (941,1209):'*', (941,1336):'0', (941,1477):'#', (941,1633):'D',
}
rows = [697, 770, 852, 941]
cols = [1209, 1336, 1477, 1633]

dtmf_sequence = ''
for start_c, end_c in tone_segs:
    start_s = start_c * chunk_small
    end_s   = min(end_c * chunk_small, len(data))
    seg = data[start_s:end_s]
    if len(seg) < 512:
        continue

    # Analyse the middle portion for a clean, stable read
    mid  = len(seg) // 2
    alen = min(4096, len(seg))
    seg_mid = seg[mid - alen//2 : mid + alen//2]

    freqs = np.fft.rfftfreq(len(seg_mid), 1/sr)
    mag   = np.abs(np.fft.rfft(seg_mid * np.hanning(len(seg_mid))))

    def peak(f):
        m = mag[(freqs >= f-30) & (freqs <= f+30)]
        return m.max() if len(m) else 0

    best_row = max(rows, key=peak)
    best_col = max(cols, key=peak)
    dtmf_sequence += DTMF_MAP.get((best_row, best_col), '?')

print(f"[+] DTMF sequence ({len(dtmf_sequence)} digits): {dtmf_sequence}")

# ── Step 3: Decode digit string as variable-length ASCII decimal ──────────────
# Each ASCII value is stored as its decimal representation:
#   32-99  →  2 digits
#   100-127 → 3 digits
# Try all valid 2- or 3-digit groupings (only one valid parse exists).

def decode_ascii_decimal(s, pos=0, acc=''):
    if pos == len(s):
        yield acc
        return
    for length in (3, 2):                       # try 3-digit first
        if pos + length <= len(s):
            v = int(s[pos:pos+length])
            if 32 <= v <= 127:
                yield from decode_ascii_decimal(s, pos + length, acc + chr(v))

flag = next(
    d for d in decode_ascii_decimal(dtmf_sequence)
    if d.startswith('cyros{') and d.endswith('}')
)
print(f"[+] Flag: {flag}")