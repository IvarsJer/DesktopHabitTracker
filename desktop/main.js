// Electron shell that loads your running Flask app
const { app, BrowserWindow, Notification, Tray, Menu } = require('electron');
const path = require('path');
const http = require('http');
const { spawn } = require('child_process');

let win, tray, pyProc;

const FLASK_URL = process.env.FLASK_URL || 'http://127.0.0.1:5001';
const SHELL_PORT = process.env.SHELL_PORT || 8787;

// If you want Electron to start Flask for you, uncomment startFlask() below.
function startFlask() {
  // venv python and desktop.py are one level up from /desktop
  const py = process.env.PYTHON || path.join(__dirname, '..', '.venv', 'Scripts', 'python.exe');
  const entry = path.join(__dirname, '..', 'desktop.py');
  pyProc = spawn(py, [entry], { stdio: 'ignore', detached: true });
}

function createWindow() {
  win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { preload: path.join(__dirname, 'preload.js') }
  });
  win.loadURL(FLASK_URL);
}

function createTray() {
  const iconPath = path.join(__dirname, 'icon.ico'); // add an icon file if you have one
  tray = new Tray(iconPath);
  const menu = Menu.buildFromTemplate([
    { label: 'Open HabitFlow', click: () => { if (win) { win.show(); win.focus(); } } },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() }
  ]);
  tray.setToolTip('HabitFlow');
  tray.setContextMenu(menu);
  tray.on('click', () => { if (win) { win.show(); win.focus(); } });
}

// Tiny HTTP server to receive notifications from Flask (POST /notify)
function startNotifyServer() {
  const server = http.createServer((req, res) => {
    if (req.method === 'POST' && req.url === '/notify') {
      let body = '';
      req.on('data', chunk => body += chunk);
      req.on('end', () => {
        try {
          const payload = JSON.parse(body || '{}');
          new Notification({
            title: payload.title || 'HabitFlow',
            body: payload.body || 'Reminder'
          }).show();
        } catch (e) {}
        res.writeHead(200);
        res.end('ok');
      });
      return;
    }
    res.writeHead(404); res.end();
  });
  server.listen(SHELL_PORT, '127.0.0.1');
  process.env.SHELL_NOTIFY_URL = `http://127.0.0.1:${SHELL_PORT}/notify`;
}

app.whenReady().then(() => {
  // startFlask(); // ← uncomment if you want the shell to launch Flask
  startNotifyServer();
  createWindow();
  createTray();
});

app.on('window-all-closed', (e) => {
  // keep running in tray
  e.preventDefault();
});

app.on('before-quit', () => {
  if (pyProc) { try { process.kill(-pyProc.pid); } catch (e) {} }
});
