# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import customtkinter as ctk
import os
import sys
import webbrowser
import threading
import pyperclip
import tkinter.messagebox as messagebox
import subprocess
import time
import atexit
import json
import psutil
import pandas as pd
from datetime import datetime
from PIL import Image, ImageTk, ImageDraw

from utils.logger import logger
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configs.config import config

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# --- MODULE IMPORTS (Fail gracefully) ---
try:
    from LTM.process_memories import store_memory, search_memories
    from LTM.memory_refiner import refine_memory
    from business.sales_automation_engine import OmegaSalesEngine
    from tools.generate_vibe_report import generate_benchmarking_suite
except ImportError as e:
    logger.error(f"CRITICAL: Resource missing.\nError: {e}")

class OmegaControlPanel(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Ω OMEGA PROTOCOL | ELITE COMMAND CENTER")
        self.geometry("1400x950")
        ctk.set_appearance_mode("dark") # Forced dark for elite look
        ctk.set_default_color_theme("blue")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Main Layout Setup
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State tracking
        self.active_branch = "DASHBOARD"
        self.mcp_process = None
        self.mcp_running = False
        self.orchestrator_process = None
        self.orchestrator_running = False
        self.running_processes = {}
        
        # Telemetry State
        self.telemetry_data = {"cpu": 0, "ram": 0, "disk": 0}
        self.ticker_items = []
        
        atexit.register(self.stop_all_processes)

        # UI Components
        self.nav_buttons = {}
        self.frames = {}
        
        self._setup_sidebar()
        self._setup_main_area()
        
        # Start Background Services
        self._start_telemetry_loop()
        self._start_ticker_loop()
        self._start_pulse_animation()
        
        # Initial View
        self.show_frame("dashboard")

    def stop_all_processes(self):
        self.stop_mcp()
        self.stop_orchestrator()
        for name, proc in list(self.running_processes.items()):
            proc.terminate()

    def _start_telemetry_loop(self):
        def loop():
            while True:
                try:
                    self.telemetry_data["cpu"] = psutil.cpu_percent()
                    self.telemetry_data["ram"] = psutil.virtual_memory().percent
                    self.telemetry_data["disk"] = psutil.disk_usage('/').percent
                    self.update_telemetry_ui()
                except: pass
                time.sleep(2)
        threading.Thread(target=loop, daemon=True).start()

    def _start_ticker_loop(self):
        def loop():
            log_path = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge", "evolution_log.jsonl")
            while True:
                if os.path.exists(log_path):
                    try:
                        with open(log_path, "r") as f:
                            lines = f.readlines()
                            new_items = []
                            for line in lines[-10:]: # Get last 10 entries
                                try:
                                    data = json.loads(line)
                                    msg = data.get("message") or data.get("accomplishment") or "Evolution step recorded."
                                    new_items.append(msg)
                                except: pass
                            self.ticker_items = new_items
                            self.update_ticker_ui()
                    except: pass
                time.sleep(10)
        threading.Thread(target=loop, daemon=True).start()

    def update_telemetry_ui(self):
        if hasattr(self, 'cpu_label'):
            self.cpu_label.configure(text=f"CPU: {self.telemetry_data['cpu']}%")
            self.ram_label.configure(text=f"RAM: {self.telemetry_data['ram']}%")
            
    def update_ticker_ui(self):
        if hasattr(self, 'ticker_label') and self.ticker_items:
            msg = " | ".join(self.ticker_items[-3:])
            self.ticker_label.configure(text=f"🚀 {msg}")

    def _setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#0d1117")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(12, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Ω OMEGA PROTOCOL", 
                                       font=ctk.CTkFont(family="Orbitron", size=24, weight="bold"),
                                       text_color="#58a6ff")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(40, 40))

        self.nav_buttons = {}
        
        # Navigation
        self.create_nav_item("dashboard", "🏠 DASHBOARD", 1)
        self.create_nav_item("orchestrator", "🎮 ORCHESTRATOR", 2)
        self.create_nav_item("dataroom", "🖼️ DATA ROOM", 3)
        self.create_nav_item("history", "📜 MISSION HISTORY", 4)
        
        # Branch Selector Link
        self.btn_switch = ctk.CTkButton(self.sidebar_frame, text="🔄 BRANCH SELECTOR", 
                                        command=self._setup_branch_selector,
                                        fg_color="#1f242c", hover_color="#30363d")
        self.btn_switch.grid(row=5, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Telemetry Display in Sidebar
        telemetry_f = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        telemetry_f.grid(row=10, column=0, padx=20, pady=20, sticky="ew")
        
        self.cpu_label = ctk.CTkLabel(telemetry_f, text="CPU: 0%", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.cpu_label.pack(side="left", padx=5)
        self.ram_label = ctk.CTkLabel(telemetry_f, text="RAM: 0%", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.ram_label.pack(side="right", padx=5)

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text=f"v29.3-ELITE", 
                                          font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.version_label.grid(row=13, column=0, padx=20, pady=20)

    def create_nav_item(self, key, text, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, 
                            command=lambda k=key: self.show_frame(k), 
                            height=50, corner_radius=10, anchor="w",
                            font=ctk.CTkFont(size=14, weight="bold"),
                            fg_color="transparent", hover_color="#21262d",
                            text_color="#8b949e")
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        self.nav_buttons[key] = btn

    def _setup_main_area(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=20, fg_color="#010409", border_width=1, border_color="#30363d")
        self.main_container.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Footer Console
        self.console_frame = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="#161b22", border_width=1, border_color="#30363d")
        self.console_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self.console_frame, text="● SYSTEM READY", text_color="#3fb950", 
                                         font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side="left", padx=25)

        self.ticker_label = ctk.CTkLabel(self.console_frame, text="🚀 INITIALIZING QUANTUM FEED...", 
                                          font=ctk.CTkFont(size=11), text_color="#58a6ff")
        self.ticker_label.pack(side="left", fill="x", expand=True)

        self.time_label = ctk.CTkLabel(self.console_frame, text="", font=ctk.CTkFont(size=11), text_color="#8b949e")
        self.time_label.pack(side="right", padx=25)
        self.update_time()

    def show_frame(self, frame_name):
        # Lazy initialization
        if frame_name not in self.frames:
            if frame_name == "dashboard": self.frames["dashboard"] = self._create_dashboard_frame()
            elif frame_name == "orchestrator": self.frames["orchestrator"] = self._create_orchestrator_frame()
            elif frame_name == "dataroom": self.frames["dataroom"] = self._create_dataroom_frame()
            elif frame_name == "history": self.frames["history"] = self._create_history_frame()
            elif frame_name == "mcp": self.frames["mcp"] = self._create_mcp_frame()
            # Branch specific frames (legacy support)
            elif frame_name == "ltm": self.frames["ltm"] = self._create_ltm_frame()
            elif frame_name == "tokamak": self.frames["tokamak"] = self._create_tokamak_frame()

        for frame in self.frames.values():
            frame.grid_forget()
            
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color="#8b949e")
            
        if frame_name in self.nav_buttons:
            self.nav_buttons[frame_name].configure(fg_color="#1f242c", text_color="#58a6ff")
        
        target_frame = self.frames.get(frame_name)
        if target_frame:
            target_frame.grid(row=0, column=0, sticky="nsew")
            self.log_status(f"NAVIGATED TO {frame_name.upper()}")

    def _create_dashboard_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, padx=40, pady=(40, 20), sticky="ew")
        ctk.CTkLabel(header, text="COMMAND CENTER OVERVIEW", 
                     font=ctk.CTkFont(size=32, weight="bold"), text_color="#f0f6fc").pack(side="left")

        # Main Content Scroll
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        # Quick Actions Card
        actions_card = ctk.CTkFrame(scroll, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#30363d")
        actions_card.grid(row=0, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        
        ctk.CTkLabel(actions_card, text="⚡ CORE OPERATIONS", font=ctk.CTkFont(size=18, weight="bold"), text_color="#58a6ff").pack(anchor="w", padx=25, pady=(20, 10))
        
        btn_f = ctk.CTkFrame(actions_card, fg_color="transparent")
        btn_f.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(btn_f, text="🚀 LAUNCH ORCHESTRATOR", command=lambda: self.show_frame("orchestrator"), fg_color="#238636").pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkButton(btn_f, text="⚛️ PHYSICS ARENA", command=lambda: self._initialize_branch("TOKAMAK"), fg_color="#1f6feb").pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkButton(btn_f, text="📈 FINANCE ARENA", command=lambda: self._initialize_branch("FINANCE"), fg_color="#8b5cf6").pack(side="left", padx=10, expand=True, fill="x")
        ctk.CTkButton(btn_f, text="🧪 DISCOVERY LOOP", command=lambda: self._initialize_branch("BIO_EVO"), fg_color="#d29922").pack(side="left", padx=10, expand=True, fill="x")

        # Telemetry Detail Cards
        cpu_card = ctk.CTkFrame(scroll, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#30363d", height=150)
        cpu_card.grid(row=1, column=0, padx=10, pady=15, sticky="nsew")
        ctk.CTkLabel(cpu_card, text="SYSTEM LOAD", font=ctk.CTkFont(size=14, weight="bold"), text_color="#8b949e").pack(pady=(20, 5))
        self.cpu_dash_val = ctk.CTkLabel(cpu_card, text="0%", font=ctk.CTkFont(size=36, weight="bold"), text_color="#3fb950")
        self.cpu_dash_val.pack()
        
        mem_card = ctk.CTkFrame(scroll, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#30363d", height=150)
        mem_card.grid(row=1, column=1, padx=10, pady=15, sticky="nsew")
        ctk.CTkLabel(mem_card, text="MEMORY USAGE", font=ctk.CTkFont(size=14, weight="bold"), text_color="#8b949e").pack(pady=(20, 5))
        self.mem_dash_val = ctk.CTkLabel(mem_card, text="0%", font=ctk.CTkFont(size=36, weight="bold"), text_color="#3fb950")
        self.mem_dash_val.pack()

        # Update telemetry values on dashboard
        def update_dash_telemetry():
            if hasattr(self, 'cpu_dash_val'):
                self.cpu_dash_val.configure(text=f"{self.telemetry_data['cpu']}%")
                self.mem_dash_val.configure(text=f"{self.telemetry_data['ram']}%")
            self.after(2000, update_dash_telemetry)
        update_dash_telemetry()

        return frame

    def _start_pulse_animation(self):
        def pulse():
            colors = ["#3fb950", "#238636", "#1e662c", "#238636"]
            i = 0
            while True:
                if hasattr(self, 'status_label'):
                    try:
                        color = colors[i % len(colors)]
                        self.status_label.configure(text_color=color)
                        i += 1
                    except: pass
                time.sleep(0.5)
        threading.Thread(target=pulse, daemon=True).start()

    def _setup_branch_selector(self):
        # Hide sidebar if visible
        if hasattr(self, 'sidebar_frame'):
            self.sidebar_frame.grid_forget()
        
        # Clear main container
        for widget in self.main_container.winfo_children():
            widget.destroy()
            
        self.main_container.grid(row=0, column=0, columnspan=2, padx=100, pady=100)
        
        title_lbl = ctk.CTkLabel(self.main_container, text="WELCOME TO THE OMEGA PROTOCOL", 
                                 font=ctk.CTkFont(family="Orbitron", size=36, weight="bold"),
                                 text_color="#58a6ff")
        title_lbl.pack(pady=(0, 20))
        
        sub_lbl = ctk.CTkLabel(self.main_container, text="Select your operational focus to initialize the workspace.", 
                               font=ctk.CTkFont(size=16), text_color="#8b949e")
        sub_lbl.pack(pady=(0, 60))
        
        # Simple entry animation
        def fade_in(widgets, alpha=0):
            if alpha <= 1:
                # tkinter doesn't support alpha for widgets easily, 
                # so we just show them and maybe move them slightly
                pass

        btn_f = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_f.pack(fill="both", expand=True)
        btn_f.grid_columnconfigure((0,1,2), weight=1)
        
        branches = [
            ("OMEGA CORE", "Deep Learning, LTM & Enterprise Sales", "CORE", "#238636"),
            ("TOKAMAK FUSION", "Plasma Disruption Physics & HLS Tuning", "TOKAMAK", "#1f6feb"),
            ("AGENT ZERO", "Autonomous Evolution & Arena Tournaments", "AGENT_ZERO", "#8957e5"),
            ("BIOLOGICAL EVO", "E. Coli Lenski Experiments & Phi_Delta Substrates", "BIO_EVO", "#d29922"),
            ("FINANCE", "Bitcoin Market Manifolds & Alpha Generation", "FINANCE", "#8b5cf6"),
            ("STRATEGIC NEXUS", "Economics, Science, Creative & Meta-Orchestration", "STRATEGIC", "#e3b341")
        ]
        
        for i, (title, desc, key, color) in enumerate(branches):
            card = ctk.CTkFrame(btn_f, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=20)
            card.grid(row=i//3, column=i%3, padx=20, pady=20, sticky="nsew")
            
            # Hover effects
            def on_enter(e, c=card, col=color):
                c.configure(border_color=col, border_width=2)
            def on_leave(e, c=card):
                c.configure(border_color="#30363d", border_width=1)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=22, weight="bold"), text_color=color).pack(pady=(40, 10))
            ctk.CTkLabel(card, text=desc, wraplength=250, font=ctk.CTkFont(size=14), text_color="#c9d1d9").pack(pady=20, padx=30)
            
            ctk.CTkButton(card, text=f"INITIALIZE {key}", 
                          command=lambda k=key: self._initialize_branch(k),
                          fg_color=color, hover_color="#30363d", height=50,
                          font=ctk.CTkFont(weight="bold")).pack(pady=(20, 40))

    def _initialize_branch(self, branch_key):
        self.active_branch = branch_key
        print(f"🚀 Initializing {branch_key} Branch...")
        
        # Reset layout to sidebar view
        self.main_container.grid_forget()
        self.main_container.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")
        
        self._setup_sidebar()
        
        # We no longer clear self.frames = {} here to preserve global frames (dashboard, history)
        # but we might want to refresh branch-specific ones
        branch_frames = ["ltm", "tokamak", "agent_zero", "bio_evo", "economics"]
        for bf in branch_frames:
            if bf in self.frames:
                del self.frames[bf]
        
        # Default to branch specific frame if it exists, otherwise dashboard
        if branch_key == "CORE": self.show_frame("ltm")
        elif branch_key == "TOKAMAK": self.show_frame("tokamak")
        elif branch_key == "AGENT_ZERO": self.show_frame("agent_zero")
        elif branch_key == "BIO_EVO": self.show_frame("bio_evo")
        elif branch_key == "FINANCE": self.show_frame("dataroom")
        elif branch_key == "STRATEGIC": self.show_frame("economics")
        else: self.show_frame("dashboard")
        
        self.log_status(f"Branch {branch_key} Active")

    def _init_frames(self):
        # Base frames are now lazily loaded in show_frame
        pass

    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.grid_forget()
            
        for btn in self.nav_buttons.values():
            btn.configure(fg_color="transparent", text_color="#8b949e")
            
        if frame_name in self.nav_buttons:
            self.nav_buttons[frame_name].configure(fg_color="#1f242c", text_color="#58a6ff")
        self.frames[frame_name].grid(row=0, column=0, sticky="nsew")
        self.log_status(f"Loaded {frame_name.capitalize()} Panel")

    def create_help_box(self, parent, title, content):
        box = ctk.CTkFrame(parent, fg_color="#161b22", corner_radius=10, border_width=1, border_color="#30363d")
        ctk.CTkLabel(box, text=f"ℹ {title}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#58a6ff").pack(anchor="w", padx=15, pady=(10, 5))
        ctk.CTkLabel(box, text=content, font=ctk.CTkFont(size=12), justify="left", wraplength=400, text_color="#8b949e").pack(anchor="w", padx=15, pady=(0, 10))
        return box

    # --- SHARED FRAMES ---
    def _create_manual_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(frame, text=f"{self.active_branch} COMMAND CENTER", 
                     font=ctk.CTkFont(size=28, weight="bold"), text_color="#f0f6fc").grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        scroll_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)

        data = [("🚀 MISSION", "Evolving through research, reasoning, and execution.")]
        if self.active_branch == "TOKAMAK":
            data.append(("⚛️ FUSION", "Using RCOD to predict plasma instabilities."))
        
        for title, content in data:
            f = ctk.CTkFrame(scroll_frame, fg_color="#0d1117", corner_radius=15, border_width=1, border_color="#30363d")
            f.pack(fill="x", padx=10, pady=15)
            ctk.CTkLabel(f, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="#58a6ff").pack(anchor="w", padx=25, pady=(20, 10))
            ctk.CTkLabel(f, text=content, font=ctk.CTkFont(size=14), justify="left", wraplength=800, text_color="#c9d1d9").pack(anchor="w", padx=25, pady=(0, 20))
        return frame

    def _create_dataroom_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        tabview = ctk.CTkTabview(frame, fg_color="#0d1117", border_width=1, border_color="#30363d")
        tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        categories = {
            "PHYSICS": ["tokamak/rcod_validation_SNAPSHOT_v26.5.png", "tokamak/rcod_validation_Figure11_T094124_PlasmaRogA.png", "tokamak/rcod_validation_Figure20_Ip.png"],
            "FINANCE": ["finance/btc_multi_scale_analysis.png", "finance/btc_rcod_analysis.png"],
            "COSMOLOGY": ["tools/cosmology_validation_v26.7.png"]
        }

        for cat, paths in categories.items():
            tab = tabview.add(cat)
            scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            scroll.pack(fill="both", expand=True)
            
            for path in paths:
                full_path = os.path.join(PROJECT_ROOT, path)
                if os.path.exists(full_path):
                    try:
                        img = Image.open(full_path)
                        # Resize for display
                        w, h = img.size
                        aspect = w/h
                        new_w = 800
                        new_h = int(new_w / aspect)
                        
                        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_w, new_h))
                        label = ctk.CTkLabel(scroll, image=ctk_img, text="")
                        label.pack(pady=20)
                        ctk.CTkLabel(scroll, text=os.path.basename(path), font=ctk.CTkFont(size=12, weight="bold"), text_color="#8b949e").pack()
                    except Exception as e:
                        ctk.CTkLabel(scroll, text=f"Error loading {path}: {e}").pack()
                else:
                    ctk.CTkLabel(scroll, text=f"File not found: {path}", text_color="#f85149").pack(pady=20)

        return frame

    def _create_orchestrator_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="OMEGA ORCHESTRATOR", font=ctk.CTkFont(size=32, weight="bold")).pack(pady=40)
        
        card = ctk.CTkFrame(frame, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=15)
        card.pack(padx=40, pady=20, fill="x")
        
        self.orch_status_lbl = ctk.CTkLabel(card, text="STATUS: STOPPED", text_color="#f85149", font=ctk.CTkFont(size=18, weight="bold"))
        self.orch_status_lbl.pack(pady=20)
        
        self.orch_toggle_btn = ctk.CTkButton(card, text="START ORCHESTRATOR", command=self.toggle_orchestrator, 
                                             fg_color="#238636", height=50, font=ctk.CTkFont(weight="bold"))
        self.orch_toggle_btn.pack(pady=20, padx=40, fill="x")
        
        # Log View
        self.orch_log = ctk.CTkTextbox(frame, fg_color="#0d1117", border_width=1, border_color="#30363d")
        self.orch_log.pack(fill="both", expand=True, padx=40, pady=20)
        
        return frame

    def toggle_orchestrator(self):
        if self.orchestrator_running:
            self.stop_orchestrator()
        else:
            self.start_orchestrator()

    def start_orchestrator(self):
        self.log_status("Launching Orchestrator...", "#d29922")
        script = os.path.join(PROJECT_ROOT, "tools", "omega_polite_orchestrator.py")
        
        def run():
            self.orchestrator_process = subprocess.Popen([sys.executable, script], 
                                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            self.orchestrator_running = True
            self.orch_status_lbl.configure(text="STATUS: RUNNING", text_color="#3fb950")
            self.orch_toggle_btn.configure(text="HALT ORCHESTRATOR", fg_color="#f85149")
            
            for line in iter(self.orchestrator_process.stdout.readline, ""):
                if hasattr(self, 'orch_log'):
                    self.orch_log.insert("end", line)
                    self.orch_log.see("end")
            
            self.orchestrator_process.wait()
            self.orchestrator_running = False
            if hasattr(self, 'orch_status_lbl'):
                self.orch_status_lbl.configure(text="STATUS: STOPPED", text_color="#f85149")
                self.orch_toggle_btn.configure(text="START ORCHESTRATOR", fg_color="#238636")
                self.log_status("Orchestrator Stopped", "#f85149")

        threading.Thread(target=run, daemon=True).start()

    def stop_orchestrator(self):
        if self.orchestrator_process:
            self.orchestrator_process.terminate()
            self.orchestrator_process = None
        self.orchestrator_running = False
        self.orch_status_lbl.configure(text="STATUS: STOPPING...", text_color="#d29922")

    # --- CORE BRANCH FRAMES ---
    def _create_ltm_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="NEURAL MEMORY (LTM)", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        # (Simplified for now to keep code concise)
        ctk.CTkLabel(frame, text="LTM functionalities initialized...").pack()
        return frame

    def _create_sales_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="ENTERPRISE SALES", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        return frame

    # --- TOKAMAK BRANCH FRAMES ---
    def _create_tokamak_frame(self):
        self.tokamak_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tokamak_container.grid_columnconfigure(0, weight=1)
        self.tokamak_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.tokamak_container, text="TOKAMAK FUSION RESEARCH", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")

        # Initial Selector View
        self.tokamak_selector = ctk.CTkFrame(self.tokamak_container, fg_color="transparent")
        self.tokamak_selector.grid(row=1, column=0, sticky="nsew")
        self.tokamak_selector.grid_columnconfigure((0,1,2), weight=1)

        selector_data = [
            ("📊 RCOD VALIDATION", "Run prediction harness on historical plasma datasets.", self.show_tokamak_validation),
            ("🧠 DISRUPTION ANALYST", "Deploy Agent Zero physicists.", self.show_tokamak_analyst)
        ]

        for i, (title, desc, cmd) in enumerate(selector_data):
            card = ctk.CTkFrame(self.tokamak_selector, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=15)
            card.grid(row=0, column=i, padx=20, pady=20, sticky="nsew")
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#58a6ff").pack(pady=(30, 10))
            ctk.CTkButton(card, text="INITIALIZE", command=cmd).pack(pady=20)

        self.tokamak_val_frame = ctk.CTkFrame(self.tokamak_container, fg_color="transparent")
        self._setup_tokamak_val_view()
        return self.tokamak_container

    def _setup_tokamak_val_view(self):
        f = self.tokamak_val_frame
        ctk.CTkButton(f, text="← BACK", command=self.reset_tokamak_view).pack(anchor="w", padx=40, pady=10)
        self.sensor_var = ctk.StringVar(value="Figure11/T094124/PlasmaRogA")
        ctk.CTkOptionMenu(f, values=["Figure11/T094124/PlasmaRogA", "Figure20/Ip"], variable=self.sensor_var).pack(pady=20)
        ctk.CTkButton(f, text="RUN HARNESS", command=self.run_tokamak_val, fg_color="#238636").pack(pady=20)

    # --- AGENT ZERO BRANCH FRAMES ---
    def _create_arena_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🧬 AGENT EVOLUTION ARENA", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        card = ctk.CTkFrame(frame, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=15)
        card.pack(padx=40, pady=20, fill="x")
        
        ctk.CTkLabel(card, text="TOURNAMENT CONFIGURATION", font=ctk.CTkFont(size=18, weight="bold"), text_color="#8957e5").pack(pady=20)
        self.arena_topic = ctk.CTkEntry(card, placeholder_text="Enter problem for competition...", width=600, height=45)
        self.arena_topic.pack(pady=20, padx=40)
        
        ctk.CTkButton(card, text="🚀 START HEAD-TO-HEAD TOURNAMENT", command=self.run_arena, 
                      fg_color="#8957e5", hover_color="#a371f7", height=50).pack(pady=(0, 40))
        
        self.arena_log = ctk.CTkTextbox(frame, fg_color="#0d1117", border_width=1, border_color="#30363d")
        self.arena_log.pack(fill="both", expand=True, padx=40, pady=20)
        return frame

    def _create_trainer_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🚀 AUTOMATED MODEL TRAINER", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        return frame

    # --- BIO EVO BRANCH FRAMES ---
    def _create_bio_evo_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🧪 BIOLOGICAL EVOLUTION", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        card = ctk.CTkFrame(frame, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=15)
        card.pack(padx=40, pady=20, fill="x")
        
        ctk.CTkLabel(card, text="E. COLI LENSKI SIMULATION (v3.0)", font=ctk.CTkFont(size=18, weight="bold"), text_color="#d29922").pack(pady=20)
        ctk.CTkLabel(card, text="Visualize 75,000+ generations of E. coli evolution using the RCOD substrate model. Monitor phenotypic divergence and CIT+ phase transitions in real-time.", 
                     wraplength=600, justify="center", text_color="#c9d1d9").pack(pady=20, padx=40)
        
        ctk.CTkButton(card, text="🌐 LAUNCH EVOLUTION SIMULATOR", command=self.run_bio_evo_sim, 
                      fg_color="#d29922", hover_color="#e3a933", height=50, font=ctk.CTkFont(weight="bold")).pack(pady=(0, 40))
        
        help_box = self.create_help_box(frame, "SCIENTIFIC CONTEXT", 
            "The Long-term Experimental Evolution (LTEE) experiment has tracked 12 populations of E. coli since 1988. This simulator applies the Omega Protocol's Informational Substrate logic to model the Cit+ mutation event.")
        help_box.pack(padx=40, pady=20, fill="x")
        return frame

    def _create_analytics_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="📊 PERFORMANCE ANALYTICS", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        ctk.CTkLabel(frame, text="Telemetry data and cross-branch ROI analysis initialized...", text_color="#8b949e").pack()
        return frame

    # --- STRATEGIC NEXUS FRAMES ---
    def _create_economics_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="📈 STRATEGIC & ECONOMIC AGENTS", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        agents = [
            ("📊 Market Analyst", "Real-time market sentiment, predictive analytics, and portfolio risk assessment."),
            ("💼 Corporate Strategist", "M&A modeling, competitive intelligence, and GTM strategy formulation."),
            ("🏙️ Urban Planner", "Resource-constrained city layout optimization and civil infrastructure design.")
        ]
        for title, desc in agents:
            card = ctk.CTkFrame(scroll, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=10)
            card.pack(fill="x", pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#58a6ff").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=desc, text_color="#c9d1d9", wraplength=800).pack(anchor="w", padx=20, pady=(0, 15))
            ctk.CTkButton(card, text="INITIALIZE AGENT", width=150).pack(anchor="e", padx=20, pady=(0, 15))
        return frame

    def _create_science_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🔬 SCIENTIFIC RESEARCH AGENTS", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        agents = [
            ("🧬 Computational Biologist", "Genomic sequencing analysis, protein folding simulations, and biochemical pathway modeling."),
            ("⚛️ Particle Physicist", "Theoretical model formulation and experimental data analysis for high-energy physics."),
            ("🏺 Archaeologist/Historian", "Ancient text decipherment and historical cross-referencing for predictive archeology.")
        ]
        for title, desc in agents:
            card = ctk.CTkFrame(scroll, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=10)
            card.pack(fill="x", pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#1f6feb").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=desc, text_color="#c9d1d9", wraplength=800).pack(anchor="w", padx=20, pady=(0, 15))
            ctk.CTkButton(card, text="INITIALIZE AGENT", width=150, fg_color="#1f6feb").pack(anchor="e", padx=20, pady=(0, 15))
        return frame

    def _create_creative_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🎬 CREATIVE & MEDIA AGENTS", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        agents = [
            ("🎥 Cinematographer/Director", "Shot composition theory, storyboard generation, and film pacing optimization."),
            ("🎵 Music Composer", "Harmonic analysis, orchestral scoring, and automated track production."),
            ("🎮 Game Designer", "Mechanics balancing, narrative design, and player psychology modeling.")
        ]
        for title, desc in agents:
            card = ctk.CTkFrame(scroll, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=10)
            card.pack(fill="x", pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#d29922").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=desc, text_color="#c9d1d9", wraplength=800).pack(anchor="w", padx=20, pady=(0, 15))
            ctk.CTkButton(card, text="INITIALIZE AGENT", width=150, fg_color="#d29922").pack(anchor="e", padx=20, pady=(0, 15))
        return frame

    def _create_meta_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        ctk.CTkLabel(frame, text="🧠 META-ORCHESTRATION AGENTS", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=40)
        
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=40, pady=20)
        
        agents = [
            ("🏛️ The Architect", "Meta-agent for designing optimal team compositions for complex project objectives."),
            ("🧬 The Synthesizer", "Synthesizes disparate agent outputs into unified, coherent final products."),
            ("👹 The Adversary", "Permanent 'red team' agent focused on probing logic flaws and weak assumptions.")
        ]
        for title, desc in agents:
            card = ctk.CTkFrame(scroll, fg_color="#0d1117", border_width=1, border_color="#30363d", corner_radius=10)
            card.pack(fill="x", pady=10)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#8957e5").pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(card, text=desc, text_color="#c9d1d9", wraplength=800).pack(anchor="w", padx=20, pady=(0, 15))
            ctk.CTkButton(card, text="INITIALIZE AGENT", width=150, fg_color="#8957e5").pack(anchor="e", padx=20, pady=(0, 15))
        return frame

    def _create_history_frame(self):
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="MISSION HISTORY & ARCHIVES", font=ctk.CTkFont(size=32, weight="bold")).grid(row=0, column=0, padx=40, pady=(40, 20), sticky="w")
        
        content_f = ctk.CTkFrame(frame, fg_color="transparent")
        content_f.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content_f.grid_columnconfigure(0, weight=1)
        content_f.grid_columnconfigure(1, weight=3)
        content_f.grid_rowconfigure(0, weight=1)

        # File List
        list_f = ctk.CTkFrame(content_f, fg_color="#0d1117", border_width=1, border_color="#30363d")
        list_f.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(list_f, text="ARCHIVED LOGS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        self.history_scroll = ctk.CTkScrollableFrame(list_f, fg_color="transparent")
        self.history_scroll.pack(fill="both", expand=True)
        
        # Log Viewer
        viewer_f = ctk.CTkFrame(content_f, fg_color="#0d1117", border_width=1, border_color="#30363d")
        viewer_f.grid(row=0, column=1, sticky="nsew")
        
        self.history_text = ctk.CTkTextbox(viewer_f, fg_color="transparent", font=ctk.CTkFont(family="Consolas", size=12))
        self.history_text.pack(fill="both", expand=True, padx=10, pady=10)

        self._refresh_history_list()
        
        return frame

    def _refresh_history_list(self):
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
            
        archive_dir = os.path.join(PROJECT_ROOT, "logs", "archive")
        if os.path.exists(archive_dir):
            files = sorted(os.listdir(archive_dir), reverse=True)
            for f in files:
                btn = ctk.CTkButton(self.history_scroll, text=f, anchor="w", fg_color="transparent", 
                                    hover_color="#21262d", text_color="#c9d1d9",
                                    command=lambda name=f: self.load_archive_log(name))
                btn.pack(fill="x", padx=5, pady=2)
        else:
            ctk.CTkLabel(self.history_scroll, text="No archives found.").pack()

    def load_archive_log(self, filename):
        path = os.path.join(PROJECT_ROOT, "logs", "archive", filename)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                self.history_text.delete("1.0", "end")
                self.history_text.insert("1.0", content)
                self.log_status(f"Loaded {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")

    # --- SHARED HANDLERS ---
    def run_bio_evo_sim(self):
        sim_path = os.path.join(PROJECT_ROOT, "official_launch", "OMEGA_EVO_SIM_V3.html")
        if os.path.exists(sim_path):
            webbrowser.open(f"file://{sim_path}")
            self.log_status("Biological Sim Launched", "#d29922")
        else:
            messagebox.showerror("Error", "Simulation file not found in official_launch/.")

    def handle_report(self):
        generate_benchmarking_suite()
        messagebox.showinfo("Success", "Report Generated.")

    def handle_calc(self):
        calc_path = os.path.join(PROJECT_ROOT, "business", "marketing_assets", "savings_calculator.html")
        if os.path.exists(calc_path): webbrowser.open(f"file://{calc_path}")

    def toggle_mcp(self):
        if self.mcp_running: self.stop_mcp()
        else: self.start_mcp()

    def start_mcp(self):
        self.log_status("Launching MCP...", "#d29922")
        try:
            script = os.path.join(PROJECT_ROOT, "mcp_server.py")
            self.mcp_process = subprocess.Popen([sys.executable, script, "--transport", "sse", "--port", "8000"],
                                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
            self.mcp_running = True
            self.mcp_status_lbl.configure(text="STATUS: ONLINE", text_color="#3fb950")
            self.mcp_toggle_btn.configure(text="STOP MCP SERVER", fg_color="#f85149")
        except: pass

    def stop_mcp(self):
        if self.mcp_process: self.mcp_process.terminate(); self.mcp_process = None
        self.mcp_running = False
        self.mcp_status_lbl.configure(text="STATUS: OFFLINE", text_color="#f85149")
        self.mcp_toggle_btn.configure(text="START MCP SERVER", fg_color="#238636")

    def on_closing(self):
        self.stop_mcp()
        self.destroy()

    # TOKAMAK SPECIFIC
    def show_tokamak_validation(self): self.tokamak_selector.grid_forget(); self.tokamak_val_frame.grid(row=1, column=0, sticky="nsew")
    def reset_tokamak_view(self): self.tokamak_val_frame.grid_forget(); self.tokamak_selector.grid(row=1, column=0, sticky="nsew")
    def show_tokamak_analyst(self):
        messagebox.showinfo("Agent Zero", "Launching Analyst...")
        subprocess.Popen([sys.executable, "agent_zero/jobs/tokamak_analyst.py"])

    def run_tokamak_val(self):
        sensor = self.sensor_var.get()
        threading.Thread(target=self._bg_tok_val, args=(sensor,), daemon=True).start()

    def _bg_tok_val(self, sensor):
        subprocess.run([sys.executable, "tokamak/rcod_tokamak_validation.py", "--sensor", sensor])
        messagebox.showinfo("Complete", "Validation Done. Plot opened.")

    # ARENA SPECIFIC
    def run_arena(self):
        topic = self.arena_topic.get().strip()
        if not topic: return
        self.arena_log.insert("end", f"🏟️ Initializing tournament on: {topic}...\n")
        threading.Thread(target=self._bg_arena, args=(topic,), daemon=True).start()

    def _bg_arena(self, topic):
        cmd = [sys.executable, "agent_zero/jobs/arena.py"]
        # Use env copy to ensure PYTHONPATH
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in iter(proc.stdout.readline, ""):
            self.arena_log.insert("end", line)
            self.arena_log.see("end")
        proc.wait()
        self.arena_log.insert("end", "\n✅ TOURNAMENT COMPLETE.\n")

if __name__ == "__main__":
    app = OmegaControlPanel()
    app.mainloop()
