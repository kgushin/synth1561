import sys
import json
from pathlib import Path

from flask import render_template
from flask import jsonify
from flask import request
from frontend import frontend

sys.path.insert(0, 'backend')
PROJECT_ROOT = Path(frontend.root_path).absolute().parent
PRESET_DIR = PROJECT_ROOT / 'presets'

import functions as fn


@frontend.route('/')
@frontend.route('/index')
def index():
    return render_template('index.html')


@frontend.route('/check_params', methods=['POST'])
def check_params():
    res, msg, par = fn.prepare_params(request.json)
    return jsonify({'res': res, 'msg': msg, 'par': par})


@frontend.route('/play', methods=['POST'])
def play():
    res, msg, par = fn.prepare_params(request.json)
    if res == 'ok':
        samples = fn.synthesize(par)
        fn.play_sound(fn.normalize(samples))
    return jsonify({'res': res, 'msg': msg, 'par': par})


@frontend.route('/list_presets', methods=['GET'])
def list_presets():
    res, files, msg = fn.list_presets(PRESET_DIR)
    return jsonify({'res': res, 'files': files, 'msg': msg})


@frontend.route('/save_preset', methods=['POST'])
def save_preset():
    res = 'ok'
    msg = []
    data = {}
    if ('name' not in request.json) or ('data' not in request.json):
        res = 'error'
        msg.append('Неверная структура запроса')
        return jsonify({'res': res, 'msg': msg, 'data': data})
    file = PRESET_DIR / (request.json['name'] + '.json')
    if file.exists():
        file.unlink(missing_ok=False)
    fn.save_preset(file, json.dumps(request.json['data']))
    return jsonify({'res': res, 'msg': msg, 'data': data})


@frontend.route('/load_preset', methods=['POST'])
def load_preset():
    res = 'ok'
    msg = []
    data = {}
    if 'name' not in request.json:
        res = 'error'
        msg.append('Неверная структура запроса')
        return jsonify({'res': res, 'msg': msg, 'data': data})
    file = PRESET_DIR / (request.json['name'] + '.json')
    if not file.exists():
        res = 'error'
        msg.append('Файл не найден: ' + str(file))
        return jsonify({'res': res, 'msg': msg, 'data': data})
    preset_data = fn.load_preset(file)
    return jsonify({'res': res, 'msg': msg, 'data': json.loads(preset_data)})

