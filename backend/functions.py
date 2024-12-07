import math
import struct
import wave
import structures


SAMPLE_RATE = 44100


# Functions

def num_samples(num_seconds: float) -> int:
    """
    Перевод секунд в количество сэмплов
    :param num_seconds: интервал времени, для которого считается количество семплов
    :return: количество семплов
    """
    return int(SAMPLE_RATE * num_seconds)


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


def play_sound(samples: list):
    """
    Проигрывает заданный набор семплов на звуковом устройстве
    """


def validate_params(params: dict):
    """
    Проверяет полноту и корректность словаря параметров синтеза
    """
    result = False
    return result


def save_preset(preset: dict):
    """
    Сохраняет заданный набор параметров синтеза в файл
    """


def load_preset(filename: str) -> dict:
    """
    Загружает набор параметров синтеза из файла
    """
    preset = {}
    return preset


def generate_sine_wave(freq: float, amp: float, duration: float) -> list:
    """
    Сгенерировать семплы синусоиды с заданной частотой и длительностью звучания
    :param freq: float > 0 частота в герцах
    :param amp: float (0..1) относительная амплитуда
    :param duration: float > 0 длительность в секундах:
    :return list: набор семплов
    """
    samples = []
    for sample_no in range(num_samples(duration)):
        samples.append(math.sin(2 * math.pi * freq * sample_no / SAMPLE_RATE))
    return samples


def modulate_amp(base: list, mod: list) -> list:
    """
    Модулирует базовый сигнал набором значений амплитуды
    """
    result = []
    return result


def mix(sets: list) -> list:
    """
    Смешивает заданные массивы семплов путем почленного суммирования
    """
    result = []
    return result


def test_mix():
    set_of_sample_lists1 = [[0, 0.1, 1, -0.1, -1], [1, 2, 4, 8, 16]]
    mixed_sets = mix(set_of_sample_lists1)
    if mixed_sets == [0, 0.2, 4, -0.8, -16]:
        print('SUCCESS')
    else:
        print('FAILURE')


def apply_envelope(samples: list, envelope: list) -> list:
    """
    Применяет заданную огибающую к набору семплов
    """
    result = []
    return result


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
