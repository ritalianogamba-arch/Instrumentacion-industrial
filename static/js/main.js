/**
 * Main Entry Point - Orchestration and Initialization
 */

let g_tempT2 = 0;
let g_tempT4 = 0;

/**
 * Retorna un color HSL basado en la temperatura para el gradiente visual
 */
function getWaterColor(temp) {
    if (temp < 35) return '#1976d2'; // Azul estándar
    if (temp < 50) return '#4fc3f7'; // Turquesa
    if (temp < 75) return '#ffb74d'; // Naranja claro
    if (temp < 90) return '#ff5722'; // Naranja intenso
    return '#d32f2f'; // Rojo (Crítico)
}

// LOOP PRINCIPAL
function mainLoop() {
    fetch('/status?t=' + new Date().getTime())
        .then(response => response.json())
        .then(d => {
        // --- Actualización de Badge de Estado ---
        const badge = document.getElementById('status-badge');
        const badgeText = document.getElementById('status-text');
        if (badge && badgeText && d.mode) {
            const isSim = d.mode === "Simulado";
            if (isSim) {
                badge.classList.remove('status-online');
                badge.classList.add('status-offline');
                badgeText.innerText = 'Modo Simulación';
            } else {
                badge.classList.remove('status-offline');
                badge.classList.add('status-online');
                badgeText.innerText = 'Sistema Online';
            }

            // Mostrar/Ocultar controles de simulación
            document.querySelectorAll('.sim-only-header, .sim-only-cell').forEach(el => {
                el.style.display = isSim ? '' : 'none';
            });
        }

        // --- Bloqueo Remoto Notice ---
        const lockNotice = document.getElementById('remote-lock-notice');
        if (lockNotice) {
            if (d.remote_lock) {
                lockNotice.classList.add('active');
            } else {
                lockNotice.classList.remove('active', 'centered');
            }
        }

        // --- Modos de Tanque ---
        if (d.tank_modes) {
            d.tank_modes.forEach((isAuto, i) => {
                const index = i + 1;
                const btn = document.getElementById(`btn-mode-${index}`);
                const btnVis = document.getElementById(`btn-mode-t${index}-vis`);
                const status = document.getElementById(`mode-status-${index}`);

                const text = isAuto ? 'AUTO' : 'MANUAL';
                const classAdd = isAuto ? 'mode-auto' : 'mode-manual';
                const classRem = isAuto ? 'mode-manual' : 'mode-auto';

                if (btn) {
                    btn.innerText = text;
                    btn.classList.add(classAdd);
                    btn.classList.remove(classRem);
                }
                if (btnVis) {
                    btnVis.innerText = text;
                    btnVis.classList.add(classAdd);
                    btnVis.classList.remove(classRem);
                }
                if (status) {
                    status.innerText = text;
                    status.className = isAuto ? 'on' : 'off';
                }
            });
        }

        // --- Tablas (Actualización dirigida para evitar parpadeo y pérdida de estilo) ---
        // --- Tablas de Coils ---
        if (d.elementos) {
            d.coils_inputs.forEach((v, i) => {
                const b = d.elementos.botones_ev[i];
                if (!b) return;
                const el = document.getElementById(`coil-in-${b.address}`);
                if (el) {
                    el.innerText = v ? 'ON' : 'OFF';
                    el.className = v ? 'on' : 'off';
                }
            });

            d.coils_outputs.forEach((v, i) => {
                const valv = d.elementos.valvulas[i];
                if (!valv) return;
                // En monitoreo.html usamos index0 para coil-out
                const el = document.getElementById(`coil-out-${i}`);
                if (el) {
                    el.innerText = v ? 'ON' : 'OFF';
                    el.className = v ? 'on' : 'off';
                }
            });
        }

        d.registers_inputs.forEach((v, i) => {
            // Buscamos el elemento correspondiente en el DOM por su ID de dirección
            // Nota: En monitoreo.html los IDs son 'reg-in-{{ sensor.address }}'
            // El backend envía registers_inputs en el orden de LISTA_SENSORES.
            // Para ser 100% dinámicos, el backend debería enviar un mapa o el sensor object.
            // Por ahora, usamos el índice para obtener el sensor del DOM si es posible,
            // o confiamos en que el backend envíe los valores escalados si es posible.
            
            // Refactorización: El backend ya provee get_system_data. 
            // Podríamos obtener las direcciones reales. 
            // Por ahora, mantenemos la compatibilidad con el DOM actual.
        });

        // Actualización específica por ID para asegurar precisión sin importar el orden
        if (d.elementos && d.elementos.sensores) {
            d.elementos.sensores.forEach((s, i) => {
                const v = d.registers_inputs[i];
                const el = document.getElementById(`reg-in-${s.address}`);
                if (el) {
                    let val = v;
                    if (s.nombre.toLowerCase().includes("temp")) val = ((v * 75 / 1000) + 0.5).toFixed(1) + " C";
                    else if (s.nombre.toLowerCase().includes("presion")) {
                         // Buscar config de tanque asociada si existe
                         const tKey = Object.keys(CONFIG_TANQUES).find(k => CONFIG_TANQUES[k].sensor === s.address);
                         if (tKey) val = escalarNivel(v, CONFIG_TANQUES[tKey]) + " %";
                         else val = v;
                    }
                    el.innerText = val;
                }
            });
        }

        d.registers_outputs.forEach((v, i) => {
            // El backend envía registers_outputs en el orden de LISTA_ACTUADORES.
        });

        if (d.elementos && d.elementos.salidas_analogicas) {
            d.elementos.salidas_analogicas.forEach((a, i) => {
                const v = d.registers_outputs[i];
                const el = document.getElementById(`reg-out-${a.address}`);
                if (el) {
                    let val = v;
                    if (a.address === 302) val = ((v - 4000) / 16000 * 50).toFixed(1) + " Hz";
                    else val = ((v - 4000) / 16000 * 100).toFixed(1) + " %";
                    el.innerText = val;
                }
            });
        }


        // --- Sincronización de Válvulas Visuales ---
        // Coils 14-21 corresponden a EV1-EV8
        d.coils_outputs.forEach((v, i) => {
            const index = i + 1;
            const btn = document.getElementById(`valve${index}`);
            if (btn && !btn.classList.contains('transitioning')) {
                if (v) {
                    btn.classList.add('open');
                    btn.classList.remove('closed');
                } else {
                    btn.classList.add('closed');
                    btn.classList.remove('open');
                }
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
        if (d.elementos && d.elementos.tanques) {
            d.elementos.tanques.forEach((t, i) => {
                const index = i + 1;
                // Encontrar el sensor de presión del tanque
                const sPresionIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_presion);
                if (sPresionIdx !== -1) {
                    const rawLevel = d.registers_inputs[sPresionIdx];
                    const tankKey = `T${index}`;
                    setVisLevel(`t${index}`, rawLevel, CONFIG_TANQUES[tankKey]);
                    
                    const levEl = document.getElementById(`vis-lev-t${index}`);
                    const levValEl = document.getElementById(`vis-lev-t${index}-val`);
                    if (levValEl) levValEl.innerText = escalarNivel(rawLevel, CONFIG_TANQUES[tankKey]) + "%";
                    
                    // Encontrar el sensor de temperatura si tiene
                    if (t.sensor_de_temperatura) {
                        const sTempIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_temperatura);
                        if (sTempIdx !== -1) {
                            const rawTemp = d.registers_inputs[sTempIdx];
                            const tempC = ((rawTemp * 75 / 1000) + 0.5).toFixed(1);
                            const tempEl = document.getElementById(`vis-temp-t${index}`);
                            const tempBarEl = document.getElementById(`temp-fill-t${index}`);
                            const tempBulbEl = document.getElementById(`temp-bulb-t${index}`);
                            const color = getWaterColor(parseFloat(tempC));

                            if (tempEl) tempEl.innerText = tempC + " C";
                            if (tempBarEl) {
                                tempBarEl.style.height = Math.min(100, Math.max(0, parseFloat(tempC))) + "%";
                                tempBarEl.style.backgroundColor = color;
                            }
                            if (tempBulbEl) tempBulbEl.style.backgroundColor = color;
                            if (levEl) levEl.style.backgroundColor = color;
                            
                            if (index === 2) g_tempT2 = parseFloat(tempC);
                            if (index === 4) g_tempT4 = parseFloat(tempC);
                        }
                    } else {
                        if (levEl) levEl.style.backgroundColor = getWaterColor(20);
                    }
                }
                
                // Actualizar SP Inputs
                const spValRaw = d.sp_niveles[i];
                const tankKey = `T${index}`;
                updateInputIfNoFocus(`sp-niv-t${index}-vis`, spValRaw, CONFIG_TANQUES[tankKey]);
            });
        }

        // --- Actuadores Manuales ---
        if (d.elementos && d.elementos.salidas_analogicas) {
            d.elementos.salidas_analogicas.forEach((a, i) => {
                const val = d.registers_outputs[i];
                const slider = document.getElementById(`slider${a.address}`);
                const display = document.getElementById(`valor${a.address}`);
                
                if (slider && !slider.matches(':active')) slider.value = val;
                if (display && !slider.matches(':active')) {
                    if (a.address === 302) {
                        const hz = ((val - 4000) / 16000 * 50).toFixed(1);
                        display.innerText = hz + " Hz";
                        
                        // Actualizar Bomba en Visual
                        const pumpSpin = document.getElementById("pump-spin");
                        const pumpLabel = document.getElementById("vfd-val-label");
                        if (pumpLabel) pumpLabel.innerText = hz + " Hz";
                        if (pumpSpin) {
                            if (parseFloat(hz) > 0.5) {
                                pumpSpin.classList.add('pump-spin-anim');
                                // Escalar duración: 50Hz -> 0.4s (rápido), 10Hz -> 2s (lento)
                                const duration = (20 / parseFloat(hz)).toFixed(2);
                                pumpSpin.style.animationDuration = duration + "s";
                            } else {
                                pumpSpin.classList.remove('pump-spin-anim');
                                pumpSpin.style.transform = "rotate(0deg)";
                            }
                        }
                    } else {
                        const perc = ((val - 4000) / 16000 * 100).toFixed(1);
                        display.innerText = perc + " %";
                        
                        // Actualizar Válvula Neumática en Visual
                        if (a.address === 303) {
                            const vnLabel = document.getElementById("vn-val-label");
                            if (vnLabel) vnLabel.innerText = perc + " %";
                        }
                    }
                }
            });
        }

        // --- Actualización de Modal Detallado ---
        if (typeof g_currentModalTankId !== 'undefined' && g_currentModalTankId !== null) {
            const id = g_currentModalTankId;
            const t = d.elementos.tanques[id - 1];
            const sPresionIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_presion);
            
            let levelVal = 0;
            let tempVal = "--";
            let levelAbs = "--";

            if (sPresionIdx !== -1) {
                const rawLevel = d.registers_inputs[sPresionIdx];
                const tankKey = `T${id}`;
                levelVal = escalarNivel(rawLevel, CONFIG_TANQUES[tankKey]);
                // Cálculo de volumen actual basado en la capacidad total
                levelAbs = (levelVal * t.volumen / 100).toFixed(2);
            }

            if (t.sensor_de_temperatura) {
                const sTempIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_temperatura);
                if (sTempIdx !== -1) {
                    tempVal = ((d.registers_inputs[sTempIdx] * 75 / 1000) + 0.5).toFixed(1);
                }
            }

            // Actualizar colores de válvulas en el modal (ejemplo simplificado)
            const v1 = document.getElementById("modal-v1");
            const v2 = document.getElementById("modal-v2");
            // Usamos las válvulas asociadas al tanque (superior e inferior)
            const vSupIdx = d.elementos.valvulas.findIndex(v => v.address === t.valvula_superior);
            const vInfIdx = d.elementos.valvulas.findIndex(v => v.address === t.valvula_inferior);
            
            if (v1 && vSupIdx !== -1) v1.style.background = d.coils_outputs[vSupIdx] ? "#28a745" : "#ff8c00";
            if (v2 && vInfIdx !== -1) v2.style.background = d.coils_outputs[vInfIdx] ? "#28a745" : "#ff8c00";

            if (typeof updateTankModal === "function") {
                updateTankModal(levelVal, tempVal, levelAbs);
            }
        }
    }).catch(err => console.error("Error en mainLoop:", err));
}

// INICIALIZACIÓN
document.addEventListener('DOMContentLoaded', function () {
    // Abrir pestaña inicial
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) firstTab.click();

    // Iniciar gráficas
    initCharts();

    // Iniciar loops de actualización
    setInterval(mainLoop, 500);
    setInterval(() => updateCharts(g_tempT2, g_tempT4), 60000);
});
