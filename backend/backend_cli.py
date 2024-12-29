import argparse

parser = argparse.ArgumentParser()

parser.add_argument("-a", "--action",
                    choices=['play', 'check', 'export'], default='play',
                    help="выполняемое действие:\n" +
                         "play -- воспроизвести звук,\n" +
                         "check -- проверить корректность заданных параметров,\n" +
                         "save -- сохранить результат в файл outfile в формате format")
parser.add_argument("-o", "--outfile",
                    help="имя файла для сохранения результата синтеза")
parser.add_argument("-f", "--format", choices=['wav', 'txt'], default='wav',
                    help="формат результата синтеза\n" +
                         "wav -- формат файла .wav,\n" +
                         "txt -- набор значений амплитуды (-1..1), разделённых переводами строк")
parser.add_argument("-p", "--params",
                    help="параметры синтеза в виде строки или имя файла с параметрами")
parser.add_argument("-w", "--wait",
                    help="не завершать программу до окончания проигрывания звука")

options = parser.parse_args()

print(options)

print ((-0.2 % 1) + 1)