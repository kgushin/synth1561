import sys
import pprint

sys.path.insert(0, '../backend')

import json
import functions


def test_mix():
    set_of_sample_lists1 = [[0, 0.1, 1, -0.1, -1], [1, 2, 4, 8, 16]]
    mixed_set = functions.mix(set_of_sample_lists1)
    assert mixed_set == [1, 2.1, 5, 7.9, 15]


def test_prepare_params():
    t = r'''
    {
        "drawflow": {
            "Home": {
                "data": {
                    "2": {
                        "id": 2,
                        "name": "tone",
                        "data": {
                            "freq": "440", "amp": "1", "phase": "0"
                        },
                        "class": "tone",
                        "html": "\n        <div>\n          <div class=\"title-box\"><i class=\"fab fa-facebook\"></i> Генератор тона</div>\n\t\t  <div class=\"box\">\n            <p>Параметры</p>\n            <input type=\"text\" df-params>\n          </div>\n        </div>\n        ",
                        "typenode": false,
                        "inputs": {},
                        "outputs": {
                            "output_1": {
                                "connections": [
                                    {
                                        "node": "4",
                                        "output": "input_1"
                                    },
                                    {
                                        "node": "3",
                                        "output": "input_1"
                                    }
                                ]
                            }
                        },
                        "pos_x": 35,
                        "pos_y": 18
                    },
                    "3": {
                        "id": 3,
                        "name": "harmonic",
                        "data": {
                            "factor": "3", "amp": "0.7", "phase": "0.3"
                        },
                        "class": "harmonic",
                        "html": "\n        <div>\n          <div class=\"title-box\"><i class=\"fab fa-facebook\"></i> Генератор гармоники</div>\n\t\t  <div class=\"box\">\n            <p>Параметры</p>\n            <input type=\"text\" df-params>\n          </div>\n        </div>\n        ",
                        "typenode": false,
                        "inputs": {
                            "input_1": {
                                "connections": [
                                    {
                                        "node": "2",
                                        "input": "output_1"
                                    }
                                ]
                            }
                        },
                        "outputs": {
                            "output_1": {
                                "connections": [
                                    {
                                        "node": "4",
                                        "output": "input_3"
                                    }
                                ]
                            }
                        },
                        "pos_x": 279,
                        "pos_y": 235
                    },
                    "4": {
                        "id": 4,
                        "name": "mixer",
                        "data": {},
                        "class": "mixer",
                        "html": "\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-code-branch\"></i> Микшер</div>\n            </div>\n            ",
                        "typenode": false,
                        "inputs": {
                            "input_1": {
                                "connections": [
                                    {
                                        "node": "2",
                                        "input": "output_1"
                                    }
                                ]
                            },
                            "input_2": {
                                "connections": []
                            },
                            "input_3": {
                                "connections": [
                                    {
                                        "node": "3",
                                        "input": "output_1"
                                    }
                                ]
                            }
                        },
                        "outputs": {
                            "output_1": {
                                "connections": [
                                    {
                                        "node": "5",
                                        "output": "input_1"
                                    }
                                ]
                            }
                        },
                        "pos_x": 367,
                        "pos_y": 28
                    },
                    "5": {
                        "id": 5,
                        "name": "sounddevice",
                        "data": {},
                        "class": "sounddevice",
                        "html": "\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-volume-up\"></i> Звуковое устройство</div>\n            </div>\n            ",
                        "typenode": false,
                        "inputs": {
                            "input_1": {
                                "connections": [
                                    {
                                        "node": "4",
                                        "input": "output_1"
                                    }
                                ]
                            }
                        },
                        "outputs": {},
                        "pos_x": 635.4228210449219,
                        "pos_y": 216.42352294921875
                    }
                }
            }
        },
        "command": "save_preset"
    }
    '''

    ts = json.loads(t)
    pprint.pprint(ts)
    res, msg, par = functions.prepare_params(ts)
    return res


def test_synthesize():
    params = test_prepare_params()
    params['duration'] = 2
    pprint.pprint(params)
    samples = functions.synthesize(params)

    functions.write_wave('test.wav', functions.normalize(samples))
    functions.play_sound(functions.normalize(samples))

#test_synthesize


def test_save_n_load_preset():
    t = r'''
        {
            "drawflow": {
                "Home": {
                    "data": {
                        "2": {
                            "id": 2,
                            "name": "tone",
                            "data": {
                                "freq": "440", "amp": "1", "phase": "0"
                            },
                            "class": "tone",
                            "html": "\n        <div>\n          <div class=\"title-box\"><i class=\"fab fa-facebook\"></i> Генератор тона</div>\n\t\t  <div class=\"box\">\n            <p>Параметры</p>\n            <input type=\"text\" df-params>\n          </div>\n        </div>\n        ",
                            "typenode": false,
                            "inputs": {},
                            "outputs": {
                                "output_1": {
                                    "connections": [
                                        {
                                            "node": "4",
                                            "output": "input_1"
                                        },
                                        {
                                            "node": "3",
                                            "output": "input_1"
                                        }
                                    ]
                                }
                            },
                            "pos_x": 35,
                            "pos_y": 18
                        },
                        "3": {
                            "id": 3,
                            "name": "harmonic",
                            "data": {
                                "factor": "3", "amp": "0.7", "phase": "0.3"
                            },
                            "class": "harmonic",
                            "html": "\n        <div>\n          <div class=\"title-box\"><i class=\"fab fa-facebook\"></i> Генератор гармоники</div>\n\t\t  <div class=\"box\">\n            <p>Параметры</p>\n            <input type=\"text\" df-params>\n          </div>\n        </div>\n        ",
                            "typenode": false,
                            "inputs": {
                                "input_1": {
                                    "connections": [
                                        {
                                            "node": "2",
                                            "input": "output_1"
                                        }
                                    ]
                                }
                            },
                            "outputs": {
                                "output_1": {
                                    "connections": [
                                        {
                                            "node": "4",
                                            "output": "input_3"
                                        }
                                    ]
                                }
                            },
                            "pos_x": 279,
                            "pos_y": 235
                        },
                        "4": {
                            "id": 4,
                            "name": "mixer",
                            "data": {},
                            "class": "mixer",
                            "html": "\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-code-branch\"></i> Микшер</div>\n            </div>\n            ",
                            "typenode": false,
                            "inputs": {
                                "input_1": {
                                    "connections": [
                                        {
                                            "node": "2",
                                            "input": "output_1"
                                        }
                                    ]
                                },
                                "input_2": {
                                    "connections": []
                                },
                                "input_3": {
                                    "connections": [
                                        {
                                            "node": "3",
                                            "input": "output_1"
                                        }
                                    ]
                                }
                            },
                            "outputs": {
                                "output_1": {
                                    "connections": [
                                        {
                                            "node": "5",
                                            "output": "input_1"
                                        }
                                    ]
                                }
                            },
                            "pos_x": 367,
                            "pos_y": 28
                        },
                        "5": {
                            "id": 5,
                            "name": "sounddevice",
                            "data": {},
                            "class": "sounddevice",
                            "html": "\n            <div>\n              <div class=\"title-box\"><i class=\"fas fa-volume-up\"></i> Звуковое устройство</div>\n            </div>\n            ",
                            "typenode": false,
                            "inputs": {
                                "input_1": {
                                    "connections": [
                                        {
                                            "node": "4",
                                            "input": "output_1"
                                        }
                                    ]
                                }
                            },
                            "outputs": {},
                            "pos_x": 635.4228210449219,
                            "pos_y": 216.42352294921875
                        }
                    }
                }
            },
            "command": "save_preset"
        }
        '''
    functions.save_preset("testttt", t)
    x = functions.load_preset("testttt")
    assert t == x


test_save_n_load_preset()


def test_playback() -> object:
    return False


