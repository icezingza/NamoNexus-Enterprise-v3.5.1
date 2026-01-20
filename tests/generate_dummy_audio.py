import wave
import math
import struct
import os

def create_sine_wave(filename, duration=3.0, freq=440.0):
    """Creates a simple sine wave audio file for testing."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    
    print(f"🔊 Generating audio wave: {filename} ({duration}s)")
    
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        
        for i in range(n_samples):
            value = int(32767.0 * math.sin(2.0 * math.pi * freq * i / sample_rate))
            data = struct.pack('<h', value)
            w.writeframesraw(data)
            
    print(f"✅ Created dummy audio successfully!")

if __name__ == "__main__":
    os.makedirs("Audio test", exist_ok=True)
    create_sine_wave(os.path.join("Audio test", "test_sine.wav"))