import os
import sys
import argparse
from pathlib import Path
import json

if sys.prefix == sys.base_prefix:
    print ('\nПрограмма должна быть запущена из виртуального окружения Python. Пожалуйста, обратитесь к документации.')
    quit()

PROJECT_ROOT = Path(__file__).absolute().parent.parent
sys.path.insert(0, PROJECT_ROOT)

import functions as fn

PRESET_DIR = PROJECT_ROOT / 'presets'
SAVE_DIR = PROJECT_ROOT / 'cli_save'
if SAVE_DIR.exists() == False:
    try:
        SAVE_DIR.mkdir(exist_ok=True)
    except Exception as e:
        print('Ошибка создания каталога ' + SAVE_DIR)
        quit()

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("-i", "--input", required=True,
                    help="имя файла json с параметрами схемы (в каталоге пресетов, указывать без расширения)")
parser.add_argument("-c", "--check", action="store_true", default=True,
                    help="проверить корректность схемы, не выполняя синтеза")
parser.add_argument("-p", "--play", action="store_true",
                    help="синтезировать и воспроизвести звук (также сохраняет звук в файл .wav в каталоге " + str(SAVE_DIR) + ")")
parser.add_argument("-e", "--export", action="store_true", default=False,
                    help="сохранить результат в файл .txt как набор значений амплитуды (-1..1), разделённых переводами строк, в каталоге " + str(SAVE_DIR))
parser.add_argument("-h", "--help", action='help', default=argparse.SUPPRESS,
                    help="показать эту справку")

options = parser.parse_args()
# print(options)
print('\n')

if options.input:
    if not fn.is_valid_preset_name(options.input):
        print('Указано недопустимое имя файла пресета (имя может включать только буквы, цифры и пробел).')
        quit()
    schema_file = PRESET_DIR / (options.input + '.json')
    if not schema_file.exists():
        print("Файл схемы не найден: " + str(schema_file))
        quit()
    print("Используемый файл схемы: " + str(schema_file))
    preset_data = json.loads(fn.load_preset(schema_file))
else:
    print('Не указан обязательный параметр --input')
    print('Для вывода справки укажите параметр --help или -h')
    quit()

if options.check == True:
    res, msg, par = fn.prepare_params(preset_data)
    if res == 'ok':
        print('\nСхема корректна')
    else:
        print('\nСхема некорректна')
        print(res, msg)
        quit()

if options.play == True:
    res, msg, par = fn.prepare_params(preset_data)
    if res == 'ok':
        samples = fn.synthesize(par)
        samples = fn.normalize(samples)
        fn.write_wave(str(SAVE_DIR / options.input) + '.wav', samples)
        print('\nРезультат синтеза записан в файл ' + str(SAVE_DIR / options.input) + '.wav')
        if os.name == 'nt':
            fn.play_sound(fn.normalize(samples))
        else:
            print('\nВоспроизведение звука из командной строки возможно только на платформе Windows')

if options.export != False:
    res, msg, par = fn.prepare_params(preset_data)
    if res == 'ok':
        samples = fn.synthesize(par)
        with open(str(SAVE_DIR / options.input) + ".txt", "w") as f:
            f.write("\n".join(str(sample) for sample in samples))
            print('Результат синтеза в виде отсчетов (-1..1) записан в файл ' + str(SAVE_DIR / options.input) + '.txt')
    else:
        print('Некорректная схема')
        print(res, msg)