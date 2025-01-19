var id = document.getElementById("drawflow");
const editor = new Drawflow(id);
editor.reroute = true;
const dataToImport = {"drawflow":{"Home":{"data":{"1":{"id":1,"name":"welcome","data":{},"class":"welcome","html":"\n    <div>\n      <div class=\"title-box\">&#128587; <b>Добро пожаловать!</b></div>\n      <div class=\"box\">\n        <p> <b>Краткая справка:</b></p><br>\n\n        <p><b>Добавляйте элементы</b>, перетаскивая их из палитры слева<br><br>\n           <b>Чтобы соединить элементы</b>, перетащите выход одного ко входу другого<br><br>\n           <b>Для удаления</b> выберите элемент и нажмите клавишу Delete<br><br>\n           <b>Для изменения масштаба</b> изображения вращайте колёсико мыши, нажав Ctrl</p>\n      </div>\n    </div>\n    ","typenode": false, "inputs":{},"outputs":{},"pos_x":10,"pos_y":10}}}}}
editor.start();
editor.import(dataToImport);

// Events!
// TODO: disable logging in prod
editor.on('nodeCreated', function(id) {
  console.log("Node created " + id);
  backend_check();
})

editor.on('nodeRemoved', function(id) {
  console.log("Node removed " + id);
  backend_check();
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
  backend_check();
})

editor.on('connectionRemoved', function(connection) {
  console.log('Connection removed');
  console.log(connection);
  backend_check();
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
      editor.addNode('tone', 0,  1, pos_x, pos_y, 'tone', {"freq": '220', "amp": '1', "phase": '0'}, tone);
      break;
    case 'harmonic':
      var html = `
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
      editor.addNode('harmonic', 1,  1, pos_x, pos_y, 'harmonic', { "factor": '2', "amp": '1', "phase": '0'}, html);
      break
    case 'envelope':
      var html = `
      <div>
        <div class="title-box"><i class="fas fa-code"></i> Огибающая</div>
        <div class="box">
          <p>Параметры</p>
          <input type="text" df-params>
        </div>
      </div>
      `;
      editor.addNode('envelope', 1, 1, pos_x, pos_y, 'envelope', { "params": ''}, html );
      break;
    case 'mixer':
        var mixer = `
        <div>
          <div class="title-box"><i class="fas fa-code-branch"></i> Микшер</div>
        </div>
        `;
        editor.addNode('mixer', 3, 1, pos_x, pos_y, 'mixer', {}, mixer);
        break;
    case 'modulator':
        var html = `
        <div>
          <div class="title-box"><i class="fas fa-code-branch"></i> Модулятор</div>
          <div class="box">
            <p>Глубина</p>
            D: <input class="short" type="text" df-depth>
          </div>
        </div>
        `;
        editor.addNode('modulator', 2, 1, pos_x, pos_y, 'modulator', {'depth': '1'}, html);
        break;
    case 'sounddevice':
        if (editor.getNodesFromName('sounddevice').length > 0) {
          Swal.fire({
            title: 'Недопустимое действие',
            text: 'На схеме уже присутствует элемент "Звуковое устройство". Элемент данного типа может быть только один.'
          });
          break;
        }
        var html = `
        <div>
          <div class="title-box"><i class="fas fa-volume-up"></i> Звуковое устройство</div>
          <div class="box">
            <p>Параметры</p>
            Громк: <input class="short" type="text" df-volume>
            &nbsp;Длит: <input class="short" type="text" df-duration>
          </div>
        </div>
        `;
        editor.addNode('sounddevice', 1, 0, pos_x, pos_y, 'sounddevice', {'volume': 1, 'duration': 5}, html);
        break;
    case 'oscilloscope':
        if (editor.getNodesFromName('oscilloscope').length > 0) {
          Swal.fire({
            title: 'Недопустимое действие',
            text: 'На схеме уже присутствует элемент "Осциллограф". Элементов данного типа должно быть не больше одного.'
          });
          break;
        }
        var html = `
        <div>
          <div class="title-box"><i class="fas fa-volume-up"></i> Осциллограф</div>
          <div class="box">
            <button onclick="backend_display_signal()">Показать сигнал</button>
          </div>
        </div>
        `;
        editor.addNode('oscilloscope', 1, 0, pos_x, pos_y, 'oscilloscope', {}, html);
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

function set_schema_name(name) {
  editor.schema_name = name;
  document.getElementById("ctrl-btn").innerHTML = (name?name:'Без имени');
}

function backend_display_signal() {
  var node_id = 12
  data = editor.export();
  data['output_node'] = node_id;
  const api_url = "{{ url_for("get_samples") }}";
  fetch(api_url, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => {
      Swal.fire({
        title: 'Осциллограф',
        width: 700,
        html: '<div id="my_dataviz" style="text-align:left;">Зависимость значения сигнала в указанной точке схемы от времени. Выделите фрагмент графика, чтобы увеличить масштаб. Двойной щелчок на графике -- вернуться к исходному масштабу.</div',
        didOpen: () => {
          show_chart("#my_dataviz", data['data'].split(','));
        }
      });
    }
  )
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
          inputValue: (editor.schema_name?editor.schema_name:''),
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
  set_schema_name(preset_name);
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


function backend_check(el) {
  show_modal = true;
  if (!el) {
    el = document.getElementById("check_btn");
    show_modal = false;
  }
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
      if (show_modal) {
        if (data.hasOwnProperty("res") && data["res"] == 'ok') {
          title = "Схема корректна";
          html = "Ошибки не найдены, можно синтезировать звук";
          if (data["msg"]["warn"].length) {
            html += '<ul><li>Предупреждение: ' + data["msg"]["warn"].join('<li>') + '</ul>';
          }
        } else {
          title = "Схема некорректна";
          html = "<div style='text-align: left;'><p>Найдены следующие ошибки:</p>";
          if (data["msg"]["critical"].length) {
            html += '<ul><li>' + data["msg"]["critical"].join('<li>') + '</ul>';
          }
          if (data["msg"]["error"].length) {
            html += '<ul><li>' + data["msg"]["error"].join('<li>') + '</ul>';
          }
          //html += 'Данные: <textarea>'+escapeHtml(JSON.stringify(data, null, 4))+'</textarea>';
        }
        Swal.fire({title: title, html: html});
      }
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
      set_schema_name(preset_name);
    });
}


function show_modal_help(item) {
  switch (item) {
    case 'tone':
      title = "Генератор тона";
      html = "<div style='text-align: left;'>" +
      "<p>Генератор тона -- элемент, генерирующий синусоидальный сигнал с указанной частотой <em>F</em>, относительной амплитудой <em>A</em> (0..1) и фазой <em>ф</em> (-1..1, значения соответствуют сдвигу фазы на -pi и pi сответственно).</p>" +
      "</div>";
      break;
    case 'harmonic':
      title = "Генератор гармоники";
      html = "<div style='text-align: left;'>" +
      "<p>Генератор гармоники -- элемент, генерирующий синусоидальный сигнал с относительной амплитудой <em>A</em> (0..1) и фазой <em>ф</em> (-1..1, значения соответствуют сдвигу фазы на -pi и pi сответственно). Значение частоты соответствует частоте 'родительского' генератора тона, умноженной на целочисленный коэффициент <em>k</em>.</p>" +
      "</div>";
      break;
    case 'envelope':
      title = "Огибающая";
      html = "<div style='text-align: left;'>" +
      "<p>Огибающая -- элемент, задающий изменение амплитуды поданного на его вход сигнала по времени. Параметры элемента задаются в виде списка кортежей, каждый элемент которого представляет собой пару значений (время, амплитуда). Пример: (0,0),(1,1),(5,0) -- амплитуда сигнала возрастает с 0 до 1 в течение первой секунды, затем снижается до 0 в течение следующих 4 секунд.</p>" +
      "<p>Примечание: при синтезе звука автоматически добавляется снижение амплитуды до 0 между последней заданной точкой огибающей и окончанием звучания.</p>" +
      "</div>";
      break;
    case 'sounddevice':
      title = "Звуковое устройство";
      html = "<div style='text-align: left;'>" +
      "<p>Звуковое устройство -- элемент, представляющий звуковое устройство компьютера. На схеме обязательно должно присутствовать единственное звуковое устройство. Позволяет задать общую длительность генерируемого звука в секундах и относительный уровень громкости (1 соответствует 100%)" +
      "</div>";
      break;
    case 'mixer':
      title = "Микшер";
      html = "<div style='text-align: left;'>" +
      "<p>Микшер -- элемент, суммирующий все поступающие на его вход сигналы. К каждому входу микшера можно подключить несколько элементов.</p>" +
      "</div>";
      break;
    case 'modulator':
      title = "Модулятор";
      html = "<div style='text-align: left;'>" +
      "<p>Модулятор -- элемент, выполняющий перемножение поступающих на его вход сигналов. Параметр 'Глубина' задает степень влияния управляющего сигнала (нижний вход) на основной сигнал (верхний вход). На выходе элемента получается сигнал, включающий составляющие с частотами, равными сумме и разности входных частот (по формуле </b>sin(a) * sin(b) = 1/2(cos(a-b) - cos(a+b))</b>.</p>" +
      "</div>";
      break;
    case 'oscilloscope':
      title = "Осциллограф";
      html = "<div style='text-align: left;'>" +
      "<p>Позволяет посмотреть график изменения сигнала в точке подключения осциллографа. На схеме может присутствовать не более одного осциллографа. Если осциллограф присутствует на схеме, но не подключён, он покажет сигнал на выходе звукового устройства.</p>" +
      "</div>";
      break;
    default:
      title = "Справка";
      html = "<div style='text-align: left;'>" +
      "<p>Какая-то справка.</p>" +
      "</div>";
      break;
  }

  Swal.fire({
    title: title,
    html: html
  });
}


editor.on('import', function(data) {
  console.log("Performed import");
  backend_check();
})


function show_chart(container, samples) {
  if (!container) {
    console.log('No container element ' + container);
	//return;
  }

  //prepare chart data
  data = []
  for (var i=0; i<samples.length; i++) {
    data.push({'t':parseFloat((i/44100).toFixed(5)), 'v':parseFloat(samples[i])});
  }
  console.log(data);

  //return;
  // set the dimensions and margins of the graph
  var margin = {top: 10, right: 30, bottom: 30, left: 60},
    width = 660 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select(container)
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

    // Add X axis
    var x = d3.scaleLinear()
      .domain([0, d3.max(data, function(d) { return d.t; })])
      .range([ 0, width ]);
    xAxis = svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
      .domain([minval = d3.min(data, function(d) { return -Math.abs(d.v); }), -minval])
      .range([ height, 0 ]);
    yAxis = svg.append("g")
      .call(d3.axisLeft(y))
      .call(g => g.append("text")
          .attr("x", -margin.left)
          .attr("y", 0)
          .attr("fill", "currentColor")
          .attr("text-anchor", "start")
          .text("Уровень сигнала"));

    d3.selectAll("g.y-axis g.tick")
        .append("line")
        .classed("grid-line", true)
        .attr("x1", 0)
        .attr("y1", 0)
        .attr("x2", width)
        .attr("y2", 0);

    // Add a clipPath: everything out of this area won't be drawn.
    var clip = svg.append("defs").append("svg:clipPath")
        .attr("id", "clip")
        .append("svg:rect")
        .attr("width", width )
        .attr("height", height )
        .attr("x", 0)
        .attr("y", 0);

    // Add brushing
    var brush = d3.brushX()                   // Add the brush feature using the d3.brush function
        .extent( [ [0,0], [width,height] ] )  // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
        .on("end", updateChart)               // Each time the brush selection changes, trigger the 'updateChart' function

    // Create the line variable: where both the line and the brush take place
    var line = svg.append('g')
      .attr("clip-path", "url(#clip)")

    // Add the line
    line.append("path")
      .datum(data)
      .attr("class", "line")  // I add the class line to be able to modify this line later on.
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
        .x(function(d) { return x(d.t) }) //d.date
        .y(function(d) { return y(d.v) })
        )

    // Add the brushing
    line
      .append("g")
        .attr("class", "brush")
        .call(brush);

    // A function that set idleTimeOut to null
    var idleTimeout
    function idled() { idleTimeout = null; }

    // A function that update the chart for given boundaries
    function updateChart() {

      // What are the selected boundaries?
      extent = d3.event.selection

      // If no selection, back to initial coordinate. Otherwise, update X axis domain
      if(!extent){
        if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
        x.domain([ 4,8])
      }else{
        x.domain([ x.invert(extent[0]), x.invert(extent[1]) ])
        line.select(".brush").call(brush.move, null) // This remove the grey brush area as soon as the selection has been done
      }

      // Update axis and line position
      xAxis.transition().duration(1000).call(d3.axisBottom(x))
      line
          .select('.line')
          .transition()
          .duration(1000)
          .attr("d", d3.line()
            .x(function(d) { return x(d.t) }) //d.date
            .y(function(d) { return y(d.v) })
          )
    }

    // If user double click, reinitialize the chart
    svg.on("dblclick",function(){
      x.domain(d3.extent(data, function(d) { return d.t; })) //d.date
      xAxis.transition().call(d3.axisBottom(x))
      line
        .select('.line')
        .transition()
        .attr("d", d3.line()
          .x(function(d) { return x(d.t) }) //d.date
          .y(function(d) { return y(d.v) })
      )
    });

//})
}