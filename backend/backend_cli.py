import sys
import argparse
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).absolute().parent.parent
PRESET_DIR = PROJECT_ROOT / 'presets'
sys.path.insert(0, PROJECT_ROOT)

import functions as fn

parser = argparse.ArgumentParser()

parser.add_argument("-c", "--check", action="store_true",
                    help="проверить корректность схемы, не выполняя синтеза")
parser.add_argument("-p", "--play", action="store_true",
                    help="синтезировать и воспроизвести звук")
parser.add_argument("-e", "--export",
                    help="сохранить результат в указанный файл как " +
                         "набор значений амплитуды (-1..1), разделённых переводами строк")
parser.add_argument("-s", "--save",
                    help="сохранить результат в указанный файл .wav")
parser.add_argument("-i", "--input",
                    help="имя файла json с параметрами схемы")

options = parser.parse_args()

print(options)

schema_file = PRESET_DIR / (options.input + '.json')
if not schema_file.exists():
    print("Файл схемы не найден: " + str(schema_file))
    quit()
print("Используемый файл схемы: " + str(schema_file))
preset_data = json.loads(fn.load_preset(schema_file))

if options.check == True:
    res, msg, par = fn.prepare_params(preset_data)
    print(res, msg)

if options.play == True:
    res, msg, par = fn.prepare_params(preset_data)
    print(res, msg)
    if res == 'ok':
        samples = fn.synthesize(par)
        fn.play_sound(fn.normalize(samples))