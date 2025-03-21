import math
import struct
import wave
import json
import pprint
import numpy
import ast
import sounddevice


SAMPLE_RATE = 44100


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
    (используется только при вызове через backend_cli)
    """
    samples = numpy.array(samples, dtype=numpy.int16)
    silence = numpy.zeros(100, dtype=numpy.int16)
    samples = numpy.concatenate((samples, silence))
    sounddevice.play(samples, blocking=True)


def prepare_params(frontend_data: dict) -> tuple:
    """
    Подготавливает параметры синтеза для операции синтеза
    :param frontend_data: структура данных, полученная с фронтенда (в распакованном виде)
    :return: подготовленная структура synth_params
    """
    status = 'error'
    params = {}
    messages = {
        "info": [],
        "warn": [],
        "error": [],
        "critical": []
    }
    if 'drawflow' not in frontend_data:
        messages["critical"].append('Неверный формат входных данных: отсутствует раздел drawflow')
        return status, messages, params
    if 'Home' not in frontend_data['drawflow']:
        messages["critical"].append('Неверный формат входных данных: отсутствует раздел drawflow/Home')
        return status, messages, params
    if 'data' not in frontend_data['drawflow']['Home']:
        messages["critical"].append('Неверный формат входных данных: отсутствует раздел drawflow/Home/data')
        return status, messages, params
    if not isinstance(frontend_data['drawflow']['Home']['data'], dict):
        messages["critical"].append('Неверный формат входных данных: drawflow/Home/data не является словарем')
        return status, messages, params

    params = {'name': '', 'tones':{}, 'effects':{}, 'duration':5, 'master_volume':1}
    if 'name' in frontend_data:
        if not all(char.isalnum() or char.isspace() for char in frontend_data['name']):
            messages["error"].append('Недопустимое имя файла: ' + frontend_data['name'])
            return status, messages, params
        params['name'] = frontend_data['name']
    if 'output_node' in frontend_data:
        params['output_node'] = int(frontend_data['output_node'])

    num_endpoints = 0

    # Собираем дерево параметров синтеза
    """
    Параметры синтеза: Словарь, содержащий данные для синтеза
    :key duration:
    :key tones:
    :key effects:
    Пример:
    synth_params = {
        "duration": 10,
        "harmonics": [
            {"base": 0, "factor": 2, "amp": 0.3, "phase": 0.2},
            {"base": 0, "factor": 3, "amp": 0.1, "phase": 0}
        ],
        "tones": [
            {"freq": 440, "amp": 1, "phase": 0},
            {"freq": 2, "amp": 0.1, "phase": 0}
        ],
        "effects": [
            {"type": "envelope", "input": "mixer_0", "data": [(1,1)]}
        ]
    }
    """
    for node_id, node_data in frontend_data['drawflow']['Home']['data'].items():
        if str(int(node_id)) != node_id:
            messages["error"].append('Неизвестный ключ словаря drawflow/Home/data: ' + node_id)
            continue
        if not isinstance(node_data, dict):
            messages["error"].append('Данные для узла id=' + node_id + ' не являются словарём')
            continue
        if 'class' not in node_data:
            messages["error"].append('Узел id=' + node_id + ' не имеет атрибута class')
            continue
        if 'data' not in node_data:
            messages["error"].append('Узел id=' + node_id + ' не имеет элемента data')
            continue

        # TODO По-хорошему, надо обходить дерево от узла sounddevice
        # Пока что собираем отдельно список генераторов и список эффектов
        match node_data['class']:
            case 'tone':
                params['tones'][node_id] = node_data['data']
                params['tones'][node_id]['type'] = node_data['class']
            case 'harmonic':
                params['tones'][node_id] = node_data['data']
                params['tones'][node_id]['type'] = node_data['class']
                if len(node_data['inputs']['input_1']['connections']) > 0:
                    params['tones'][node_id]['base'] = node_data['inputs']['input_1']['connections'][0]['node']
                else:
                    messages["error"].append('Элемент "Генератор гармоники" id=' + node_id + ' не имеет входного подключения')
            case 'mixer':
                params['effects'][node_id] = node_data['data']
                params['effects'][node_id]['type'] = node_data['class']
                params['effects'][node_id]['input'] = []
                for input_data in node_data['inputs'].values():
                    for connection_data in input_data['connections']:
                        params['effects'][node_id]['input'].append(connection_data['node'])
                        # TODO one input can have multiple connections
                if len(params['effects'][node_id]['input']) == 0:
                    messages["error"].append('Элемент "Микшер" id=' + node_id + ' не имеет входных подключений')
            case 'modulator':
                params['effects'][node_id] = node_data['data']
                params['effects'][node_id]['type'] = node_data['class']
                params['effects'][node_id]['input'] = []
                for input_data in node_data['inputs'].values():
                    for connection_data in input_data['connections']:
                        params['effects'][node_id]['input'].append(connection_data['node'])
                if len(params['effects'][node_id]['input']) == 0:
                    messages["error"].append('Элемент "Модулятор" id=' + node_id + ' не имеет входных подключений')
            case 'envelope':
                try:
                    if 'params' not in node_data['data'] or node_data['data']['params'] == '':
                        raise Exception('Строка параметров не задана')
                    if len(node_data['data']['params']) > 255:
                        raise Exception('Слишком длинная строка параметров')
                    if not all(char in '(),. -0123456789' for char in node_data['data']['params']):
                        raise Exception('Недопустимый формат строки параметров ' + str(node_data['data']['params']))
                    parsed_params = ast.literal_eval(node_data['data']['params'])
                    if not isinstance(parsed_params, tuple):
                        raise Exception('Нельзя преобразовать в кортеж строку параметров ' + str(node_data['data']['params']))
                    if len(parsed_params) == 2 and type(parsed_params[0]) is not tuple:
                        parsed_params = [parsed_params]
                    else:
                        parsed_params = list(parsed_params)
                    for el in parsed_params:
                        if not isinstance(el, tuple):
                            raise Exception('Часть строки параметров не является кортежем ' + str(el))
                    params['effects'][node_id] = {'params': parsed_params}
                    params['effects'][node_id]['type'] = node_data['class']
                    if len(node_data['inputs']['input_1']['connections']) == 0:
                        raise Exception('Элемент не имеет входных подключений')
                    params['effects'][node_id]['input'] = node_data['inputs']['input_1']['connections'][0]['node']
                except Exception as err:
                    messages['error'].append('Неверные параметры элемента "Огибающая" id=' + node_id + ': ' + str(err))
            case 'sounddevice':
                num_endpoints += 1
                params['effects'][node_id] = node_data['data']
                if len(node_data['inputs']['input_1']['connections']):
                    params['effects'][node_id]['input'] = node_data['inputs']['input_1']['connections'][0]['node']
                else:
                    messages["error"].append(
                        'Элемент "Звуковое устройство" id=' + node_id + ' не имеет входного подключения')
                if 'duration' in node_data['data']:
                    if all(char in ' .+0123456789' for char in str(node_data['data']['duration'])):
                        params['duration'] = float(node_data['data']['duration'])
                    else:
                        messages["error"].append(
                            'У элемента "Звуковое устройство" id=' + node_id + ' задано недопустимое значение длительности: ' + str(node_data['data']['duration']))
                if 'volume' in node_data['data'] and node_data['data']['volume'] != '':
                    params['master_volume'] = float(node_data['data']['volume'])
                params['effects'][node_id]['type'] = node_data['class']
            case 'oscilloscope':
                if len(node_data['inputs']['input_1']['connections']):
                    params['output_node'] = node_data['inputs']['input_1']['connections'][0]['node'];
                else:
                    messages["warn"].append('Элемент "Осциллограф" id=' + node_id + ' не подключён к схеме. Не подключённый осциллограф показывает сигнал на входе звукового устройства.')
            case 'comment':
                # Ничего не делаем
                messages["warn"].append('На схеме есть элементы "Комментарий", они вам точно нужны?')
            case _:
                messages["error"].append('Неизвестный тип узла: id=' + node_data['class'] + ', id: ' + node_id)

    if num_endpoints == 0:
        messages["error"].append('Отсутствует обязательный элемент "Звуковое устройство"')
    if num_endpoints > 1:
        messages["error"].append('На схеме имеются несколько элементов "Звуковое устройство": ' + str(num_endpoints))

    if params['duration'] <= 0:
        messages["error"].append('Недопустимое значение длительности: ' + str(params['duration']) + ' сек.')
    if params['duration'] > 30:
        messages["error"].append('Cлишком большое значение длительности: ' + str(params['duration']) + ' сек. Длительность не должна превышать 30 сек.')
    if abs(params['master_volume']) > 1:
        messages["error"].append('Cлишком большое значение громкости ' + str(params['master_volume']) + '. Громкость не должна превышать 1 (100%).')

    if len(messages['critical']) > 0 or len(messages['error']) > 0:
        status = 'error'
        return status, messages, params

    # Приводим тип всех параметров
    # Для гармоник явно определяем частоту
    for tone_id, tone_data in params['tones'].items():
        if tone_data['type'] == 'tone':
            if 'freq' not in tone_data or tone_data['freq'] == '' or not all(char in '.0123456789' for char in str(tone_data['freq'])) or float(str(tone_data['freq']) + '0') == 0:
                messages["critical"].append(f'Для элемента "Генератор тона" {tone_id} задано недопустимое значение параметра "Частота"')
                params['tones'][tone_id]['freq'] = 0
            else:
                params['tones'][tone_id]['freq'] = float(tone_data['freq'])
        if 'amp' in tone_data:
            params['tones'][tone_id]['amp'] = float(tone_data['amp'])
        if 'phase' in tone_data:
            params['tones'][tone_id]['phase'] = float(tone_data['phase'])
        if tone_data['type'] == 'harmonic':
            factor = int(tone_data['factor'])
            base_id = tone_data['base']
            freq = float(params['tones'][base_id]['freq']) * factor
            params['tones'][tone_id]['freq'] = freq
        if 'freq' in params['tones'][tone_id] and params['tones'][tone_id]['freq'] > 16000:
                messages["warn"].append('Тон ' + tone_id +' имеет слишком большое значение частоты: ' + str(params['tones'][tone_id]['freq']) + ' Гц.')

    if len(messages['critical']) == 0 and len(messages['error']) == 0:
        status = 'ok'
    return status, messages, params


def save_preset(filename: str, preset: str):
    """
    Сохраняет конфигурацию конструктора в файл с заданным именем
    :param filename: имя файла
    :param preset: конфигурация конструктора (значения тонов и т.п; расположение блоков)
    """
    with open(filename, "wb") as f:
        f.write(preset.encode("utf-8"))


def list_presets(dirname) -> tuple:
    """
    Возвращает список сохраненных пресетов
    """
    status = 'ok'
    files = []
    messages = []
    if not dirname.is_dir():
        status = 'error'
        messages.append('Каталог пресетов не найден: ' + dirname)
        return status, files, messages
    for file in dirname.glob('*.json'):
        files.append(file.stem)
    return status, files, messages


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


def multiply(samples1: list, samples2: list) -> list:
    """
    Выполняет почленное перемножение двух наборов семплов
    """
    result = []
    for idx in range(0, len(samples1)):
        curr_sample = 0
        if idx < len(samples2):
            curr_sample = samples1[idx] * samples2[idx]
        result.append(curr_sample)
    return result

def modulate(base_samples, control_samples, depth):
    """
    Модулирует сигнал base_samples сигналом control_samples с глубиной depth
    """
    factoring_samples = []
    control_dc = 1 - depth
    for idx in range(0, len(control_samples)):
        factoring_samples.append(control_samples[idx] * depth + control_dc)
    return multiply(base_samples, factoring_samples)


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
    :param samples: массив семплов
    :param envelope: Кусочно-линейная огибающая
        Список кортежей вида (Tn, An), упорядоченный по возрастанию Tn (Tn >= 0), где
        T: float момент времени
        A: float (0..1) относительная амплитуда в этот момент времени
        Пример: ((0, 1), (0.1, 0))
    """
    duration = len(samples) / 44100 #44100 = Sample Rate
    envelope.append((duration, 0)) # От последней заданной точки к концу звучания амплитуда снижается до 0
    SaWAppEnv = [] #Samples with applied envelope
    segm_no = 1
    for sample_no in range(len(samples)):
        current_time = sample_no/44100
        if current_time > envelope[segm_no][0]:
            if segm_no < len(envelope):
                segm_no += 1
        amplitude = (current_time - envelope[segm_no - 1][0]) * (envelope[segm_no][1] - envelope[segm_no - 1][1])\
            / (envelope[segm_no][0] - envelope[segm_no - 1][0])
        amplitude = (amplitude + envelope[segm_no - 1][1]) ** 2
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


def synthesize(params: dict, end_node: int=0) -> list:
    """
    Синтезирует набор семплов по заданным параметрам синтеза
    :param params: параметры синтеза
    :param end_node: для какого узла вернуть результат (если 0, то для звукового устройства)
    """
    tone_samples = {}
    result = []
    for id, data in params['tones'].items():
        tone_samples[id] = generate_sine_wave(data['freq'],
                                              params['duration'],
                                              data['amp'],
                                              data['phase'])
    if id == end_node:
        return tone_samples[id]

    while len(result) == 0:
        for id, data in params['effects'].items():
            if not id in tone_samples.keys():
                tone_samples[id] = []
            elif len(tone_samples[id]) > 0:
                continue
            match data['type']:
                case 'mixer':
                    inputs_ready = True
                    for input_id in data['input']:
                        if input_id not in tone_samples.keys():
                            inputs_ready = False
                    if inputs_ready == True:
                        input_samples_list = []
                        for input_id in data['input']:
                            input_samples_list.append(tone_samples[input_id])
                        tone_samples[id] = mix(input_samples_list)
                case 'modulator':
                    inputs_ready = True
                    for input_id in data['input']:
                        if input_id not in tone_samples.keys():
                            inputs_ready = False
                    if inputs_ready == True:
                        input_samples_list = []
                        for input_id in data['input']:
                            input_samples_list.append(tone_samples[input_id])
                        tone_samples[id] = modulate(input_samples_list[0], input_samples_list[1], float(data['depth']))
                case 'envelope':
                    if (len(tone_samples[id]) == 0) and (len(tone_samples[data['input']]) > 0):
                        tone_samples[id] = apply_envelope(tone_samples[data['input']], data['params'])
                case 'sounddevice':
                    if (data['input'] in tone_samples) and (len(tone_samples[data['input']]) > 0):
                        return tone_samples[data['input']]
        if (end_node in tone_samples) and len(tone_samples[end_node]) > 0:
            return tone_samples[end_node]


def is_valid_preset_name(name: str):
    """
    Проверяет строку на валидность в качестве имени пресета.
    В имени допустимы буквы, цифры и пробел.
    """
    return all(char.isalnum() or char.isspace() for char in name)