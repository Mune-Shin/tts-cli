from typing import Optional
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

def play_wav_on_device(wav_path, device_name: Optional[str]=None, device_id: Optional[int]=None):
    # デバイスID優先
    if device_id is not None:
        selected_device = device_id
    elif device_name:
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if device_name.lower() in d['name'].lower() and d['max_output_channels'] > 0:
                selected_device = i
                break
        else:
            raise ValueError(f"デバイス '{device_name}' が見つかりません")
    else:
        selected_device = None  # デフォルト

    with wave.open(wav_path, 'rb') as wf:
        channels = wf.getnchannels()
        rate = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

        if channels == 2:
            audio = audio.reshape(-1, 2)

        print(f"Playing on device ID: {selected_device if selected_device is not None else 'Default'}")
        sd.play(audio, samplerate=rate, device=selected_device)
        sd.wait()

def list_output_devices():
    devices = sd.query_devices()
    for i, d in enumerate(devices):
        if d['max_output_channels'] > 0:
            print(f"[{i}] {d['name']}")

def main():
    parser = argparse.ArgumentParser(description="TTSを任意の出力デバイスに送信")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="読み上げるテキスト")
    group.add_argument("-l", "--list-devices", action="store_true", help="利用可能な出力デバイスを一覧表示")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-d", "--device", help="出力デバイス名（例：VB-Audio Virtual Cable）", default=None)
    group.add_argument("-D", "--device-id", type=int, help="出力デバイス番号", default=None)
    args = parser.parse_args()

    if args.list_devices:
        list_output_devices()
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        wav_path = tmp.name

    synthesize_to_wav(args.text, wav_path)
    play_wav_on_device(wav_path, args.device, args.device_id)
    os.remove(wav_path)

if __name__ == "__main__":
    main()
