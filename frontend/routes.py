import sys
import json
from pathlib import Path
import pprint

from flask import render_template
from flask import jsonify
from flask import request
from frontend import frontend

sys.path.insert(0, 'backend')
import functions as fn


PROJECT_ROOT = Path(frontend.root_path).absolute().parent
PRESET_DIR = PROJECT_ROOT / 'presets'
if not PRESET_DIR.exists():
    PRESET_DIR.mkdir()
SOUND_DIR = PROJECT_ROOT / 'frontend' / 'static' / 'sound_cache'
if not SOUND_DIR.exists():
    SOUND_DIR.mkdir()

@frontend.route('/')
@frontend.route('/index')
def index():
    return render_template('index.html')


@frontend.route('/docs')
def docs():
    return render_template('docs.html')


@frontend.route('/about')
def about():
    return render_template('about.html')


@frontend.route('/check_params', methods=['POST'])
def check_params():
    res, msg, par = fn.prepare_params(request.json)
    return jsonify({'res': res, 'msg': msg, 'par': par})


@frontend.route('/play', methods=['POST'])
def play():
    res, msg, par = fn.prepare_params(request.json)
    if res == 'ok':
        samples = fn.synthesize(par)
        samples = fn.apply_envelope(samples, [(0, 1),(par["duration"] * 0.9, 1), (par["duration"], 0)])
        samples = fn.normalize(samples)
        if 'master_volume' in par and par['master_volume'] < 1:
            adj_samples = []
            for sample in samples:
                adj_samples.append(int(sample * par['master_volume']))
            samples = adj_samples
        #fn.play_sound(samples)
        #print(SOUND_DIR / (par['name'] + '.wav'))
        fn.write_wave(str(SOUND_DIR / (par['name'] + '.wav')), samples)
    return jsonify({'res': res, 'msg': msg, 'par': par})


@frontend.route('/get_samples', methods=['POST'])
def get_samples():
    res, msg, par = fn.prepare_params(request.json)
    samples = []
    data = []
    if res == 'ok':
        samples = fn.synthesize(par, par['output_node'])
        for idx in range(len(samples)):
            data.append(str(round(samples[idx], 3)))
    return jsonify({'res': res, 'msg': msg, 'data': ",".join(data), 'sample_rate': fn.SAMPLE_RATE})


@frontend.route('/list_presets', methods=['GET'])
def list_presets():
    res, files, msg = fn.list_presets(PRESET_DIR)
    return jsonify({'res': res, 'files': files, 'msg': msg})


@frontend.route('/save_preset', methods=['POST'])
def save_preset():
    res = 'ok'
    msg =  {
        "info": [],
        "warn": [],
        "error": [],
        "critical": []
    }
    data = {}
    if ('name' not in request.json) or ('data' not in request.json):
        res = 'error'
        msg["error"].append('Неверная структура запроса')
        return jsonify({'res': res, 'msg': msg, 'data': data})
    if not all(char.isalnum() or char.isspace() for char in request.json['name']):
        res = 'error'
        msg["error"].append('Недопустимое имя файла: ' + request.json['name'])
        return jsonify({'res': res, 'msg': msg, 'data': data})
    file = PRESET_DIR / (request.json['name'] + '.json')
    if file.exists():
        file.unlink(missing_ok=False)
    fn.save_preset(file, json.dumps(request.json['data']))
    return jsonify({'res': res, 'msg': msg, 'data': data})


@frontend.route('/load_preset', methods=['POST'])
def load_preset():
    res = 'ok'
    msg = {
        "info": [],
        "warn": [],
        "error": [],
        "critical": []
    }
    data = {}
    if 'name' not in request.json:
        res = 'error'
        msg["error"].append('Неверная структура запроса')
        return jsonify({'res': res, 'msg': msg, 'data': data})
    file = PRESET_DIR / (request.json['name'] + '.json')
    if not file.exists():
        res = 'error'
        msg["error"].append('Файл не найден: ' + str(file))
        return jsonify({'res': res, 'msg': msg, 'data': data})
    preset_data = fn.load_preset(file)
    return jsonify({'res': res, 'msg': msg, 'data': json.loads(preset_data)})

