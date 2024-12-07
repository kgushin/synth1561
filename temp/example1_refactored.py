import math
import wave
import struct

SAMPLE_RATE = 44100


def write_wave(filename, samples):
    """
    Запись массива 16-битных сэмплов в режиме моно
    с частотой дискретизации SR в wav-файл
    """
    f = wave.open(filename, "w")
    f.setparams((1, 2, SAMPLE_RATE, len(samples), "NONE", ""))
    f.writeframes(b"".join(
        [struct.pack('<h', x) for x in samples]))
    f.close()


def num_samples(num_seconds: float) -> int:
    """
    Перевод секунд в количество сэмплов
    :param num_seconds: интервал времени, для которого считается количество семплов
    :return: количество семплов
    """
    return int(SAMPLE_RATE * num_seconds)


def generate_sine_wave(freq: int, duration: float):
    """ Сгенерировать семплы синусоиды с заданной частотой и длительностью звучания """
    samples = []
    for sample_no in range(num_samples(duration)):
        samples.append(math.sin(2 * math.pi * freq * sample_no / SAMPLE_RATE))
    return samples


def normalize(samples: list, bits_per_sample=16) -> list:
    """
    Нормализует значения семплов в соответствии с разрядностью звукового устройства
    :param samples: массив значений семплов
    :param bits_per_sample: разрядность звукового устройства
    :return: массив нормализованных значений (максимальное значение не превышает допустимого)
    """
    if abs(min(samples)) > max(samples):
        max_sample_value = abs(min(samples))
    else:
        max_sample_value = max(samples)
    if max_sample_value == 0:  # Массив семплов состоит из одних нулей
        return samples
    normalize_multiplier = (2 ** (bits_per_sample - 1) - 1) / max_sample_value
    normalized_samples = []
    for sample in samples:
        normalized_samples.append(int(sample * normalize_multiplier))
    return normalized_samples


samples = generate_sine_wave(220, 1)
write_wave("wave_test.wav", normalize(samples))