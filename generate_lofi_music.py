import math
import random
import struct
import wave
import numpy as np

SAMPLE_RATE = 44100
BPM = 88
BEAT_DUR = 60.0 / BPM
BAR_DUR = BEAT_DUR * 4
TOTAL_DURATION = 50.0  # seconds
TOTAL_SAMPLES = int(SAMPLE_RATE * TOTAL_DURATION)

t = np.linspace(0, TOTAL_DURATION, TOTAL_SAMPLES, endpoint=False)
audio = np.zeros(TOTAL_SAMPLES, dtype=np.float32)

# --- 1. Chords Generator (E-piano / Rhodes vibe) ---
# Frequencies in Hz for chord progression
# Progression: Cmaj7 -> Am7 -> Dm7 -> G7 (2 beats each or 1 bar each)
chords = [
    [261.63, 329.63, 392.00, 493.88],  # Cmaj7
    [220.00, 261.63, 329.63, 392.00],  # Am7
    [293.66, 349.23, 440.00, 523.25],  # Dm7
    [196.00, 246.94, 293.66, 349.23],  # G7
]

num_bars = int(np.ceil(TOTAL_DURATION / BAR_DUR))

for bar in range(num_bars):
    bar_start_t = bar * BAR_DUR
    chord_freqs = chords[bar % len(chords)]

    # Play chord notes with slight arpeggiated strum and decaying envelope
    for idx, freq in enumerate(chord_freqs):
        note_start = bar_start_t + idx * 0.04
        if note_start >= TOTAL_DURATION:
            continue
        
        start_sample = int(note_start * SAMPLE_RATE)
        duration_samples = int(BAR_DUR * 0.9 * SAMPLE_RATE)
        end_sample = min(start_sample + duration_samples, TOTAL_SAMPLES)
        length = end_sample - start_sample
        if length <= 0:
            continue

        t_note = np.linspace(0, length / SAMPLE_RATE, length, endpoint=False)
        
        # Lo-fi pitch wobble (vibrato)
        wobble = 1.0 + 0.003 * np.sin(2 * np.pi * 4.5 * t_note)
        freq_wobble = freq * wobble
        
        # Warm Rhodes-like tone: fundamental + quiet 2nd & 3rd harmonics
        wave_signal = (
            0.6 * np.sin(2 * np.pi * freq_wobble * t_note) +
            0.25 * np.sin(2 * np.pi * 2 * freq_wobble * t_note) +
            0.15 * np.sin(2 * np.pi * 3 * freq_wobble * t_note)
        )
        
        # Envelope: quick attack, exponential decay
        env = np.exp(-1.8 * t_note)
        audio[start_sample:end_sample] += wave_signal * env * 0.18

# --- 2. Upbeat Lo-Fi Drum Loop (Kick, Snare, Hi-Hat) ---
total_beats = int(np.ceil(TOTAL_DURATION / BEAT_DUR))

for b in range(total_beats):
    beat_t = b * BEAT_DUR
    start_s = int(beat_t * SAMPLE_RATE)
    beat_in_bar = b % 4

    # Kick drum on beat 0 and beat 2.5
    kick_times = [0.0]
    if beat_in_bar == 2:
        kick_times.append(0.5)

    for k_off in kick_times:
        k_t = beat_t + k_off * BEAT_DUR
        if k_t < TOTAL_DURATION:
            ks = int(k_t * SAMPLE_RATE)
            dur = int(0.18 * SAMPLE_RATE)
            ke = min(ks + dur, TOTAL_SAMPLES)
            length = ke - ks
            if length > 0:
                tn = np.linspace(0, length / SAMPLE_RATE, length, endpoint=False)
                # Pitch sweep from 130 Hz down to 45 Hz
                freq_sweep = 130.0 * np.exp(-30 * tn) + 45.0
                kick_sig = np.sin(2 * np.pi * freq_sweep * tn) * np.exp(-12 * tn)
                audio[ks:ke] += kick_sig * 0.35

    # Snare / Rimshot on beats 1 and 3
    if beat_in_bar in [1, 3]:
        dur = int(0.15 * SAMPLE_RATE)
        se = min(start_s + dur, TOTAL_SAMPLES)
        length = se - start_s
        if length > 0:
            tn = np.linspace(0, length / SAMPLE_RATE, length, endpoint=False)
            tone = np.sin(2 * np.pi * 180 * tn) * np.exp(-25 * tn)
            noise = (np.random.rand(length) * 2 - 1) * np.exp(-20 * tn)
            snare_sig = (0.4 * tone + 0.6 * noise)
            audio[start_s:se] += snare_sig * 0.22

    # Hi-hat on 8th notes (0.0 and 0.5 beats)
    for h_off in [0.0, 0.5]:
        h_t = beat_t + h_off * BEAT_DUR
        if h_t < TOTAL_DURATION:
            hs = int(h_t * SAMPLE_RATE)
            dur = int(0.05 * SAMPLE_RATE)
            he = min(hs + dur, TOTAL_SAMPLES)
            length = he - hs
            if length > 0:
                tn = np.linspace(0, length / SAMPLE_RATE, length, endpoint=False)
                noise = (np.random.rand(length) * 2 - 1) * np.exp(-60 * tn)
                audio[hs:he] += noise * 0.08

# --- 3. Vinyl Crackle Noise & Soft Compression ---
crackle = (np.random.rand(TOTAL_SAMPLES) * 2 - 1) * 0.012
# Add random soft pops
pop_indices = np.random.choice(TOTAL_SAMPLES, size=150, replace=False)
crackle[pop_indices] += (np.random.rand(150) * 2 - 1) * 0.08

audio += crackle

# Soft limiter / Normalization
max_val = np.max(np.abs(audio))
if max_val > 0:
    audio = (audio / max_val) * 0.85

# Convert to 16-bit PCM WAV
audio_int16 = (audio * 32767).astype(np.int16)

out_file = "lofi_music.wav"
with wave.open(out_file, "w") as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(audio_int16.tobytes())

print(f"Generated upbeat lo-fi track: {out_file} ({TOTAL_DURATION}s)")
