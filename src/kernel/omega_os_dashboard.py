# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "/home/jake/Downloads/training/python_env/agent_zero/knowledge"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            # Dashboard HTML
            with open("/home/jake/Downloads/training/python_env/agent_zero/knowledge/omega_os_evolution.md", "r") as f:
                os_content = f.read()
            
            innovation_content = "Innovation ledger is empty."
            if os.path.exists("/home/jake/Downloads/training/python_env/agent_zero/knowledge/innovation_ledger.md"):
                with open("/home/jake/Downloads/training/python_env/agent_zero/knowledge/innovation_ledger.md", "r") as f:
                    innovation_content = f.read()
            
            scout_content = "No device discoveries yet."
            scout_logs = "/home/jake/Downloads/training/automations/logs"
            if os.path.exists(scout_logs):
                latest_logs = sorted(os.listdir(scout_logs), reverse=True)[:5]
                scout_content = ""
                for log in latest_logs:
                    with open(os.path.join(scout_logs, log), "r") as f:
                        scout_content += f"\n### {log}\n{f.read()[:1000]}...\n"

            sarai_status = "Sarai Training Ongoing..."
            if os.path.exists("/home/jake/Downloads/training/sarai_termux_optimized.pt"):
                sarai_status = "Sarai (135M INT4) - STANDBY on NPU"

            html = f"""
            <html>
            <head>
                <title>Omega Protocol Dashboard</title>
                <style>
                    body {{ font-family: monospace; background: #111; color: #0f0; padding: 20px; }}
                    pre {{ white-space: pre-wrap; word-wrap: break-word; border-left: 3px solid #0f0; padding-left: 15px; margin-bottom: 40px; }}
                    h1 {{ color: #0ff; }}
                    h2 {{ color: #f0f; border-bottom: 1px solid #f0f; }}
                    h3 {{ color: #ff0; }}
                    ul {{ list-style-type: square; color: #ff0; }}
                </style>
                <meta http-equiv="refresh" content="30">
            </head>
            <body>
                <h1>✦ OMEGA PROTOCOL DASHBOARD ✦</h1>
                <p><b>Version:</b> 0.1.868 | <b>DEDS Status:</b> Multi-Persistence Active</p>
                <hr>
                
                <h2>🧠 HARDWARE-ACCELERATED AI (NPU)</h2>
                <h3>SARAI NODE: {sarai_status}</h3>
                <p><b>Hardware:</b> AMD XDNA 2 (50 TOPS) | <b>Routing:</b> Asynchronous NPU Dispatch</p>

                <h2>🖥️ OMEGA OS EVOLUTION</h2>
                <pre>{os_content}</pre>
                
                <h2>🔍 DEVICE AUTOMATION DISCOVERIES</h2>
                <pre>{scout_content}</pre>

                <h2>💡 UNIVERSAL INNOVATION LEDGER</h2>
                <pre>{innovation_content}</pre>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"📡 Omega OS Dashboard serving at port {{PORT}}")
    httpd.serve_forever()
