import math
import wave
import struct

SR = 44100


def write_wave(filename, samples):
    """
    Запись массива 16-битных сэмплов в режиме моно
    с частотой дискретизации SR в wav-файл
    """
    f = wave.open(filename, "w")
    f.setparams((1, 2, SR, len(samples), "NONE", ""))
    f.writeframes(b"".join(
        [struct.pack('<h', round(x * 32767)) for x in samples]))
    f.close()


def num_samples(num_seconds: float):
    """
    Перевод секунд в количество сэмплов
    :param num_seconds: интервал времени, для которого считается количество семплов
    :return: int количество семплов
    """
    return int(SR * num_seconds)


def generate_sine_wave(freq: int, duration: float):
    """ Сгенерировать семплы синусоиды с заданной частотой и длительностью звучания """
    samples = []
    for sample_no in range(int(num_samples(duration))):
        samples.append(math.sin(2 * math.pi * freq * sample_no / SR))
    return samples


samples = generate_sine_wave(220, 1)
write_wave("wave_test.wav", samples)