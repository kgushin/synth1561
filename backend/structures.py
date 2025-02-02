# Описание структур

synth_params = {}
"""
Параметры синтеза
Словарь, содержащий данные для синтеза
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


tone_params = {}
"""
Параметры тона
:key type: тип {"base", "harmonic"} default "base"
:key form: форма сигнала {"sine", "square", "saw"} default "sine"
:key freq: частота float > 0, не превосходит (SAMPLE_RATE / 2) (по теореме Котельникова)
:key factor: множитель частоты int > 0, указывается для гармоник вместо частоты
:key amp: относительная амплитуда float (0..1) default 1
:key phase: фаза float (-1..1) default 0, значения -1 и 1 соответствуют сдвигу фазы -PI/2 и PI/2
Пример:
tone_params = {"type": "base", "freq": 440}
"""

envelope_params = []
"""
Кусочно-линейная огибающая
Массив таплов (T, A), где
    T: float момент времени (если значение отрицательное, отсчитывается от конца звучания)
    A: float (0..1) относительная амплитуда в этот момент времени
# Пример:
envelope_params = [(0, 1), (0.1, 0)]
"""
