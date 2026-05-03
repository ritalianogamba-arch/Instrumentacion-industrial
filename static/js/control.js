/**
 * Control Logic - PID, Valves, and Actuators
 */

function ioPID(id, action) {
    const suffix = id.toLowerCase();
    if (action === 'read') {
        const sp = document.getElementById(`read-sp-${suffix}`);
        const kp = document.getElementById(`read-kp-${suffix}`);
        const ti = document.getElementById(`read-ti-${suffix}`);
        const td = document.getElementById(`read-td-${suffix}`);
        
        if (sp) document.getElementById(`sp-${suffix}`).value = sp.innerText;
        if (kp) document.getElementById(`kp-${suffix}`).value = kp.innerText;
        if (ti) document.getElementById(`ti-${suffix}`).value = ti.innerText;
        if (td) document.getElementById(`td-${suffix}`).value = td.innerText;
        
        alert("Valores cargados.");
    } else {
        const params = {
            id: id,
            setpoint: document.getElementById(`sp-${suffix}`).value,
            kp: document.getElementById(`kp-${suffix}`).value,
            ti: document.getElementById(`ti-${suffix}`).value,
            td: document.getElementById(`td-${suffix}`).value
        };
        fetch('/update_pid', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(params)
        })
        .then(r => r.json())
        .then(d => alert(d.success ? "Guardado" : "Error"));
    }
}

function togglePID_Coil(id) {
    const btn = document.getElementById(`btn-pid-${id.toLowerCase()}`);
    if (!btn) return;
    const isOn = btn.innerText === "ON";
    writeCoil(450, !isOn);
}

function togglePID_Reg(id) {
    const btn = document.getElementById(`btn-pid-${id.toLowerCase()}`);
    if (!btn) return;
    const isOn = btn.innerText === "ON";
    const newVal = isOn ? 0 : 1;
    writeRegister(407, newVal)
        .then(() => {
            writeCoil(350, (newVal === 1));
        });
}

function toggleValve(n) {
    const addr = 14 + (n - 1);
    const btn = document.getElementById(`valve${n}`);
    if (!btn || btn.disabled) return;

    btn.disabled = true;
    btn.classList.add('transitioning');
    const nState = !btn.classList.contains('open');

    writeCoil(addr, nState)
        .then(r => r.json())
        .then(d => {
            if (d.success) {
                setTimeout(() => {
                    btn.disabled = false;
                    btn.classList.remove('transitioning');
                    if (nState) {
                        btn.classList.add('open'); btn.classList.remove('closed');
                    } else {
                        btn.classList.add('closed'); btn.classList.remove('open');
                    }
                }, 16000);
            } else {
                btn.disabled = false;
                btn.classList.remove('transitioning');
                alert('Error al accionar');
            }
        });
}

function actualizarEstadoValvulas() {
    for (let i = 1; i <= 7; i++) {
        const btn = document.getElementById(`valve${i}`);
        if (!btn || btn.disabled) continue;
        readCoil(14 + i - 1).then(d => {
            if (d.success && !btn.disabled) {
                if (d.value) {
                    btn.classList.add('open'); btn.classList.remove('closed');
                } else {
                    btn.classList.add('closed'); btn.classList.remove('open');
                }
            }
        });
    }
}

function writeLevelSP(tankId, percent) {
    const cfg = CONFIG_TANQUES[tankId];
    if (!cfg) return;
    let p = parseFloat(percent);
    if (p < 0) p = 0; if (p > 100) p = 100;
    const rawVal = Math.round(cfg.min + (p * (cfg.max - cfg.min) / 100));
    writeRegister(cfg.addr, rawVal);
}

function actualizarValorVariador(addr, val) {
    writeRegister(addr, val);
}
