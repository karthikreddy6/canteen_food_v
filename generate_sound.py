import math
import struct
import wave
import os

os.makedirs('app/static/sounds', exist_ok=True)
sample_rate = 8000.0
frequency = 587.33 # D5 note (pleasant bell pitch)
num_samples = int(sample_rate * 0.8) # 0.8 seconds duration

with wave.open('app/static/sounds/bell.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(int(sample_rate))
    
    for i in range(num_samples):
        # Sine wave formula
        value = math.sin(2.0 * math.pi * frequency * (i / sample_rate))
        # Smooth decay envelope (fades out volume exponentially)
        decay = math.exp(-4.0 * (i / num_samples))
        sample = int(value * 32767.0 * decay)
        wav.writeframes(struct.pack('<h', sample))

print("Sound generated successfully at app/static/sounds/bell.wav")
