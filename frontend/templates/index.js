var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = true;
const dataToImport = {"drawflow":{"Home":{"data":{"1":{"id":1,"name":"welcome","data":{},"class":"welcome","html":"\n    <div>\n      <div class=\"title-box\">&#128587; Добро пожаловать!</div>\n      <div class=\"box\">\n        <p> <b>Краткая справка</b></p><br>\n\n        <p><b>Добавляйте элементы</b>, перетаскивая их из палитры слева<br><br>\n           <b>Чтобы соединить элементы</b>, перетащите выход одного ко входу другого<br><br>\n           <b>Для удаления</b> выберите элемент и нажмите клавишу Delete<br><br>\n           <b>Для изменения масштаба</b> изображения вращайте колёсико мыши, нажав Ctrl</p>\n      </div>\n    </div>\n    ","typenode": false, "inputs":{},"outputs":{},"pos_x":10,"pos_y":10}}}}}
editor.start();
editor.import(dataToImport);

// Events!
// TODO: disable logging in prod
editor.on('nodeCreated', function(id) {
  console.log("Node created " + id);
  check_scheme();
})

editor.on('nodeRemoved', function(id) {
  console.log("Node removed " + id);
  check_scheme();
})

editor.on('nodeSelected', function(id) {
  console.log("Node selected " + id);
})

editor.on('moduleCreated', function(name) {
  console.log("Module Created " + name);
})

editor.on('moduleChanged', function(name) {
  console.log("Module Changed " + name);
})

editor.on('connectionCreated', function(connection) {
  console.log('Connection created');
  console.log(connection);
  check_scheme();
})

editor.on('connectionRemoved', function(connection) {
  console.log('Connection removed');
  console.log(connection);
  check_scheme();
})

editor.on('mouseMove', function(position) {
  console.log('Position mouse x:' + position.x + ' y:'+ position.y);
})

editor.on('nodeMoved', function(id) {
  console.log("Node moved " + id);
})

editor.on('zoom', function(zoom) {
  console.log('Zoom level ' + zoom);
})

editor.on('translate', function(position) {
  console.log('Translate x:' + position.x + ' y:'+ position.y);
})

editor.on('addReroute', function(id) {
  console.log("Reroute added " + id);
})

editor.on('removeReroute', function(id) {
  console.log("Reroute removed " + id);
})

/* DRAG EVENT */

/* Mouse and Touch Actions */

var elements = document.getElementsByClassName('drag-drawflow');
for (var i = 0; i < elements.length; i++) {
  elements[i].addEventListener('touchend', drop, false);
  elements[i].addEventListener('touchmove', positionMobile, false);
  elements[i].addEventListener('touchstart', drag, false );
}

var mobile_item_selec = '';
var mobile_last_move = null;
function positionMobile(ev) {
 mobile_last_move = ev;
}

function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  if (ev.type === "touchstart") {
    mobile_item_selec = ev.target.closest(".drag-drawflow").getAttribute('data-node');
  } else {
  ev.dataTransfer.setData("node", ev.target.getAttribute('data-node'));
  }
}

function drop(ev) {
  if (ev.type === "touchend") {
    var parentdrawflow = document.elementFromPoint( mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY).closest("#drawflow");
    if(parentdrawflow != null) {
      addNodeToDrawFlow(mobile_item_selec, mobile_last_move.touches[0].clientX, mobile_last_move.touches[0].clientY);
    }
    mobile_item_selec = '';
  } else {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("node");
    addNodeToDrawFlow(data, ev.clientX, ev.clientY);
  }

}

function addNodeToDrawFlow(name, pos_x, pos_y) {
  if(editor.editor_mode === 'fixed') {
    return false;
  }
  pos_x = pos_x * ( editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)) - (editor.precanvas.getBoundingClientRect().x * ( editor.precanvas.clientWidth / (editor.precanvas.clientWidth * editor.zoom)));
  pos_y = pos_y * ( editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)) - (editor.precanvas.getBoundingClientRect().y * ( editor.precanvas.clientHeight / (editor.precanvas.clientHeight * editor.zoom)));

  switch (name) {
    case 'tone':
    var tone = `
    <div>
      <div class="title-box"><i class="fas fa-wave-square"></i> Генератор тона</div>
          <div class="box">
        <p>Параметры</p>
        f: <input class="short" type="text" df-freq>
        &nbsp;A: <input class="short" type="text" value="1" df-amp>
        &nbsp;&phi;: <input class="short" type="text" value="0" df-phase>
      </div>
    </div>
    `;
      editor.addNode('tone', 0,  1, pos_x, pos_y, 'tone', {"freq": '', "amp": '1', "phase": '0'}, tone);
      break;
    case 'harmonic':
      var harmonic = `
    <div>
      <div class="title-box"><i class="fas fa-wave-square"></i> Генератор гармоники</div>
      <div class="box">
        <p>Параметры</p>
        k: <input class="short" type="text" df-factor>
        &nbsp;A: <input class="short" type="text" value="1" df-amp>
        &nbsp;&phi;: <input class="short" type="text" value="0" df-phase>
      </div>
    </div>
    `;
      editor.addNode('harmonic', 1,  1, pos_x, pos_y, 'harmonic', { "factor": '', "amp": '1', "phase": '0'}, harmonic);
      break
    case 'envelope':
      var envelope = `
      <div>
        <div class="title-box"><i class="fas fa-code"></i> Огибающая</div>
        <div class="box">
          <p>Параметры</p>
          <input type="text" df-params>
        </div>
      </div>
      `;
      editor.addNode('envelope', 1, 1, pos_x, pos_y, 'envelope', { "params": ''}, envelope );
      break;
    case 'mixer':
        var mixer = `
        <div>
          <div class="title-box"><i class="fas fa-code-branch"></i> Микшер</div>
        </div>
        `;
        editor.addNode('mixer', 3, 1, pos_x, pos_y, 'mixer', {}, mixer);
        break;
    case 'sounddevice':
        var sounddevice = `
        <div>
          <div class="title-box"><i class="fas fa-volume-up"></i> Звуковое устройство</div>
        </div>
        `;
        editor.addNode('sounddevice', 1, 0, pos_x, pos_y, 'sounddevice', {}, sounddevice);
        break;
    case 'dbclick':
        var dbclick = `
        <div>
        <div class="title-box"><i class="fas fa-mouse"></i> Db Click</div>
          <div class="box dbclickbox" ondblclick="showpopup(event)">
          <form>
            Dbl Click to set params
            <div class="modal" style="display:none">
              <div class="modal-content">
                <span class="close" onclick="closemodal(event)">&times;</span>
                Укажите параметры элемента<br/>
                <label for="freq">Частота, Гц </label><input name="freq" type="text" df-freq><br/>
                Амплитуда, 0..1 <input name="amp" type="text" df-amp><br/>
                Фаза, -1..1 <input name="phase" type="text" df-phase><br/>
              </div>
            </div>
          </form>
          </div>
        </div>
        `;
        editor.addNode('dbclick', 1, 1, pos_x, pos_y, 'dbclick', {"freq": 440, "amp": 1, "phase": 0}, dbclick);
        break;
    default:
      editor.addNode('unknown', 0, 0, pos_x, pos_y, 'unknown', {"name": 'unknown'}, "Unknown node type");
      break;
  }
}

var transform = '';
function showpopup(e) {
e.target.closest(".drawflow-node").style.zIndex = "9999";
e.target.children[0].style.display = "block";
//document.getElementById("modalfix").style.display = "block";

//e.target.children[0].style.transform = 'translate('+translate.x+'px, '+translate.y+'px)';
transform = editor.precanvas.style.transform;
editor.precanvas.style.transform = '';
editor.precanvas.style.left = editor.canvas_x +'px';
editor.precanvas.style.top = editor.canvas_y +'px';
console.log(transform);

//e.target.children[0].style.top  =  -editor.canvas_y - editor.container.offsetTop +'px';
//e.target.children[0].style.left  =  -editor.canvas_x  - editor.container.offsetLeft +'px';
editor.editor_mode = "fixed";

}

function closemodal(e) {
 e.target.closest(".drawflow-node").style.zIndex = "2";
 e.target.parentElement.parentElement.style.display  ="none";
 //document.getElementById("modalfix").style.display = "none";
 editor.precanvas.style.transform = transform;
   editor.precanvas.style.left = '0px';
   editor.precanvas.style.top = '0px';
  editor.editor_mode = "edit";
}

function changeModule(event) {
  var all = document.querySelectorAll(".menu ul li");
    for (var i = 0; i < all.length; i++) {
      all[i].classList.remove('selected');
    }
  event.target.classList.add('selected');
}

function changeMode(option) {
//console.log(lock.id);
  if(option == 'lock') {
    lock.style.display = 'none';
    unlock.style.display = 'block';
  } else {
    lock.style.display = 'block';
    unlock.style.display = 'none';
  }
}


/* Functions for synth1561 */

function escapeHtml(string) {
    return string
     .replace(/&/g, "&amp;")
     .replace(/</g, "&lt;")
     .replace(/>/g, "&gt;")
     .replace(/"/g, "&quot;")
     .replace(/'/g, "&#039;");
}

function backend_save_preset() {
  // Сначала получаем список всех файлов в каталоге пресетов,
  // чтобы предложить создать новый файл или перезаписать существующий
  preset_name = ''
  const list_url = "{{ url_for("list_presets") }}"
  fetch(list_url, {
    "method": "GET"
  })
    .then(response => response.json())
    .then(data => {
      Swal.fire({
          title: "Сохранить схему",
          text: "Введите имя файла для сохранения",
          input: "text",
          showCancelButton: true,
      }).then(result => {
          if (result.isConfirmed) {
            preset_name = result.value;
            if (data['files'].includes(result.value)) {
              Swal.fire({
                title: "Файл уже существует",
                html: "Файл <b>" + preset_name + "</b> уже существует, перезаписать?",
                confirmButtonText: "Перезаписать",
                showCancelButton: true,
                cancelButtonText: "Отмена"
              }).then(result => {
                if (result.isConfirmed) {
                  backend_push_preset(preset_name);
                }
              })
            } else {
              backend_push_preset(preset_name);
            }
          }
      });
    });
}

function backend_push_preset(preset_name) {
  console.log('Calling push_preset with ' + preset_name);
  if (!preset_name) return;
  editor_data = editor.export();
  const api_url = "{{ url_for("save_preset") }}";
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify({'name': preset_name, 'data': editor_data})
  })
    .then(response => response.json())
    .then(data => {
      console.log(data);
      //editor.import(data['data']);
    });
}

function backend_play(el) {
  var saved_bgcolor = el.style.backgroundColor;
  el.style.backgroundColor = "red";
  data = editor.export();
  data["command"] = "play";
  const api_url = "{{ url_for("play") }}"
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
  "body": JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      el.style.backgroundColor = saved_bgcolor;
      //Swal.fire({ title: 'Ответ', html: 'Данные: <textarea>'+escapeHtml(JSON.stringify(data, null, 4))+'</textarea>'});
    }
  )
}

function check_scheme() {
  check_btn_el = document.getElementById("check_btn")
  data = editor.export();
  data["command"] = "check";
  const api_url = "{{ url_for("check_params") }}"
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.hasOwnProperty("res") && data["res"] == 'ok') {
        check_btn_el.style.backgroundColor = "green";
      } else {
        check_btn_el.style.backgroundColor = "red";
      }
    }
  )
}

function backend_dev(el) {
  console.log(el);
  data = editor.export();
  data["command"] = "check";
  const api_url = "{{ url_for("check_params") }}"
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      if (data.hasOwnProperty("res") && data["res"] == 'ok') {
        el.style.backgroundColor = "green";
      } else {
        el.style.backgroundColor = "red";
      }
      Swal.fire({ title: 'Ответ', html: 'Данные: <textarea>'+escapeHtml(JSON.stringify(data, null, 4))+'</textarea>'});
    }
  )
}


function backend_load_preset() {
  // Сначала получаем список всех файлов в каталоге пресетов, чтобы выбрать нужный
  preset_name = ''
  const list_url = "{{ url_for("list_presets") }}"
  fetch(list_url, {
    "method": "GET"
  })
    .then(response => response.json())
    .then(data => {
      Swal.fire({
          title: "Выберите схему для загрузки",
          input: "select",
          inputOptions: data['files'],
          inputPlaceholder: "Выберите файл:",
          showCancelButton: true,
      }).then(result => {
          if (result.isConfirmed) {
            preset_name = data['files'][result.value];
          }
          console.log('Got ' + preset_name);
          backend_fetch_preset(preset_name);
          return preset_name;
      });
    });
}

function backend_fetch_preset(preset_name) {
  console.log('Calling load_preset with ' + preset_name);
  if (!preset_name) return;
  const api_url = "{{ url_for("load_preset") }}";
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify({'name': preset_name})
  })
    .then(response => response.json())
    .then(data => {
      //console.log(data);
      editor.import(data['data']);
    });
}