import pyttsx3
import sounddevice as sd
import numpy as np
import argparse
import tempfile
import wave
import os

def synthesize_to_wav(text, wav_path):
    engine = pyttsx3.init()
    engine.save_to_file(text, wav_path)
    engine.runAndWait()

def play_wav_on_device(wav_path, device_name=None):
    with wave.open(wav_path, 'rb') as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

        if channels == 2:
            audio = audio.reshape(-1, 2)

        device_id = None
        if device_name:
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                if device_name.lower() in d['name'].lower() and d['max_output_channels'] > 0:
                    device_id = i
                    break
            if device_id is None:
                raise ValueError(f"デバイス '{device_name}' が見つかりません")

        sd.play(audio, samplerate=rate, device=device_id)
        sd.wait()

def main():
    parser = argparse.ArgumentParser(description="TTSを任意の出力デバイスに送信")
    parser.add_argument("text", help="読み上げるテキスト")
    parser.add_argument("--device", help="出力デバイス名（例：VB-Audio Virtual Cable）", default=None)
    args = parser.parse_args()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = tmp.name

    synthesize_to_wav(args.text, wav_path)
    play_wav_on_device(wav_path, args.device)
    os.remove(wav_path)

if __name__ == "__main__":
    main()
