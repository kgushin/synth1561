"""
Structures


# Кусочно-линейная огибающая
# Массив таплов (Tn, An),
#  где Tn -- момент времени (если значение отрицательное, отсчитывается от конца звучания)
#  An -- относительная амплитуда в этот момент времени
# Пример:
envelope = [
    (0,1)
]
"""


#Functions

def play_sound(samples: list):
    """
    Проигрывает заданный набор семплов на звуковом устройстве
    """


def validate_params(params: dict):
    """
    Проверяет полноту и корректность словаря параметров синтеза
    """
    return result


def save_preset(preset: dict):
    """
    Сохраняет заданный набор параметров синтеза в файл
    """


def load_preset(filename: str) -> dict:
    """
    Загружает набор параметров синтеза из файла
    """
    return preset


def modulate_amp(base: list, mod: list) -> list:
    """
    Модулирует базовый сигнал набором значений амплитуды
    """
    return result
set_of_sample_lists = []
def mix(sets: list) -> list:
    """
    Смешивает заданные массивы семплов путем почленного суммирования
    """

    return result

def test_mix():
    set_of_sample_lists1 = [[0, 0.1, 1, -0.1, -1], [1, 2, 4, 8, 16]]
    mixed_sets = mix(sets1)
    if mixed_sets == [0, 0.2, 4, -0.8, -16]:
        print('SUCCESS')
    else:
        print('FAILURE')

def apply_envelope(samples: list, envelope: list) -> list:
    """
    Применяет заданную огибающую к набору семплов
    """
    return result


def normalize(samples: list, bits_per_sample = 16) -> list:
    """
    Нормализует значения семплов в соответствии с разрядностью звукового устройства
    :param samples: массив значений семплов
    :return:
    """
    if abs(min(samples)) > max(samples):
        max_samples = abs(min(samples))
    else:
        max_samples = max(samples)
    normalize_multiplier = ( 2 ** (bits_per_sample - 1) - 1) / max_samples
    normalized_samples = []
    for sample in samples:
        normalized_samples.append(int(sample * normalize_multiplier))
    return normalized_samples
