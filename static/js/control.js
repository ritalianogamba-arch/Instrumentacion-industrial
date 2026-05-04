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
        .then(r => {
            if (r.status === 403) { mostrarBloqueoAnimado(); return null; }
            return r.json();
        })
        .then(d => {
            if (d) alert(d.success ? "Guardado" : "Error");
        });
    }
}

function toggleGenericPID(id, address, type) {
    const btn = document.getElementById(`btn-pid-${id.toLowerCase()}`);
    if (!btn) return;
    const isOn = btn.innerText === "ON";
    
    if (type === 'coil') {
        writeCoil(address, !isOn).then(r => {
            if (r.status === 403) mostrarBloqueoAnimado();
        });
    } else {
        const newVal = isOn ? 0 : 1;
        writeRegister(407, newVal) // T4 usa el registro 407 para comando
            .then(r => {
                if (r.status === 403) {
                    mostrarBloqueoAnimado();
                    return null;
                }
                return writeCoil(address, (newVal === 1));
            });
    }
}

function toggleValve(n, addr) {
    const btn = document.getElementById(`valve${n}`);
    if (!btn || btn.disabled) return;

    btn.disabled = true;
    btn.classList.add('transitioning');
    const nState = !btn.classList.contains('open');

    writeCoil(addr, nState)
        .then(r => {
            if (r.status === 403) {
                mostrarBloqueoAnimado();
                btn.disabled = false;
                btn.classList.remove('transitioning');
                return null;
            }
            return r.json();
        })
        .then(d => {
            if (!d) return;
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

function writeLevelSP(tankId, percent) {
    const cfg = CONFIG_TANQUES[tankId];
    if (!cfg) return;
    let p = parseFloat(percent);
    if (p < 0) p = 0; if (p > 100) p = 100;
    const rawVal = Math.round(cfg.min + (p * (cfg.max - cfg.min) / 100));
    writeRegister(cfg.addr, rawVal).then(r => {
        if (r.status === 403) mostrarBloqueoAnimado();
    });
}

function actualizarValorVariador(addr, val) {
    writeRegister(addr, val).then(r => {
        if (r.status === 403) mostrarBloqueoAnimado();
    });
}

function toggleTankMode(index, address) {
    const btnId = `btn-mode-${index}`;
    const btnVisId = `btn-mode-t${index}-vis`;
    const btn = document.getElementById(btnId);
    const btnVis = document.getElementById(btnVisId);
    
    if (!btn) return;
    const isAuto = btn.classList.contains('mode-auto');
    const newValue = !isAuto;
    
    toggleAutoMode(address, newValue)
        .then(r => {
            if (r.status === 403) {
                // Bloqueado
                mostrarBloqueoAnimado();
            } else if (!r.ok) {
                alert("Error al cambiar modo");
            }
        });
}

/**
 * Muestra visualmente que el mando está bloqueado
 */
function mostrarBloqueoAnimado() {
    const notice = document.getElementById('remote-lock-notice');
    if (!notice) return;
    
    notice.classList.add('active', 'centered');
    setTimeout(() => {
        notice.classList.remove('centered');
    }, 2000);
}

function mockToggleInput(address) {
    fetch('/mock/toggle_input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: address })
    });
}
