import math
import struct
import wave
import json
import pprint
#import numpy
#import sounddevice

import logging
logger = logging.getLogger('')

#import structures


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
    samples = numpy.array(samples, dtype=numpy.int16)
    pprint.pprint(samples)
    sounddevice.play(samples)


def validate_params(params: dict):
    """
    Выполняет валидацию параметров синтеза
    """
    result = False
    return result


def prepare_params(frontend_data: dict) -> dict:
    """
    Подготавливает параметры синтеза для операции синтеза
    :param frontend_data: структура данных, полученная с фронтенда (в распакованном виде)
    :return: подготовленная структура synth_params
    """
    params = {}
    if 'drawflow' not in frontend_data:
        logger.fatal('Неверный формат входных данных: отсутствует раздел drawflow')
        return params
    if 'Home' not in frontend_data['drawflow']:
        logger.fatal('Неверный формат входных данных: отсутствует раздел drawflow/Home')
        return params
    if 'data' not in frontend_data['drawflow']['Home']:
        logger.fatal('Неверный формат входных данных: отсутствует раздел drawflow/Home/data')
        return params
    if not isinstance(frontend_data['drawflow']['Home']['data'], dict):
        logger.fatal('Неверный формат входных данных: drawflow/Home/data не является словарем')
        return params

    duration = 0
    params = {'tones':{}, 'effects':{}, 'duration':5}
    # Собираем списки тонов и эффектов
    for node_id, node_data in frontend_data['drawflow']['Home']['data'].items():
        match node_data['class']:
            case 'tone':
                params['tones'][node_id] = node_data['data']
                params['tones'][node_id]['type'] = node_data['class']
            case 'harmonic':
                params['tones'][node_id] = node_data['data']
                params['tones'][node_id]['type'] = node_data['class']
                params['tones'][node_id]['base'] = node_data['inputs']['input_1']['connections'][0]['node']
            case 'mixer':
                params['effects'][node_id] = node_data['data']
                params['effects'][node_id]['type'] = node_data['class']
                params['effects'][node_id]['input'] = []
                for input_data in node_data['inputs'].values():
                    for connection_data in input_data['connections']:
                        params['effects'][node_id]['input'].append(connection_data['node'])
                        # TODO one input can have multiple connections
                if len(node_data['inputs']) == 0:
                    logger.fatal("Не заданы входные соединения для узла " + node_id)
            case 'sounddevice':
                params['effects'][node_id] = node_data['data']
                params['effects'][node_id]['type'] = node_data['class']
                params['effects'][node_id]['input'] = node_data['inputs']['input_1']['connections'][0]['node']
            case _:
                logger.warning('Неизвестный тип узла: ' + node_data['class'] + ', id: ' + node_id)
    #return params

    # TODO Проверяем длительность
    '''
    if 'duration' not in frontend_data:
        logger.fatal('Не задан обязательный параметр: длительность')
        return params;
    else:
        params['duration'] = float(params['duration'])
        if params['duration'] < 0:
            logger.fatal('Недопустимое значение: длительность ' + params['duration'])
        if params['duration'] > 30:
            logger.warning('Возможно, слишком большое значение: длительность' + params['duration'])
    '''

    # Приводим тип всех параметров
    # Для гармоник явно определяем частоту
    for tone_id, tone_data in params['tones'].items():
        if 'freq' in tone_data:
            params['tones'][tone_id]['freq'] = float(tone_data['freq'])
        if 'amp' in tone_data:
            params['tones'][tone_id]['amp'] = float(tone_data['amp'])
        if 'phase' in tone_data:
            params['tones'][tone_id]['phase'] = float(tone_data['phase'])
        if tone_data['type'] == 'harmonic':
            factor = int(tone_data['factor'])
            base_id = tone_data['base']
            params['tones'][tone_id]['freq'] = float(params['tones'][base_id]['freq']) * int(tone_data['factor'])
            # TODO Log warning if frequency is too high

    return params


def save_preset(filename: str, preset: str):
    """
    Сохраняет конфигурацию конструктора в файл с заданным именем
    :param filename: имя файла
    :param preset: конфигурация конструктора (значения тонов и т.п; расположение блоков)
    """
    with open(filename, "wb") as f:
        f.write(preset.encode("utf-8"))


def list_presets(dirname: str='') -> list:
    """
    Возвращает список сохраненных пресетов
    """
    result = []
    return result


def load_preset(filename: str) -> str:
    """
    Загружает конфигурацию конструктора из файла с заданным именем
    :param filename: имя файла
    """
    with open(filename, "rb") as f:
        preset = f.read()
    return preset.decode("utf-8")

def generate_sine_wave(freq: float, duration: float, amp: float = 1, phase: float = 0) -> list:
    """
    Сгенерировать семплы синусоиды с заданными параметрами
    :param freq: float > 0 частота в герцах
    :param duration: float > 0 длительность в секундах:
    :param amp: float (0..1) относительная амплитуда
    :param phase: float (0..2*pi) сдвиг фазы
    :return list: набор семплов
    """
    samples = []
    for sample_no in range(num_samples(duration)):
        samples.append(amp * math.sin((2 * math.pi * freq * sample_no / SAMPLE_RATE) + phase))
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
    for idx in range(0, len(sets[0])):
        curr_sum = 0
        for curr_set in sets:
            if idx < len(curr_set):
                curr_sum += curr_set[idx]
        result.append(curr_sum)
    return result


def apply_envelope(samples: list, envelope: list) -> list:
    """
    Применяет заданную огибающую к набору семплов
    :param envelope: Список кортежей вида (Tn, An), упорядоченный по возрастанию Tn (Tn >= 0). Первый и последний
        кортеж в наборе соответствуют моменту времени (0) и окончанию звучания.
    """
    wave_time = len(samples) / 44100 #44100 = Sample Rate
    SaWAppEnv = [] #Samples with applied envelope
    segm_no = 1

    for sample_no in range(len(samples)):
        current_time = sample_no/44100
        if envelope[segm_no - 1][0] > current_time > envelope[segm_no][0]:
            if segm_no < len(envelope):
                segm_no += 1
        amplitude = (current_time - envelope[segm_no - 1][0]) * (envelope[segm_no][1] - envelope[segm_no - 1][1])\
            / (envelope[segm_no][0] - envelope[segm_no - 1][0])
        SaWAppEnv.append(samples[sample_no] * amplitude)
    return SaWAppEnv



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


def synthesize(params: dict) -> list:
    """
    """
    tone_samples = {}
    result = []
    for id, data in params['tones'].items():
        tone_samples[id] = generate_sine_wave(data['freq'],
                                              params['duration'],
                                              data['amp'],
                                              data['phase'])
    while len(result) == 0:
        for id, data in params['effects'].items():
            match data['type']:
                case 'mixer':
                    inputs_ready = True
                    for input_id in data['input']:
                        if input_id not in tone_samples.keys():
                            inputs_ready = False
                    if inputs_ready == True:
                        tone_samples[id] = []
                        for input_id in data['input']:
                            tone_samples[id] = mix([tone_samples[input_id], tone_samples[id]])
                case 'sounddevice':
                    if len(tone_samples[data['input']]) > 0:
                        result = tone_samples[data['input']]
    return result


def process_request(frontend_data: str):
    """
    Обработка запроса фронтенда
    """
    request_data = json.loads(frontend_data)
    params = prepare_params(request_data)
    if 'command' not in request_data:
        logger.fatal("Отсутствует необходимый параметр command")
        # TODO подумать, какие ошибки собираем в логгере и когда ловим исключения
    match request_data['command']:
        case 'save_preset':
            save_preset(frontend_data)
        case 'load_preset':
            load_preset('')
        case 'list_presets':
            list_presets()
        case 'check_params':
            prepare_params(request_data)
        case 'save_wav':
            params = prepare_params(request_data)
            samples = synthesize(params)
            write_wave('test.wav', normalize(samples))
    return False


#TODO установить numpy и sounddevice в виртуальное окружение и раскомментить соответствующие импорты в начале файла