/**
 * Control Logic - PID, Valves, and Actuators
 */

const PLC_SENDS_SCALED_LEVEL = (typeof window.PLC_SENDS_SCALED_LEVEL !== 'undefined')
    ? window.PLC_SENDS_SCALED_LEVEL
    : false;

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
    const btnId = `side-btn-temp-${id.toLowerCase()}`;
    const btn = document.getElementById(btnId);
    if (!btn) {
        console.error(`[toggleGenericPID] Botón no encontrado: #${btnId}`);
        return;
    }

    // Verificar bloqueo por pointer-events (más robusto que comparar opacity como string)
    if (btn.style.pointerEvents === 'none') {
        mostrarBloqueoAnimado();
        return;
    }

    const isOn = btn.innerText.trim() === 'ON';
    console.log(`[toggleGenericPID] id=${id}, address=${address}, isOn=${isOn} -> nuevo estado=${!isOn}`);

    // Ambos PIDs (T2 y T4) usan coils para su botón virtual
    writeCoil(address, !isOn)
        .then(r => {
            if (!r) return;
            if (r.status === 403) {
                mostrarBloqueoAnimado();
                return;
            }
            return r.json();
        })
        .then(data => {
            if (data) {
                if (data.success) {
                    // Actualización optimista inmediata (el loop de polling confirmará después)
                    btn.innerText = isOn ? 'OFF' : 'ON';
                    btn.style.background = isOn ? '#c62828' : '#2e7d32';
                } else {
                    console.error(`[toggleGenericPID] Error del servidor: ${data.error}`);
                }
            }
        })
        .catch(err => console.error(`[toggleGenericPID] Error de red: ${err}`));
}

function toggleValve(n, addr) {
    const btn = document.getElementById(`valve${n}`);
    if (!btn || btn.classList.contains('transitioning')) return;

    btn.classList.add('transitioning');
    const nState = !btn.classList.contains('open');

    writeCoil(addr, nState)
        .then(r => {
            if (r && r.status === 403) {
                mostrarBloqueoAnimado();
                btn.classList.remove('transitioning');
                return null;
            }
            return r ? r.json() : null;
        })
        .then(d => {
            if (!d) {
                btn.classList.remove('transitioning');
                return;
            }
            if (d.success) {
                const delay = d.note === 'Escrito en Mock' ? 500 : 15000;
                setTimeout(() => {
                    btn.classList.remove('transitioning');
                }, delay);
            } else {
                btn.classList.remove('transitioning');
                alert('Error al accionar');
            }
        })
        .catch(err => {
            btn.classList.remove('transitioning');
            console.error(err);
        });
}

function writeLevelSP(tankId, percent) {
    const cfg = CONFIG_TANQUES[tankId];
    if (!cfg) return;
    let p = parseFloat(percent);
    if (isNaN(p)) p = 0;
    p = Math.max(0, Math.min(100, p));

    const rawVal = PLC_SENDS_SCALED_LEVEL
        ? Math.round(p)
        : Math.round(cfg.min + (p * (cfg.max - cfg.min) / 100));

    writeRegister(cfg.sp, rawVal).then(r => {
        if (r && r.status === 403) mostrarBloqueoAnimado();
    });
}

function actualizarValorVariador(addr, val) {
    writeRegister(addr, val).then(r => {
        if (r.status === 403) mostrarBloqueoAnimado();
    });
}

function toggleTankMode(index, address) {
    const isAuto = _last_tank_modes && (_last_tank_modes[index - 1] === 1 || _last_tank_modes[index - 1] === true);
    const newValue = !isAuto;

    toggleAutoMode(address, newValue)
        .then(r => {
            if (r.status === 403) {
                mostrarBloqueoAnimado();
            } else if (!r.ok) {
                alert("Error al cambiar modo");
            }
        });
}

// Variable global para tracking de modos
let _last_tank_modes = [];


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
    }).catch(err => console.error("Error toggling mock coil:", err));
}
