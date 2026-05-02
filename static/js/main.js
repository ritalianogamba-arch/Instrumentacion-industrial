// CONFIGURACION GLOBAL
const CONFIG_TANQUES = {
    T1: { addr: 101, min: 4000, max: 10083 },
    T2: { addr: 102, min: 4000, max: 10812 },
    T3: { addr: 103, min: 4000, max: 6150  },
    T4: { addr: 104, min: 4000, max: 9745  },
    T5: { addr: 105, min: 4000, max: 20000 } 
};

let g_tempT2 = 0;
let g_tempT4 = 0;

// CHART.JS CON ZOOM/PAN ACTIVADO
let c2, c4;
function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: { 
            y: { beginAtZero: false },
            x: { 
                ticks: { maxTicksLimit: 20 } 
            }
        },
        plugins: {
            zoom: {
                pan: { enabled: true, mode: 'x' },
                zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
            }
        }
    };

    c2 = new Chart(document.getElementById('chartT2').getContext('2d'), { 
        type: 'line', 
        data: { labels: [], datasets: [{ label: 'Temp T2 (C)', borderColor: '#E65100', backgroundColor: 'rgba(230, 81, 0, 0.1)', data: [], tension: 0.4, fill: true }] }, 
        options: JSON.parse(JSON.stringify(commonOptions)) 
    });
    
    c4 = new Chart(document.getElementById('chartT4').getContext('2d'), { 
        type: 'line', 
        data: { labels: [], datasets: [{ label: 'Temp T4 (C)', borderColor: '#1976D2', backgroundColor: 'rgba(25, 118, 210, 0.1)', data: [], tension: 0.4, fill: true }] }, 
        options: JSON.parse(JSON.stringify(commonOptions)) 
    });
}

function toggleScaleMode() {
    const isAuto = document.getElementById('autoScale').checked;
    document.getElementById('manualControls').style.display = isAuto ? 'none' : 'inline-block';
}

function applyManualScale() {
    const min = parseFloat(document.getElementById('chartMin').value);
    const max = parseFloat(document.getElementById('chartMax').value);
    [c2, c4].forEach(chart => {
        chart.options.scales.y.min = min;
        chart.options.scales.y.max = max;
        chart.update();
    });
}

function updateCharts(t2, t4) {
    const now = new Date().toLocaleTimeString();
    const isAuto = document.getElementById('autoScale').checked;

    c2.data.labels.push(now); 
    c2.data.datasets[0].data.push(t2);
    
    c4.data.labels.push(now); 
    c4.data.datasets[0].data.push(t4);
    
    if(c2.data.labels.length > 2000) { 
        c2.data.labels.shift(); c2.data.datasets[0].data.shift();
        c4.data.labels.shift(); c4.data.datasets[0].data.shift();
    }

    const totalPoints = c2.data.labels.length;
    if(totalPoints > 30) {
        c2.options.scales.x.min = totalPoints - 30;
        c2.options.scales.x.max = totalPoints - 1;
        c4.options.scales.x.min = totalPoints - 30;
        c4.options.scales.x.max = totalPoints - 1;
    }

    if(isAuto) {
        c2.options.scales.y.min = Math.floor(t2 - 10);
        c2.options.scales.y.max = Math.ceil(t2 + 10);
        c4.options.scales.y.min = Math.floor(t4 - 10);
        c4.options.scales.y.max = Math.ceil(t4 + 10);
    }
    
    c2.update();
    c4.update();
}

// INTERFAZ
function openTab(name, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

// MODBUS
function writeRegister(addr, val) {
     if(addr===300 || addr===301 || addr===400) { alert("Direccion protegida"); return; }
     fetch('/write_register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({address: addr, value: parseInt(val)}) });
}
function writeLevelSP(tankId, percent) {
    const cfg = CONFIG_TANQUES[tankId];
    if(!cfg) return;
    let p = parseFloat(percent); if(p < 0) p = 0; if(p > 100) p = 100;
    const rawVal = Math.round(cfg.min + (p * (cfg.max - cfg.min) / 100));
    writeRegister(cfg.addr, rawVal);
}

// PID
function ioPID(id, action) {
    const suffix = id.toLowerCase();
    if (action === 'read') {
        document.getElementById(`sp-${suffix}`).value = document.getElementById(`read-sp-${suffix}`).innerText;
        document.getElementById(`kp-${suffix}`).value = document.getElementById(`read-kp-${suffix}`).innerText;
        document.getElementById(`ti-${suffix}`).value = document.getElementById(`read-ti-${suffix}`).innerText;
        document.getElementById(`td-${suffix}`).value = document.getElementById(`read-td-${suffix}`).innerText;
        alert("Valores cargados.");
    } else {
        const params = {
            id: id,
            setpoint: document.getElementById(`sp-${suffix}`).value,
            kp: document.getElementById(`kp-${suffix}`).value,
            ti: document.getElementById(`ti-${suffix}`).value,
            td: document.getElementById(`td-${suffix}`).value
        };
        fetch('/update_pid', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(params) })
        .then(r=>r.json()).then(d=>alert(d.success?"Guardado":"Error"));
    }
}
function togglePID_Coil(id) { 
    const btn = document.getElementById(`btn-pid-${id.toLowerCase()}`);
    const isOn = btn.innerText === "ON";
    fetch('/write_coil', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({address: 450, value: !isOn}) });
}
function togglePID_Reg(id) { 
    const btn = document.getElementById(`btn-pid-${id.toLowerCase()}`);
    const isOn = btn.innerText === "ON";
    const newVal = isOn ? 0 : 1;
    fetch('/write_register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({address: 407, value: newVal}) })
    .then(()=>{ fetch('/write_coil', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({address: 350, value: (newVal===1)}) }); });
}

// LOOP
setInterval(() => {
    fetch('/status').then(r=>r.json()).then(d => {
        // Tablas
        let h1=""; d.coils_inputs.forEach((v,i)=>h1+=`<tr><td class="${v?'on':'off'}">%I0.${i}</td></tr>`); document.getElementById('coils_inputs').innerHTML=h1;
        let h2=""; d.coils_outputs.forEach((v,i)=>h2+=`<tr><td class="${v?'on':'off'}">%Q0.${i}</td></tr>`); document.getElementById('coils_outputs').innerHTML=h2;
        let h3=""; 

        const sen=['PT100 T2','PT100 T4','Nivel T1','Nivel T4','Nivel T2','Nivel T3','Nivel T5'];
        d.registers_inputs.forEach((v,i)=>{ 
            let val=v;
            if(i<2) val=((v*75/1000)+0.5).toFixed(1)+" C";
            else if(i===2) val=escalarNivel(v, CONFIG_TANQUES.T1)+" %";
            else if(i===3) val=escalarNivel(v, CONFIG_TANQUES.T4)+" %";
            else if(i===4) val=escalarNivel(v, CONFIG_TANQUES.T2)+" %";
            else if(i===5) val=escalarNivel(v, CONFIG_TANQUES.T3)+" %";
            else if(i===6) val=escalarNivel(v, CONFIG_TANQUES.T5)+" %";
            h3+=`<tr><td>${sen[i]}</td><td>${val}</td></tr>`;
        });
        document.getElementById('registers_inputs').innerHTML=h3;

        let h4="";
        const act=['Resist 1','Valvula','VFD','Reserva'];
        d.registers_outputs.forEach((v,i)=>{
            let val=v;
            if(i===1) val=((v-4000)/16000*100).toFixed(1)+" %";
            if(i===2) val=((v-4000)/16000*50).toFixed(1)+" Hz";
            h4+=`<tr><td>${act[i]}</td><td>${val}</td></tr>`;
        });
        document.getElementById('registers_outputs').innerHTML=h4;

        // PID T2
        if(d.pid_t2.params) {
            document.getElementById('read-sp-t2').innerText = d.pid_t2.params.setpoint;
            document.getElementById('read-kp-t2').innerText = d.pid_t2.params.kp;
            document.getElementById('read-ti-t2').innerText = d.pid_t2.params.ti;
            document.getElementById('read-td-t2').innerText = d.pid_t2.params.td;
            document.getElementById('temp-t2-val').innerText = d.pid_t2.status.temp_actual + " C";
            document.getElementById('out-t2-val').innerText = d.pid_t2.status.salida + " %";
            updateBtn('btn-pid-t2', d.pid_flags.t2_activo);
            updatePermiso('permiso-t2', d.pid_flags.t2_permiso);
        }
        
        // PID T4
        if(d.pid_t4.params) {
            document.getElementById('read-sp-t4').innerText = d.pid_t4.params.setpoint;
            document.getElementById('read-kp-t4').innerText = d.pid_t4.params.kp;
            document.getElementById('read-ti-t4').innerText = d.pid_t4.params.ti;
            document.getElementById('read-td-t4').innerText = d.pid_t4.params.td;
            document.getElementById('temp-t4-val').innerText = d.pid_t4.status.temp_actual + " C";
            document.getElementById('out-t4-val').innerText = d.pid_t4.status.salida + " %";
            updateBtn('btn-pid-t4', d.pid_flags.t4_activo);
            updatePermiso('permiso-t4', d.pid_flags.t4_permiso);
        }

        // Visual
        if(d.registers_inputs.length >= 6) {
            setVisLevel('t2', d.registers_inputs[4], CONFIG_TANQUES.T2);
            let t2 = ((d.registers_inputs[0]*75/1000)).toFixed(1);
            document.getElementById('vis-temp-t2').innerText = t2 + " C";
            
            setVisLevel('t4', d.registers_inputs[3], CONFIG_TANQUES.T4);
            let t4 = ((d.registers_inputs[1]*75/1000)).toFixed(1);
            document.getElementById('vis-temp-t4').innerText = t4 + " C";
            
            setVisLevel('t1', d.registers_inputs[2], CONFIG_TANQUES.T1);
            setVisLevel('t3', d.registers_inputs[5], CONFIG_TANQUES.T3);
            if(d.registers_inputs.length >= 7) setVisLevel('t5', d.registers_inputs[6], CONFIG_TANQUES.T5);
            
            const hT2 = d.pid_flags.t2_activo && d.pid_flags.t2_permiso;
            const hT4 = d.pid_flags.t4_activo && d.pid_flags.t4_permiso;
            
            document.getElementById('vis-lev-t2').style.backgroundColor = hT2 ? '#ff5722' : '#1976d2';
            document.getElementById('vis-lev-t4').style.backgroundColor = hT4 ? '#ff5722' : '#1976d2';

            g_tempT2 = parseFloat(t2);
            g_tempT4 = parseFloat(t4);
        }
        
        if(d.sp_niveles && d.sp_niveles.length >= 5) {
            updateInputIfNoFocus('sp-niv-t1', d.sp_niveles[0], CONFIG_TANQUES.T1);
            updateInputIfNoFocus('sp-niv-t2', d.sp_niveles[1], CONFIG_TANQUES.T2);
            updateInputIfNoFocus('sp-niv-t3', d.sp_niveles[2], CONFIG_TANQUES.T3);
            updateInputIfNoFocus('sp-niv-t4', d.sp_niveles[3], CONFIG_TANQUES.T4);
            updateInputIfNoFocus('sp-niv-t5', d.sp_niveles[4], CONFIG_TANQUES.T5);
        }
        
        if(d.registers_outputs.length >= 3) {
           const val302 = d.registers_outputs[1];
           document.getElementById('valor302').innerText = ((val302-4000)/16000*100).toFixed(1)+" %";
           if(!document.getElementById('slider302').matches(':active')) document.getElementById('slider302').value = val302;
           const val303 = d.registers_outputs[2];
           document.getElementById('valor303').innerText = ((val303-4000)/16000*50).toFixed(1)+" Hz";
           if(!document.getElementById('slider303').matches(':active')) document.getElementById('slider303').value = val303;
        }
    });
}, 2000);

// LOOP LENTO
setInterval(() => {
    updateCharts(g_tempT2, g_tempT4);
}, 60000);

function escalarNivel(v, cfg) {
    let p = ((v - cfg.min)/(cfg.max - cfg.min))*100;
    if(p<0) p=0; if(p>100) p=100;
    return p.toFixed(1);
}
function setVisLevel(id, v, cfg) {
    document.getElementById(`vis-lev-${id}`).style.height = escalarNivel(v, cfg) + "%";
}
function updateInputIfNoFocus(id, rawVal, cfg) {
    if(document.activeElement.id !== id) {
        let p = ((rawVal - cfg.min) / (cfg.max - cfg.min)) * 100;
        if(p<0) p=0; if(p>100) p=100;
        document.getElementById(id).value = Math.round(p);
    }
}
function updateBtn(id, active) {
    const btn = document.getElementById(id);
    if(active) { btn.innerText="ON"; btn.style.background="#2e7d32"; }
    else { btn.innerText="OFF"; btn.style.background="#d32f2f"; }
}
function updatePermiso(id, ok) {
    const s = document.getElementById(id);
    if(ok) { s.innerText="OK"; s.style.color="#2e7d32"; }
    else { s.innerText="BAJO"; s.style.color="#d32f2f"; }
}
function actualizarValorVariador(addr, val) { writeRegister(addr, val); }
function toggleValve(n) {
    const addr = 14 + (n-1);
    const btn = document.getElementById(`valve${n}`);
    if(btn.disabled) return; 
    
    btn.disabled = true; 
    btn.classList.add('transitioning');
    const nState = !btn.classList.contains('open');
    fetch('/write_coil', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({address: addr, value: nState}) })
    .then(r=>r.json()).then(d=>{ 
        if(d.success) { 
             setTimeout(() => {
                btn.disabled = false; 
                btn.classList.remove('transitioning');
                if(nState) { btn.classList.add('open'); btn.classList.remove('closed'); }
                else { btn.classList.add('closed'); btn.classList.remove('open'); }
             }, 16000);
        } else {
             btn.disabled = false; 
             btn.classList.remove('transitioning');
             alert('Error al accionar');
        }
    });
}
function actualizarEstadoValvulas() {
     for(let i=1; i<=7; i++) {
         const btn = document.getElementById(`valve${i}`);
         if(btn.disabled) continue;
         fetch(`/read_coil?address=${14+i-1}`).then(r=>r.json()).then(d=>{
             if(d.success && !btn.disabled) {
                 if(d.value) { btn.classList.add('open'); btn.classList.remove('closed'); }
                 else { btn.classList.add('closed'); btn.classList.remove('open'); }
             }
         });
     }
}

document.addEventListener('DOMContentLoaded', function() {
     document.querySelector('.tab-button').click();
     initCharts();
     setInterval(actualizarEstadoValvulas, 3000);
});
