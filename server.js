const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');

const PYTHON_PORT = process.env.PYTHON_PORT || 8000;
const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  // Reverse proxy /api/analyze requests internally to the Python engine
  if (req.url === '/api/analyze') {
    const proxyReq = http.request(
      {
        hostname: '127.0.0.1',
        port: PYTHON_PORT,
        path: '/',
        method: req.method,
        headers: req.headers,
      },
      (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res, { end: true });
      }
    );

    proxyReq.on('error', (err) => {
      console.error('Python proxy error:', err.message);
      res.writeHead(502, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Python analyzer unavailable' }));
    });

    req.pipe(proxyReq, { end: true });
    return;
  }

  // Serve the frontend
  if (req.url === '/' || req.url === '/index.html') {
    fs.readFile(path.join(__dirname, 'index.html'), (err, data) => {
      if (err) {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Error loading index.html');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(data);
    });
    return;
  }

  res.writeHead(404);
  res.end();
});

const wss = new WebSocketServer({ server });

let currentVibe = {
  energy: 0.35,
  vibe: 'Deep Focus',
  description: 'Monotonous rhythms for uninterrupted coding',
  palette: ['#090d16', '#3b82f6'],
  spotifyTrackId: ''
};

wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'SYNC', data: currentVibe }));

  ws.on('message', (message) => {
    try {
      const parsed = JSON.parse(message);
      if (parsed.type === 'UPDATE_VIBE') {
        currentVibe = { ...currentVibe, ...parsed.data };
        wss.clients.forEach((client) => {
          if (client.readyState === 1) {
            client.send(JSON.stringify({ type: 'SYNC', data: currentVibe }));
          }
        });
      }
    } catch (e) {
      console.error('WebSocket parse error:', e);
    }
  });
});

server.listen(PORT, () => {
  console.log(`LofiCanvas Gateway listening on port ${PORT}`);
});