/**
 * Main Entry Point - Orchestration and Initialization
 */

// Configuración de escalamiento de temperatura (sincronizado con config/plc.py)
// El valor real lo inyecta Flask en index.html como window.PLC_SENDS_SCALED_TEMP
const PLC_SENDS_SCALED_TEMP = (typeof window.PLC_SENDS_SCALED_TEMP !== 'undefined')
    ? window.PLC_SENDS_SCALED_TEMP
    : false; // default: escalamiento en el SCADA (PLC envía raw)

function rawToCelsius(raw) {
    if (PLC_SENDS_SCALED_TEMP) return parseFloat(raw).toFixed(1);
    return ((raw * 75 / 1000) + 0.5).toFixed(1);
}

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
        // --- Cache Global de Elementos ---
        _elementos_cache = d.elementos;
        _last_tank_modes = d.tank_modes;

        // --- Actualización de Badge de Estado y Lock ---
        const badge = document.getElementById('status-badge');
        const badgeText = document.getElementById('status-text');
        const plcOverlay = document.getElementById('plc-disconnect-overlay');
        if (badge && badgeText && d.mode) {
            const isOffline = d.mode === "Desconectado";
            badge.className = isOffline ? 'status-badge status-offline' : 'status-badge status-online';
            badgeText.innerText = isOffline ? 'PLC Desconectado' : 'Sistema Online';
            if (plcOverlay) plcOverlay.style.display = isOffline ? 'flex' : 'none';
        }

        const lockNotice = document.getElementById('remote-lock-notice');
        if (lockNotice) {
            if (d.remote_lock) {
                lockNotice.classList.add('active');
                // Bloquear visualmente botones de control
                document.querySelectorAll('[id^="side-btn-temp-"], [id^="btn-group-"]').forEach(btn => {
                    btn.style.opacity = "0.5";
                    btn.style.pointerEvents = "none";
                });
            } else {
                lockNotice.classList.remove('active', 'centered');
                document.querySelectorAll('[id^="side-btn-temp-"], [id^="btn-group-"]').forEach(btn => {
                    btn.style.opacity = "1";
                    btn.style.pointerEvents = "auto";
                });
            }
        }

        // --- Sincronización de Sidebar (Actuadores Globales) ---
        if (d.elementos && d.elementos.salidas_analogicas) {
            d.elementos.salidas_analogicas.forEach((a, i) => {
                const val = d.registers_outputs[i];
                const cfg = CONFIG_ACTUADORES[a.address];
                if (!cfg) return;

                const scale = (cfg.unidad === 'Hz' || cfg.unit === 'Hz') ? 50 : 100;
                const scaledVal = ((val - cfg.min) / (cfg.max - cfg.min) * scale).toFixed(1);

                // Update Sidebar Horizontal Controls
                const sideSlider = document.getElementById(`slider-${a.address}-side`);
                const sideInput = document.getElementById(`input-${a.address}-side`);
                const sideLabel = document.getElementById(`valor-${a.address}-side`);

                if (sideSlider && !sideSlider.matches(':active')) sideSlider.value = val;
                if (sideInput && document.activeElement !== sideInput) sideInput.value = scaledVal;
                if (sideLabel) sideLabel.innerText = scaledVal + " " + (cfg.unidad || cfg.unit || '%');

                // Sync Visual Schematic Labels
                const vLabel = document.getElementById(a.unidad === 'Hz' ? "vfd-val-label" : "vn-val-label");
                if (vLabel && !a.nombre.includes("Resistencia")) vLabel.innerText = scaledVal + " " + (cfg.unidad || cfg.unit || '%');

                if (a.unidad === 'Hz') {
                    const pumpSpin = document.getElementById("pump-spin");
                    if (pumpSpin) {
                        if (parseFloat(scaledVal) > 0.5) {
                            pumpSpin.classList.add('pump-spin-anim');
                            pumpSpin.style.animationDuration = (20 / parseFloat(scaledVal)).toFixed(2) + "s";
                        } else {
                            pumpSpin.classList.remove('pump-spin-anim');
                            pumpSpin.style.transform = "rotate(0deg)";
                        }
                    }
                }
            });
        }

        // --- Sincronización de Sidebar (Control de Nivel) ---
        if (d.sp_niveles) {
            d.sp_niveles.forEach((sp, i) => {
                const tankIdx = i + 1;
                const input = document.getElementById(`side-sp-nivel-t${tankIdx}`);
                if (input && document.activeElement !== input) {
                    const cfg = CONFIG_TANQUES[`T${tankIdx}`];
                    input.value = PLC_SENDS_SCALED_LEVEL
                        ? Math.round(sp)
                        : Math.round(((sp - cfg.min) / (cfg.max - cfg.min)) * 100);
                }
            });
        }

        // --- Sincronización de Sidebar (Control de Temperatura) ---
        [2, 4].forEach(tIdx => {
            const pidKey = `pid_t${tIdx}`;
            const pidData = d[pidKey];
            if (!pidData) return;

            const pidActive = d.pid_flags[`t${tIdx}_activo`];
            const tObj = d.elementos.tanques[tIdx-1];
            const sPresionIdx = d.elementos.sensores.findIndex(s => s.address === tObj.sensor_de_presion);
            
            // LED Seguro
            // LED Seguro (usando condición de nivel del PLC si está disponible)
            const led = document.getElementById(`side-led-seguro-t${tIdx}`);
            let isSafe;
            if (Array.isArray(d.condiciones_nivel) && typeof d.condiciones_nivel[tIdx-1] !== 'undefined') {
                // Valor 1 = seguro, 0 = peligro
                isSafe = d.condiciones_nivel[tIdx-1] === 1 || d.condiciones_nivel[tIdx-1] === true;
            } else {
                // Fallback a la lógica anterior usando presión cruda
                const rawLevel = d.registers_inputs[sPresionIdx];
                isSafe = rawLevel > (tObj.condicion_de_nivel || 400);
            }
            if (led) led.className = 'led-indicator ' + (isSafe ? 'active' : 'danger');

            // Botón Resistance
            // Botón Resistance (Sidebar y Pestaña PID)
            const btnSide = document.getElementById(`side-btn-temp-t${tIdx}`);
            const btnPID = document.getElementById(`btn-pid-t${tIdx}`);
            
            [btnSide, btnPID].forEach(btn => {
                if (btn) {
                    btn.innerText = pidActive ? 'ON' : 'OFF';
                    btn.style.background = pidActive ? '#2e7d32' : '#c62828';
                }
            });

            // Setpoint e Inputs PID — solo sincronizar si el acordeón está cerrado
            const accordion = document.getElementById(`side-pid-accordion-t${tIdx}`);
            const isEditing = accordion && accordion.classList.contains('expanded');

            const spInput = document.getElementById(`side-sp-temp-t${tIdx}`);
            if (spInput && document.activeElement !== spInput && !isEditing) spInput.value = pidData.params.setpoint;

            if (!isEditing) {
                const kp = document.getElementById(`side-kp-t${tIdx}`);
                const ti = document.getElementById(`side-ti-t${tIdx}`);
                const td = document.getElementById(`side-td-t${tIdx}`);
                if (kp) kp.value = pidData.params.kp;
                if (ti) ti.value = pidData.params.ti;
                if (td) td.value = pidData.params.td;
            }
        });

        // --- Visualización de Tanques y Válvulas ---
        d.coils_outputs.forEach((v, i) => {
            const btn = document.getElementById(`valve${i + 1}`);
            if (btn) {
                const wasOpen = btn.classList.contains('open');
                const isTransitioning = btn.classList.contains('transitioning');
                
                // Si cambió de estado externamente (no estamos nosotros transicionando)
                if (v !== wasOpen && !isTransitioning) {
                    btn.classList.add('transitioning');
                    setTimeout(() => {
                        btn.classList.remove('transitioning');
                        btn.className = v ? 'valve-industrial open' : 'valve-industrial closed';
                    }, 15000); // Parpadeo de 15 segundos
                } else if (!isTransitioning) {
                    btn.className = v ? 'valve-industrial open' : 'valve-industrial closed';
                }
            }
        });

        // --- Actualización de Tablas de Monitoreo ---
        if (d.coils_inputs && d.elementos && d.elementos.botones_ev) {
            d.coils_inputs.forEach((v, i) => {
                const b = d.elementos.botones_ev[i];
                if (b) {
                    const el = document.getElementById(`coil-in-${b.address}`);
                    if (el) {
                        el.innerText = v ? 'ON' : 'OFF';
                        el.className = v ? 'on' : 'off';
                        el.style.color = v ? '#2e7d32' : '#d32f2f';
                    }
                }
            });
        }
        if (d.coils_outputs) {
            d.coils_outputs.forEach((v, i) => {
                const el = document.getElementById(`coil-out-${i}`);
                if (el) {
                    el.innerText = v ? 'ON' : 'OFF';
                    el.className = v ? 'on' : 'off';
                    el.style.color = v ? '#2e7d32' : '#d32f2f';
                }
            });
        }
        if (d.registers_inputs && d.elementos && d.elementos.sensores) {
            d.registers_inputs.forEach((v, i) => {
                const s = d.elementos.sensores[i];
                if (s) {
                    const el = document.getElementById(`reg-in-${s.address}`);
                    if (el) el.innerText = v;
                }
            });
        }

        if (d.elementos && d.elementos.tanques) {
            d.elementos.tanques.forEach((t, i) => {
                const index = i + 1;
                const sPresionIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_presion);
                if (sPresionIdx !== -1) {
                    const rawLevel = d.registers_inputs[sPresionIdx];
                    const cfg = CONFIG_TANQUES[`T${index}`];
                    setVisLevel(`t${index}`, rawLevel, cfg);
                    
                    const levValEl = document.getElementById(`vis-lev-t${index}-val`);
                    if (levValEl) levValEl.innerText = rawLevel;
                    
                    const levEl = document.getElementById(`vis-lev-t${index}`);
                    if (t.sensor_de_temperatura) {
                        const sTempIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_temperatura);
                        if (sTempIdx !== -1) {
                            const rawTemp = d.registers_inputs[sTempIdx];
                            const tempC = rawToCelsius(rawTemp);
                            const color = getWaterColor(parseFloat(tempC));
                            
                            const tempEl = document.getElementById(`vis-temp-t${index}`);
                            if (tempEl) tempEl.innerText = tempC;
                            
                            const tempBarEl = document.getElementById(`temp-fill-t${index}`);
                            if (tempBarEl) {
                                tempBarEl.style.height = Math.min(100, Math.max(0, (parseFloat(tempC) - 20) * 100 / 75)) + "%";
                                tempBarEl.style.backgroundColor = color;
                            }
                            const tempBulbEl = document.getElementById(`temp-bulb-t${index}`);
                            if (tempBulbEl) tempBulbEl.style.backgroundColor = color;
                            if (levEl) levEl.style.backgroundColor = color;
                            
                            if (index === 2) g_tempT2 = parseFloat(tempC);
                            if (index === 4) g_tempT4 = parseFloat(tempC);
                        }
                    } else if (levEl) {
                        levEl.style.backgroundColor = getWaterColor(20);
                    }
                }
            });
        }

        // --- Modal Detallado ---
        if (typeof g_currentModalTankId !== 'undefined' && g_currentModalTankId !== null) {
            const id = g_currentModalTankId;
            const t = d.elementos.tanques[id - 1];
            const sPresionIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_presion);
            const rawLevel = d.registers_inputs[sPresionIdx];
            const levelVal = escalarNivel(rawLevel, CONFIG_TANQUES[`T${id}`]);
            const levelAbs = (levelVal * t.volumen / 100).toFixed(2);
            let tempVal = "--";

            if (t.sensor_de_temperatura) {
                const sTempIdx = d.elementos.sensores.findIndex(s => s.address === t.sensor_de_temperatura);
                tempVal = rawToCelsius(d.registers_inputs[sTempIdx]);
            }

            const vSupIdx = d.elementos.valvulas.findIndex(v => v.address === t.valvula_superior);
            const vInfIdx = d.elementos.valvulas.findIndex(v => v.address === t.valvula_inferior);
            const mV1 = document.getElementById("modal-v1");
            const mV2 = document.getElementById("modal-v2");
            if (mV1) mV1.className = d.coils_outputs[vSupIdx] ? "valve-industrial open" : "valve-industrial closed";
            if (mV2) mV2.className = d.coils_outputs[vInfIdx] ? "valve-industrial open" : "valve-industrial closed";

            updateTankModal(levelVal, tempVal, levelAbs);
        }
    }).catch(err => {
        console.error("Error en mainLoop:", err);
        const badge = document.getElementById('status-badge');
        const badgeText = document.getElementById('status-text');
        const plcOverlay = document.getElementById('plc-disconnect-overlay');
        if (badge) badge.className = 'status-badge status-offline';
        if (badgeText) badgeText.innerText = 'Sin conexión';
        if (plcOverlay) plcOverlay.style.display = 'flex';
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
    setInterval(mainLoop, 500);
    setInterval(() => updateCharts(g_tempT2, g_tempT4), 60000);
});
