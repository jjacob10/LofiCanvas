const http = require('http');
const fs = require('fs');
const path = require('path');
const { WebSocketServer } = require('ws');

const server = http.createServer((req, res) => {
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
  } else {
    res.writeHead(404);
    res.end();
  }
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
      console.error('Error handling WebSocket message:', e);
    }
  });
});

server.listen(3000, () => {
  console.log('Node.js Room Gateway running on http://localhost:3000');
});