import sys
import json

from flask import render_template
from flask import jsonify
from flask import request
from frontend import frontend

sys.path.insert(0, 'backend')

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