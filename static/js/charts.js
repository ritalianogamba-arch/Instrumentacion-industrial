/**
 * Charts Logic - Chart.js initialization and updates
 */

let c2, c4, cLab;

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

    const ctx2 = document.getElementById('chartT2');
    if (ctx2) {
        c2 = new Chart(ctx2.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temp T2 (C)',
                    borderColor: '#E65100',
                    backgroundColor: 'rgba(230, 81, 0, 0.1)',
                    data: [],
                    tension: 0.4,
                    fill: true
                }]
            },
            options: JSON.parse(JSON.stringify(commonOptions))
        });
    }

    const ctx4 = document.getElementById('chartT4');
    if (ctx4) {
        c4 = new Chart(ctx4.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temp T4 (C)',
                    borderColor: '#1976D2',
                    backgroundColor: 'rgba(25, 118, 210, 0.1)',
                    data: [],
                    tension: 0.4,
                    fill: true
                }]
            },
            options: JSON.parse(JSON.stringify(commonOptions))
        });
    }

    const ctxLab = document.getElementById('chartLAB');
    if (ctxLab) {
        cLab = new Chart(ctxLab.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'PID LAB SP',
                    borderColor: '#7B1FA2',
                    backgroundColor: 'rgba(123, 31, 162, 0.1)',
                    data: [],
                    tension: 0.4,
                    fill: true
                }]
            },
            options: JSON.parse(JSON.stringify(commonOptions))
        });
    }
}

function toggleScaleMode() {
    const autoScaleEl = document.getElementById('autoScale');
    if (!autoScaleEl) return;
    
    const isAuto = autoScaleEl.checked;
    const manualControls = document.getElementById('manualControls');
    if (manualControls) {
        manualControls.style.display = isAuto ? 'none' : 'inline-block';
    }
}

function applyManualScale() {
    const minEl = document.getElementById('chartMin');
    const maxEl = document.getElementById('chartMax');
    if (!minEl || !maxEl) return;

    const min = parseFloat(minEl.value);
    const max = parseFloat(maxEl.value);
    
    [c2, c4, cLab].forEach(chart => {
        if (chart) {
            chart.options.scales.y.min = min;
            chart.options.scales.y.max = max;
            chart.update();
        }
    });
}

function updateCharts(t2, t4) {
    if (!c2 || !c4) return;
    
    const now = new Date().toLocaleTimeString();
    const autoScaleEl = document.getElementById('autoScale');
    const isAuto = autoScaleEl ? autoScaleEl.checked : true;

    c2.data.labels.push(now);
    c2.data.datasets[0].data.push(t2);

    c4.data.labels.push(now);
    c4.data.datasets[0].data.push(t4);

    if (c2.data.labels.length > 2000) {
        c2.data.labels.shift(); c2.data.datasets[0].data.shift();
        c4.data.labels.shift(); c4.data.datasets[0].data.shift();
    }

    const totalPoints = c2.data.labels.length;
    if (totalPoints > 30) {
        c2.options.scales.x.min = totalPoints - 30;
        c2.options.scales.x.max = totalPoints - 1;
        c4.options.scales.x.min = totalPoints - 30;
        c4.options.scales.x.max = totalPoints - 1;
    }

    if (isAuto) {
        c2.options.scales.y.min = Math.floor(t2 - 10);
        c2.options.scales.y.max = Math.ceil(t2 + 10);
        c4.options.scales.y.min = Math.floor(t4 - 10);
        c4.options.scales.y.max = Math.ceil(t4 + 10);
    }

    c2.update();
    c4.update();
}
