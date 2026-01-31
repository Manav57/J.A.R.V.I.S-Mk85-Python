// --- EEL CONNECTION ---
eel.expose(js_print_terminal);
function js_print_terminal(text) {
    const term = document.getElementById('terminal-log');
    const p = document.createElement('p');
    p.innerText = `> ${text}`;
    p.classList.add('log-entry');
    term.appendChild(p);
    term.scrollTop = term.scrollHeight;
}

eel.expose(js_set_status);
function js_set_status(status) {
    const el = document.getElementById('status-text');
    const center = document.querySelector('.circle-center');

    el.innerText = status;

    if(status === "LISTENING") {
        el.style.color = "#00ff00"; // Green
        el.style.textShadow = "0 0 20px #00ff00";
        if(center) center.style.boxShadow = "0 0 50px #00ff00";
    } else if (status === "SPEAKING") {
        el.style.color = "#00f3ff"; // Blue
        el.style.textShadow = "0 0 20px #00f3ff";
        if(center) center.style.boxShadow = "0 0 80px #00f3ff";
    } else if (status === "ONLINE") {
        el.style.color = "#ffffff"; // White
        el.style.textShadow = "0 0 10px #ffffff";
    }
}

// --- HOLOGRAM DISPLAY LOGIC (THE FIX) ---
eel.expose(js_show_display);
function js_show_display(content) {
    const modal = document.getElementById('hologram-modal');
    const screen = document.getElementById('hologram-text');

    // CRITICAL FIX: innerHTML allows images/videos to show.
    // innerText would only show the code as text.
    screen.innerHTML = content;

    // Show the window
    modal.classList.remove('hidden');
}

function closeModal() {
    document.getElementById('hologram-modal').classList.add('hidden');
    // Clear content so video stops playing in background
    document.getElementById('hologram-text').innerHTML = "";
}

function copyText() {
    const text = document.getElementById('hologram-text').innerText;
    navigator.clipboard.writeText(text).then(() => {
        js_print_terminal("DATA COPIED");
    });
}

// --- CLOCK & ANIMATION ---
setInterval(() => {
    const now = new Date();
    const timeElem = document.getElementById('clock');
    if(timeElem) timeElem.innerText = now.toLocaleTimeString();
}, 1000);

// Random Data Stream
setInterval(() => {
    const stream = document.getElementById('data-stream-left');
    if(stream) {
        let str = "";
        const chars = "0123456789ABCDEF";
        for(let i=0; i<10; i++) str += chars[Math.floor(Math.random()*16)];
        stream.innerText = `0x${str} // SYSTEM_OK`;
    }

    // Update Hardware bars
    const cpuBar = document.getElementById('cpu-bar');
    if(cpuBar) {
        const cpu = Math.floor(Math.random() * 30) + 20;
        cpuBar.style.width = cpu + "%";
        document.getElementById('cpu-num').innerText = cpu + "%";
    }
}, 1500);