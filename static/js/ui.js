/**
 * UI & Visual Logic - DOM updates and tab management
 */

function openTab(name, btn) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.getElementById(name).style.display = 'block';
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
}

function escalarNivel(v, cfg) {
    if (!cfg) return "0.0";
    let p = ((v - cfg.min) / (cfg.max - cfg.min)) * 100;
    if (p < 0) p = 0; if (p > 100) p = 100;
    return p.toFixed(1);
}

function setVisLevel(id, v, cfg) {
    const el = document.getElementById(`vis-lev-${id}`);
    if (el) {
        el.style.height = escalarNivel(v, cfg) + "%";
    }
}

function updateInputIfNoFocus(id, rawVal, cfg) {
    const el = document.getElementById(id);
    if (el && document.activeElement.id !== id) {
        let p = ((rawVal - cfg.min) / (cfg.max - cfg.min)) * 100;
        if (p < 0) p = 0; if (p > 100) p = 100;
        el.value = Math.round(p);
    }
}

function updateBtn(id, active) {
    const btn = document.getElementById(id);
    if (!btn) return;
    if (active) {
        btn.innerText = "ON";
        btn.style.background = "#2e7d32";
    } else {
        btn.innerText = "OFF";
        btn.style.background = "#d32f2f";
    }
}

function updatePermiso(id, ok) {
    const s = document.getElementById(id);
    if (!s) return;
    if (ok) {
        s.innerText = "OK";
        s.style.color = "#2e7d32";
    } else {
        s.innerText = "BAJO";
        s.style.color = "#d32f2f";
    }
}
