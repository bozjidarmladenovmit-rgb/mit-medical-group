"""Synthesises a short, warm musical ending ("sting") for the end card, in a given major key.
A soft string-like swell, two rising piano notes, then a full major chord that rings out.
    python3 src/sting.py C# 4.4 out.wav
"""
import sys, wave
import numpy as np

SR = 48000
NOTES = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
         'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

def hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)

def piano(f, dur, vel=1.0):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for k, amp in enumerate([1.0, 0.55, 0.32, 0.18, 0.1, 0.06], start=1):
        decay = 1.6 + 1.4 * k
        out += amp * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k) * t) * np.exp(-t * decay / 5.0)
    attack = np.minimum(t / 0.006, 1)
    return vel * out * attack

def pad(freqs, dur, attack=1.2):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for f in freqs:
        for d in (-0.003, 0.0, 0.003):  # slight detune = soft string ensemble
            out += np.sin(2 * np.pi * f * (1 + d) * t) + 0.3 * np.sin(2 * np.pi * 2 * f * (1 + d) * t)
    env = np.minimum(t / attack, 1) * np.exp(-np.maximum(t - attack, 0) * 0.15)
    return out * env / (3 * len(freqs))

def reverb(x):
    y = x.copy()
    for delay, gain in [(0.029, 0.5), (0.037, 0.45), (0.043, 0.4), (0.051, 0.35), (0.083, 0.3), (0.121, 0.22), (0.17, 0.15)]:
        d = int(delay * SR)
        z = np.zeros_like(x); z[d:] = x[:-d] * gain
        y += z
    return y

def add(buf, sig, at):
    i = int(at * SR); j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i]

def main(key='C#', total=4.4, out='sting.wav'):
    r = 60 + NOTES[key]          # tonic around middle C
    third, fifth = r + 4, r + 7
    buf = np.zeros(int(total * SR))
    add(buf, 0.35 * pad([hz(r - 12), hz(third - 12), hz(fifth - 12), hz(r)], total), 0.0)
    add(buf, 0.55 * piano(hz(fifth), 1.4), 0.25)                  # rising motif: 5th ...
    add(buf, 0.6 * piano(hz(r + 12), 1.4), 0.6)                   # ... to octave
    for m, v in [(r - 12, 0.6), (r, 0.5), (third, 0.45), (fifth, 0.45), (r + 12, 0.5), (third + 12, 0.25)]:
        add(buf, v * piano(hz(m), total - 1.0), 1.0)              # final major chord as the logo lands
    add(buf, 0.18 * piano(hz(r + 24), 2.5), 1.02)                 # small sparkle on top
    buf = reverb(buf)
    fade = np.ones_like(buf); n = int(0.9 * SR); fade[-n:] = np.linspace(1, 0, n)
    buf *= fade
    buf = 0.85 * buf / np.max(np.abs(buf))
    st = np.stack([buf, np.roll(buf, int(0.011 * SR)) * 0.97], axis=1)  # gentle stereo width
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3])
