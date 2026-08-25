from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import hashlib

# 10-Tier Vibe Catalog
VIBE_CATALOG = [
    {
        "name": "Zen Garden",
        "min_energy": 0.0,
        "max_energy": 0.15,
        "desc": "Ultra-low ambient drone, quiet minimalism",
        "palette": ["#061a14", "#10b981"]  # Deep moss & Emerald
    },
    {
        "name": "Midnight Rain",
        "min_energy": 0.15,
        "max_energy": 0.28,
        "desc": "Gentle lo-fi beats, calm rain acoustics",
        "palette": ["#08121e", "#38bdf8"]  # Dark navy & Sky blue
    },
    {
        "name": "Deep Focus",
        "min_energy": 0.28,
        "max_energy": 0.38,
        "desc": "Monotonous rhythms for uninterrupted coding",
        "palette": ["#090d16", "#3b82f6"]  # Slate & Cobalt
    },
    {
        "name": "Lo-Fi Coffee Shop",
        "min_energy": 0.38,
        "max_energy": 0.48,
        "desc": "Warm vinyl crackle, mellow jazzy chords",
        "palette": ["#1c130d", "#d97706"]  # Roasted espresso & Warm amber
    },
    {
        "name": "Synthwave Dusk",
        "min_energy": 0.48,
        "max_energy": 0.58,
        "desc": "80s retro drive, warm synth pads",
        "palette": ["#20072b", "#d946ef"]  # Deep plum & Bright fuchsia
    },
    {
        "name": "Flow State",
        "min_energy": 0.58,
        "max_energy": 0.68,
        "desc": "Pulsing basslines, locked-in groove",
        "palette": ["#130722", "#ec4899"]  # Dark purple & Neon pink
    },
    {
        "name": "Cyberpunk Club",
        "min_energy": 0.68,
        "max_energy": 0.78,
        "desc": "Hard electro synth, heavy low-end",
        "palette": ["#022627", "#06b6d4"]  # Obsidian teal & Cyan glow
    },
    {
        "name": "Neon Overdrive",
        "min_energy": 0.78,
        "max_energy": 0.88,
        "desc": "Fast tempo, aggressive drums & drops",
        "palette": ["#2b0707", "#ef4444"]  # Blood black & Crimson neon
    },
    {
        "name": "Hyper Vibe",
        "min_energy": 0.88,
        "max_energy": 0.95,
        "desc": "Peak festival energy, maximalist sound",
        "palette": ["#3b1100", "#f97316"]  # Deep rust & Electric orange
    },
    {
        "name": "Solar Flare",
        "min_energy": 0.95,
        "max_energy": 1.01,
        "desc": "Saturated, full-spectrum bass overload",
        "palette": ["#261c02", "#eab308"]  # Dark obsidian & Electric yellow
    }
]

class VibeHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        # Health check and root status endpoint
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        response = {
            "status": "online",
            "service": "Python Vibe Engine",
            "vibes_available": len(VIBE_CATALOG)
        }
        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        content_type = self.headers.get('Content-Type', '')

        norm_energy = 0.5

        # Handle Spotify JSON analysis
        if 'application/json' in content_type:
            try:
                body = json.loads(post_data.decode('utf-8'))
                spotify_url = body.get('url', '')
                
                track_id_match = re.search(r'track[/:]([a-zA-Z0-9]+)', spotify_url)
                track_id = track_id_match.group(1) if track_id_match else spotify_url
                
                hash_int = int(hashlib.md5(track_id.encode()).hexdigest(), 16)
                norm_energy = round(0.10 + (hash_int % 85) / 100.0, 2)
            except Exception:
                norm_energy = 0.55
        else:
            # Handle Raw Audio Stream Bytes
            if len(post_data) > 0:
                sample = post_data[:min(len(post_data), 150000)]
                avg_val = sum(sample) / len(sample)
                variance = sum((b - avg_val) ** 2 for b in sample) / len(sample)
                norm_energy = min(max(round(variance / 5500.0, 2), 0.05), 0.99)

        # Match to catalog tier
        selected_vibe = VIBE_CATALOG[5]
        for v in VIBE_CATALOG:
            if v["min_energy"] <= norm_energy < v["max_energy"]:
                selected_vibe = v
                break

        response = {
            "energy": norm_energy,
            "vibe": selected_vibe["name"],
            "description": selected_vibe["desc"],
            "palette": selected_vibe["palette"]
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    HTTPServer.allow_reuse_address = True
    server = HTTPServer(('127.0.0.1', 8000), VibeHandler)
    print("Python Vibe Engine running on http://127.0.0.1:8000...")
    server.serve_forever()