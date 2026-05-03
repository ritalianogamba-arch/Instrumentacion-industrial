/**
 * Main Entry Point - Orchestration and Initialization
 */

let g_tempT2 = 0;
let g_tempT4 = 0;

// LOOP PRINCIPAL
function mainLoop() {
    fetchStatus().then(d => {
        // --- Tablas (Actualización dirigida para evitar parpadeo y pérdida de estilo) ---
        d.coils_inputs.forEach((v, i) => {
            const el = document.getElementById(`coil-in-${i}`);
            if (el) {
                el.innerText = v ? 'ON' : 'OFF';
                el.className = v ? 'on' : 'off';
            }
        });

        d.coils_outputs.forEach((v, i) => {
            const el = document.getElementById(`coil-out-${i}`);
            if (el) {
                el.innerText = v ? 'ON' : 'OFF';
                el.className = v ? 'on' : 'off';
            }
        });

        d.registers_inputs.forEach((v, i) => {
            const addr = 200 + i;
            const el = document.getElementById(`reg-in-${addr}`);
            if (el) {
                let val = v;
                // Formateo específico por dirección
                if (addr === 200 || addr === 201) val = ((v * 75 / 1000) + 0.5).toFixed(1) + " C";
                else if (addr === 202) val = escalarNivel(v, CONFIG_TANQUES.T1) + " %";
                else if (addr === 204) val = escalarNivel(v, CONFIG_TANQUES.T2) + " %";
                else if (addr === 205) val = escalarNivel(v, CONFIG_TANQUES.T3) + " %";
                else if (addr === 203) val = escalarNivel(v, CONFIG_TANQUES.T4) + " %";
                // T5 usa la misma presión que T4 generalmente en este sistema acoplado
                el.innerText = val;
            }
        });

        d.registers_outputs.forEach((v, i) => {
            const addr = 301 + i;
            const el = document.getElementById(`reg-out-${addr}`);
            if (el) {
                let val = v;
                if (addr === 302) val = ((v - 4000) / 16000 * 50).toFixed(1) + " Hz";
                else if (addr === 303) val = ((v - 4000) / 16000 * 100).toFixed(1);
                else if (addr >= 304) val = ((v - 4000) / 16000 * 100).toFixed(1);
                el.innerText = val;
            }
        });

        // --- PID T2 ---
        if (d.pid_t2.params) {
            document.getElementById('read-sp-t2').innerText = d.pid_t2.params.setpoint;
            document.getElementById('read-kp-t2').innerText = d.pid_t2.params.kp;
            document.getElementById('read-ti-t2').innerText = d.pid_t2.params.ti;
            document.getElementById('read-td-t2').innerText = d.pid_t2.params.td;
            document.getElementById('temp-t2-val').innerText = d.pid_t2.status.temp_actual + " C";
            document.getElementById('out-t2-val').innerText = d.pid_t2.status.salida + " %";
            updateBtn('btn-pid-t2', d.pid_flags.t2_activo);
            updatePermiso('permiso-t2', d.pid_flags.t2_permiso);
        }

        // --- PID T4 ---
        if (d.pid_t4.params) {
            document.getElementById('read-sp-t4').innerText = d.pid_t4.params.setpoint;
            document.getElementById('read-kp-t4').innerText = d.pid_t4.params.kp;
            document.getElementById('read-ti-t4').innerText = d.pid_t4.params.ti;
            document.getElementById('read-td-t4').innerText = d.pid_t4.params.td;
            document.getElementById('temp-t4-val').innerText = d.pid_t4.status.temp_actual + " C";
            document.getElementById('out-t4-val').innerText = d.pid_t4.status.salida + " %";
            updateBtn('btn-pid-t4', d.pid_flags.t4_activo);
            updatePermiso('permiso-t4', d.pid_flags.t4_permiso);
        }

        // --- Visualización ---
        if (d.registers_inputs.length >= 6) {
            setVisLevel('t2', d.registers_inputs[4], CONFIG_TANQUES.T2);
            let t2 = ((d.registers_inputs[0] * 75 / 1000)).toFixed(1);
            document.getElementById('vis-temp-t2').innerText = t2 + " C";

            setVisLevel('t4', d.registers_inputs[3], CONFIG_TANQUES.T4);
            let t4 = ((d.registers_inputs[1] * 75 / 1000)).toFixed(1);
            document.getElementById('vis-temp-t4').innerText = t4 + " C";

            setVisLevel('t1', d.registers_inputs[2], CONFIG_TANQUES.T1);
            setVisLevel('t3', d.registers_inputs[5], CONFIG_TANQUES.T3);
            if (d.registers_inputs.length >= 7) setVisLevel('t5', d.registers_inputs[6], CONFIG_TANQUES.T5);

            const hT2 = d.pid_flags.t2_activo && d.pid_flags.t2_permiso;
            const hT4 = d.pid_flags.t4_activo && d.pid_flags.t4_permiso;

            const levT2 = document.getElementById('vis-lev-t2');
            const levT4 = document.getElementById('vis-lev-t4');
            if (levT2) levT2.style.backgroundColor = hT2 ? '#ff5722' : '#1976d2';
            if (levT4) levT4.style.backgroundColor = hT4 ? '#ff5722' : '#1976d2';

            g_tempT2 = parseFloat(t2);
            g_tempT4 = parseFloat(t4);
        }

        if (d.sp_niveles && d.sp_niveles.length >= 5) {
            updateInputIfNoFocus('sp-niv-t1', d.sp_niveles[0], CONFIG_TANQUES.T1);
            updateInputIfNoFocus('sp-niv-t2', d.sp_niveles[1], CONFIG_TANQUES.T2);
            updateInputIfNoFocus('sp-niv-t3', d.sp_niveles[2], CONFIG_TANQUES.T3);
            updateInputIfNoFocus('sp-niv-t4', d.sp_niveles[3], CONFIG_TANQUES.T4);
            updateInputIfNoFocus('sp-niv-t5', d.sp_niveles[4], CONFIG_TANQUES.T5);
        }

        if (d.registers_outputs.length >= 3) {
            // VFD (302)
            const val302 = d.registers_outputs[1];
            const elVal302 = document.getElementById('valor302');
            if (elVal302) elVal302.innerText = ((val302 - 4000) / 16000 * 50).toFixed(1) + " Hz";
            if (!document.getElementById('slider302').matches(':active')) document.getElementById('slider302').value = val302;

            // Neumática (303)
            const val303 = d.registers_outputs[2];
            const elVal303 = document.getElementById('valor303');
            if (elVal303) elVal303.innerText = ((val303 - 4000) / 16000 * 100).toFixed(1) + " %";
            if (!document.getElementById('slider303').matches(':active')) document.getElementById('slider303').value = val303;
        }
    });
}

// INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function () {
    // Abrir pestaña inicial
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) firstTab.click();

    // Iniciar gráficas
    initCharts();

    // Iniciar loops de actualización
    setInterval(mainLoop, 2000);
    setInterval(() => updateCharts(g_tempT2, g_tempT4), 60000);
    setInterval(actualizarEstadoValvulas, 3000);
});
