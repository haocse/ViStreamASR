#!/usr/bin/env python3
"""
Simple microphone test script that runs continuously until cancelled.
Tests microphone input and displays audio levels in real-time.
"""

import pyaudio
import numpy as np
import time
import sys
from datetime import datetime


def test_microphone():
    """Test microphone input with real-time level display."""
    print("🎤 Starting microphone test...")
    print("   Press Ctrl+C to stop")
    print()

    # Audio parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1  # Mono
    RATE = 44100  # 44.1kHz

    p = pyaudio.PyAudio()

    try:
        # Find and display input devices
        info = p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        
        print("Available audio input devices:")
        for i in range(num_devices):
            device = p.get_device_info_by_host_api_device_index(0, i)
            if device.get('maxInputChannels') > 0:
                print(f"  {i}: {device.get('name')}")
        print()

        # Open audio stream from default input device
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=None  # Use default
        )

        print("📊 Microphone levels (Ctrl+C to stop):")
        print()

        while True:
            try:
                # Read audio data
                data = stream.read(CHUNK, exception_on_overflow=False)

                # Convert to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)

                # Calculate RMS (Root Mean Square) - a measure of audio level
                rms = np.sqrt(np.mean(np.square(audio_data)))

                # Calculate decibel level (rough approximation)
                if rms > 0:
                    # Avoid log(0) and provide a simple dB conversion
                    db = 20 * np.log10(rms / 32768 * 100 + 1e-10)
                else:
                    db = -60  # Very quiet

                # Create visual bar
                bar_length = min(int((db + 60) * 2), 50)  # Scale to 0-50 characters
                bar = '█' * max(bar_length, 0)
                spaces = ' ' * max(50 - bar_length, 0)

                # Display timestamp and level
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"{timestamp} [{bar}{spaces}] {db:6.1f} dB", end='\r')

                time.sleep(0.05)  # Small delay to prevent CPU overload

            except IOError as e:
                if str(e).find('Input overflow'):
                    print("\n⚠️  Buffer overflow, discarding...")
                    time.sleep(0.1)
                    continue
                else:
                    raise
            except KeyboardInterrupt:
                break

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        print("\n\n🛑 Stopping microphone test...")
        try:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
        except:
            pass

    print("✅ Microphone test completed")
    return True


if __name__ == "__main__":
    test_microphone()