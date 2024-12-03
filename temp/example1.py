import math
import struct
import wave

SR = 44100

# Запись массива 16-битных сэмплов в режиме моно
# с частотой дискретизации SR в wav-файл
def write_wave(filename, samples):
  f = wave.open(filename, "w")
  f.setparams((1, 2, SR, len(samples), "NONE", ""))
  f.writeframes(b"".join(
    [struct.pack('<h', round(x * 32767)) for x in samples]))
  f.close()

# Перевод секунд в количество сэмплов
def sec(x):
  return SR * x
  
# Сумма синусоид, имеющих частоты, определенные в bank
def sines(bank, t):
  mix = 0
  for f in bank:
    mix += math.sin(2 * math.pi * f * t / SR)
  return mix

# DTMF-сигналы для цифр 1-9
DTMF = [
  [697, 1209], [697, 1336], [697, 1477],
  [770, 1209], [770, 1336], [770, 1477],
  [852, 1209], [852, 1336], [852, 1477]
]

samples = []

# Цикл по цифрам телефонного номера
for d in [3, 1, 1, 5, 5, 5, 2, 3, 6, 8]:
  for t in range(int(sec(0.05))):
    samples.append(0.5 * sines(DTMF[d - 1], t))
  for t in range(int(sec(0.05))):
    samples.append(0)

write_wave("dtmf.wav", samples)