/**
 * API Logic - Communication with the backend
 */

function writeRegister(addr, val) {
    if (addr === 300 || addr === 301 || addr === 400) {
        alert("Direccion protegida");
        return Promise.reject("Protected address");
    }
    return fetch('/write_register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: addr, value: parseInt(val) })
    });
}

function writeCoil(addr, val) {
    return fetch('/write_coil', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: addr, value: val })
    });
}

function fetchStatus() {
    return fetch('/status').then(r => r.json());
}

function readCoil(addr) {
    return fetch(`/read_coil?address=${addr}`).then(r => r.json());
}
