# simple.py — IDE, interpreter, presentation layer (threaded)
# Version: true 0.9.9 / !true 0.9.6
import os, glob, random, string, sys, threading, re, subprocess
import tkinter as tk
from tkinter import filedialog

from modules import (
    PHI, DEBUG, ESC_NL, ESC_CHAR, PH_OPEN, PH_CLOSE, HISTORY_MAX,
    TRUTH_PRINCIPLE, CORE_PRINCIPLE, TRUE_VERSION, NOT_TRUE_VERSION,
    log, set_log_fh, set_log_level,
    valid_name, entails, eval_expr, parse_ref,
)
from creator import Creator, UIBridge, Agent

S = {"s":8, "m":13, "l":21, "xl":34, "xxl":55, "h":89}
BG, FG, ACCENT = "#1a1a1a", "#e8e0d0", "#c8a04a"
EDITOR_BG = "#202020"
EDITOR_BORDER = "#333333"
PANEL_BG = "#141414"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
LOG_PATH = os.path.join(BASE_DIR, "simple.log")
TEST_LOG_PATH = os.path.join(BASE_DIR, "simple_test.log")

HL = {
    "agent":     {"fg": "#5fb85f", "bg": "#1e2a1e"},
    "agent_line":{"fg": "#5fb85f", "bg": None},
    "named":     {"fg": "#5b9bd5", "bg": None},
    "action":    {"fg": "#7fb069", "bg": None},
    "act":       {"fg": "#7fb069", "bg": None},
    "cond":      {"fg": "#e8c547", "bg": None},
    "op":        {"fg": "#a8d888", "bg": "#2a2a3a"},
    "jump":      {"fg": "#b07fd5", "bg": None},
    "container": {"fg": "#888888", "bg": None},
    "separator": {"fg": "#444444", "bg": None},
    "agent_type":{"fg": "#ffffff", "bg": "#3a3a3a"},
    "version":   {"fg": "#666666", "bg": None},
    "executing": {"fg": None, "bg": "#3a3a1a"},
    "axis_hit":  {"fg": "#ffff88", "bg": "#4a4a1a"},
}

DEFAULT_PROGRAM = """# version: 1
Mr.Green, #5fb85f | Data as <condition> | Aim: 0 | step: 0 | mode: 1
6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor >= max ? -1 => dir
floor <= 1 ? 1 => dir

floor + dir => ::math => floor"""

SAMPLES = {
    "elevator.cycle": DEFAULT_PROGRAM,
    "counter.cycle": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
0 = counter
counter + 1 ?=> counter
""",
    "matrix.tape": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0

123
456
789
= array2d

1 = i
1 = j

array2d:y:i:x:j % 2 == 0 ? X => array2d:y:i:x:j
array2d:y:i:x:j % 2 == 1 ? O => array2d:y:i:x:j

j + 1 ?=> j
j > 3 ? 1 => j
j == 1 ? i + 1 ?=> i
i > 3 ? ::agent:finish
""",
    "classes.tape": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
color: red; max_speed: 200; = args
car, args => ::gen
color; max_speed; = args
car_1.cycle, args => ::check
::agent:finish
""",
    "script.tape": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
1 = a
2 = b
0 = result
a + b => ::math => result
::agent:finish
""",
    "race_a.cycle": """# version: 1
Mr.Red, #d04040 | Data as <type> | Aim: 0 | step: 0 | mode: 1

:data.txt:line:1 => a
a + "-" => a
a => :data.txt:line:1
""",
    "race_b.cycle": """# version: 1
Mr.Blue, #4080d0 | Data as <type> | Aim: 0 | step: 0 | mode: 1

:data.txt:line:2 => b
b + "-" => b
b => :data.txt:line:2
""",
    "data.txt": """A: 
B: 
""",
    "double.fn": """= args
args * 2
= double
""",
    "concat.fn": """= args
Pet
+ rov
= surname

= args
my name is ${=> surname}
= main
""",
    "counter.fn": """= args
1
+ 1
= inc
""",
}

class Editor(tk.Frame):
    def __init__(s, parent, name, index, app):
        super().__init__(parent, bg=BG)
        s.name = name
        s.app = app
        s._hl_cache = {}
        head = tk.Frame(s, bg=BG); head.pack(fill="x", pady=(0, S["s"]))
        s.indicator = tk.Label(head, text="●", bg=BG, fg="#444444",
                               font=("TkDefaultFont", S["m"]))
        s.indicator.pack(side="left", padx=(0, S["s"]))
        tk.Label(head, text=f"#{index+1}  ·  {name}", bg=BG, fg=FG,
                 font=("TkDefaultFont", S["m"])).pack(side="left")
        close_btn = tk.Label(head, text="×", bg=BG, fg="#888888",
                             font=("TkDefaultFont", S["m"]), cursor="hand2")
        close_btn.pack(side="right", padx=S["s"])
        close_btn.bind("<Button-1>", lambda e: s.app.close_editor(s.name))
        body = tk.Frame(s, bg=EDITOR_BG); body.pack(fill="both", expand=True)
        s.gutter = tk.Canvas(body, width=S["xl"], bg=EDITOR_BG,
                             highlightthickness=0, bd=0)
        s.gutter.pack(side="left", fill="y", pady=S["s"])
        s.text = tk.Text(body, height=5, width=60, bg=EDITOR_BG, fg=FG,
                         insertbackground=ACCENT, insertwidth=2,
                         font=("Monospace", S["m"]),
                         wrap="none", undo=True, bd=0, relief="flat",
                         highlightthickness=1,
                         highlightbackground=EDITOR_BORDER,
                         highlightcolor=ACCENT,
                         padx=S["s"], pady=S["s"])
        s.text.pack(side="left", fill="both", expand=True)
        for typ, c in HL.items():
            kw = {"foreground": c["fg"]}
            if c.get("bg"): kw["background"] = c["bg"]
            s.text.tag_config(typ, **kw)
        s.on_change_cb = None
        s.on_focus_cb = None
        s._agent_idx = -1
        s.text.bind("<Button-1>", s._on_click)
        s.text.bind("<KeyRelease>", lambda e: (s.redraw_gutter(), s.on_change(), s.highlight_syntax()))
        s.text.bind("<Configure>", lambda e: s.redraw_gutter())
        s.redraw_gutter()
        s.highlight_syntax()

    def _on_click(s, e):
        s.text.focus_set()
        if s.on_focus_cb: s.on_focus_cb()
        return None

    def on_change(s):
        if s.on_change_cb: s.on_change_cb()

    def fit_height(s):
        n = int(s.text.index("end-1c").split(".")[0])
        s.text.config(height=max(5, n))

    def highlight_syntax(s):
        for typ in list(HL.keys()) + ["cond", "act"]:
            s.text.tag_remove(typ, "1.0", "end")
        lines = s.text.get("1.0", "end-1c").split("\n")
        for i, line in enumerate(lines):
            if line in s._hl_cache:
                tags = s._hl_cache[line]
            else:
                tags = s.app.creator.highlight_tags(line)
                if i == 0 and "," in line and "#" in line and "Data as" in line:
                    mcol = re.search(r'#([0-9a-fA-F]{6})', line)
                    if mcol:
                        s.text.tag_config("agent_line", foreground="#" + mcol.group(1))
                    tags.append(("agent_line", 0, len(line)))
                s._hl_cache[line] = tags
            row = i + 1
            for tag, start, end in tags:
                s.text.tag_add(tag, f"{row}.{start}", f"{row}.{end}")
        for t in ("cond", "act", "action", "op", "agent_line", "agent_type", "agent", "version", "executing", "axis_hit"):
            try: s.text.tag_raise(t)
            except Exception: pass

    def set_agent(s, idx, executing=None, agent_color=None):
        s.text.tag_remove("agent", "1.0", "end")
        s.text.tag_remove("executing", "1.0", "end")
        if agent_color:
            s.text.tag_config("agent", foreground=agent_color)
        lines = s.text.get("1.0", "end-1c").split("\n")
        if 0 <= idx < len(lines):
            s.text.tag_add("agent", f"{idx+1}.0", f"{idx+1}.end")
            s.text.see(f"{idx+1}.0")
        if executing is not None and 0 <= executing < len(lines):
            s.text.tag_add("executing", f"{executing+1}.0", f"{executing+1}.end")
        s.text.tag_raise("executing")
        s.text.tag_raise("agent")
        s._agent_idx = idx
        s.redraw_gutter()

    def set_running(s, running, agent_color="#5fb85f"):
        color = agent_color if running else "#444444"
        s.indicator.config(fg=color)

    def set_axis_hit(s, row):
        s.text.tag_remove("axis_hit", "1.0", "end")
        if row is not None:
            lines = s.text.get("1.0", "end-1c").split("\n")
            if 0 <= row < len(lines):
                s.text.tag_add("axis_hit", f"{row+1}.0", f"{row+1}.end")
                s.text.tag_raise("axis_hit")

    def redraw_gutter(s):
        s.gutter.delete("all")
        lines = s.text.get("1.0", "end-1c").split("\n")
        total = len(lines)
        for i in range(1, total+1):
            d = s.text.dlineinfo(f"{i}.0")
            if d is None: continue
            y = d[1] + d[3]//2 - S["s"]//2
            if i-1 == s._agent_idx: color, label = ACCENT, str(i)
            elif not lines[i-1].strip(): color, label = "#333333", "·"
            else: color, label = "#666666", str(i)
            s.gutter.create_text(S["xl"]-S["s"], y, anchor="e",
                                 text=label, fill=color,
                                 font=("Monospace", S["m"]))

    def get_text(s): return s.text.get("1.0", "end-1c")
    def set_text(s, t):
        s.text.delete("1.0", "end"); s.text.insert("1.0", t)
        s.text.see("1.0")
        s._hl_cache = {}
        s.fit_height()
        s.redraw_gutter()
        s.highlight_syntax()

def TButton(parent, text, cmd, bg=ACCENT, fg=BG, w=S["xl"]):
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                     font=("TkDefaultFont", S["m"]), width=w//S["m"],
                     relief="flat", bd=0, highlightthickness=0,
                     activebackground=bg, activeforeground=fg, cursor="hand2")

class App:
    def __init__(s, root):
        s.root = root
        root.title(f"Simple — true {TRUE_VERSION} / !true {NOT_TRUE_VERSION}")
        root.configure(bg=BG)
        s.model = {"cycles": [], "memory": {}, "cur": 0, "playing": False, "ms": 390, "step_count": 0}
        s.editors = []
        s.creator = Creator(s.model, UIBridge(s))
        s.build()
        s.creator.load_all_fns(BASE_DIR)
        root.bind("<Control-space>", lambda e: s.toggle())
        root.bind("<Control-s>", lambda e: s.save_cycle())

    def exit(s):
        s.root.after(0, s.root.destroy)

    def build(s):
        bar = tk.Frame(s.root, bg=PANEL_BG, height=S["xxl"]); bar.pack(fill="x")
        bar.pack_propagate(False)
        s.btn = TButton(bar, "▶", s.toggle); s.btn.pack(side="left", padx=S["s"], pady=S["s"])
        s.btn_back = TButton(bar, "⏪", s.step_back, bg=FG); s.btn_back.pack(side="left", padx=S["s"])
        s.btn_fwd = TButton(bar, "⏩", s.step_forward, bg=FG); s.btn_fwd.pack(side="left", padx=S["s"])
        s.ms = tk.StringVar(value="390")
        tk.Entry(bar, textvariable=s.ms, width=6, bg=BG, fg=FG,
                 insertbackground=ACCENT, relief="flat", bd=0,
                 font=("Monospace", S["m"])).pack(side="left", padx=S["s"])
        TButton(bar, "+", lambda: s.add_editor(f"cycle{len(s.editors)+1}.cycle"), bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "📂", s.open_file_dialog, bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "💾", s.save_cycle, bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "⏮", s.reset, bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "terminal", s.open_terminal, bg=FG).pack(side="left", padx=S["s"])

        main = tk.Frame(s.root, bg=BG); main.pack(fill="both", expand=True)
        left = tk.Frame(main, bg=BG); left.pack(side="left", fill="both", expand=True)
        s.canvas = tk.Canvas(left, bg=BG); s.canvas.pack(fill="both", expand=True)
        s.inner = tk.Frame(s.canvas, bg=BG)
        s._inner_win = s.canvas.create_window((0,0), window=s.inner, anchor="nw")
        s.inner.bind("<Configure>",
                     lambda e: s.canvas.configure(scrollregion=s.canvas.bbox("all")))
        s.canvas.bind("<Configure>", s._on_canvas_resize)

        right = tk.Frame(main, bg=PANEL_BG, width=200)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="samples", bg=PANEL_BG, fg=FG,
                 font=("TkDefaultFont", S["m"])).pack(anchor="w", padx=S["s"], pady=S["s"])
        s.sample_filter = tk.StringVar(value="true")
        filt_frame = tk.Frame(right, bg=PANEL_BG)
        filt_frame.pack(fill="x", padx=S["s"], pady=(0, S["s"]))
        for label, val in (("true", "true"), ("!true", "!true")):
            b = tk.Radiobutton(filt_frame, text=label, variable=s.sample_filter,
                               value=val, command=s.refresh_samples,
                               bg=PANEL_BG, fg=FG, selectcolor=EDITOR_BG,
                               activebackground=PANEL_BG, activeforeground=ACCENT,
                               font=("TkDefaultFont", S["m"]), indicatoron=False,
                               relief="flat", bd=0, padx=S["s"])
            b.pack(side="left", fill="x", expand=True)
        s.samples_list = tk.Listbox(right, bg=EDITOR_BG, fg=FG,
                                    selectbackground=ACCENT, selectforeground=BG,
                                    font=("Monospace", S["m"]),
                                    bd=0, highlightthickness=0)
        s.samples_list.pack(fill="both", expand=True, padx=S["s"], pady=(0, S["s"]))
        s.samples_list.bind("<<ListboxSelect>>", s._on_sample_click)

        s.status = tk.Label(s.root, text="", bg=PANEL_BG, fg=FG, anchor="w",
                            font=("Monospace", S["m"]), height=1, padx=S["s"])
        s.status.pack(fill="x", side="bottom")
        main_path = os.path.join(BASE_DIR, "main.cycle")
        if os.path.isfile(main_path):
            try:
                with open(main_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if not content.lstrip().startswith("# version"):
                    content = "# version: 1\n" + content
                s.add_editor("main.cycle", content)
            except Exception:
                s.add_editor("main.cycle", DEFAULT_PROGRAM)
        else:
            s.add_editor("main.cycle", DEFAULT_PROGRAM)
        s.refresh_samples()

    def open_terminal(s):
        """Открывает системный терминал по умолчанию (Linux/macOS/Windows)."""
        try:
            if sys.platform == "win32":
                subprocess.Popen("start cmd", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                for cmd in (["x-terminal-emulator"], ["gnome-terminal"], ["konsole"], ["xterm"]):
                    try:
                        subprocess.Popen(cmd)
                        return
                    except FileNotFoundError:
                        continue
                log("terminal: no emulator found", "WARN")
        except Exception as e:
            log(f"terminal: {e}", "ERROR")

    def _on_canvas_resize(s, e):
        s.canvas.itemconfig(s._inner_win, width=e.width)

    def refresh_ui(s):
        for i, (c, ed) in enumerate(zip(s.model["cycles"], s.editors)):
            new = "\n".join(c["lines"])
            if ed.get_text() != new:
                ed.text.delete("1.0", "end")
                ed.text.insert("1.0", new)
                ed.fit_height()
                ed.redraw_gutter()
                ed.highlight_syntax()
            executing = c.get("agent_pos", 0) + 1 if c.get("agent_pos", 0) + 1 < len(c["lines"]) else None
            agent = s.creator.agents.get(c["name"])
            running = agent.running if agent else False
            agent_color = agent.color if agent else "#5fb85f"
            ed.set_agent(c.get("agent_pos", 0), executing=executing, agent_color=agent_color)
            ed.set_running(running, agent_color)
            last_ref = s.model.get("last_axis_ref")
            if last_ref:
                p = parse_ref(last_ref)
                if p and p["kind"] in ("axis", "axis_chain"):
                    base = p["base"]
                    for j, ln in enumerate(c["lines"]):
                        t, m = s.creator.resolve_line(ln)
                        if t == "named":
                            names = []
                            if s.creator.is_named_node(m): names = m.names
                            elif hasattr(m, "group"):
                                try: names = [n.strip() for n in re.split(r'[,\s]+', m.group("names")) if n.strip()]
                                except Exception: names = []
                            if base in names:
                                ed.set_axis_hit(j)
                                break
        s.update_status()

    def update_status(s):
        if not s.model["cycles"]: return
        c = s.model["cycles"][s.model["cur"]]
        n = len(c["lines"])
        st = "⏸" if s.model["playing"] else "▶"
        kind = "cycle" if c.get("loop", True) else "tape"
        s.status.config(
            text=f" {kind} {s.model['cur']+1}/{len(s.model['cycles'])}"
                 f"  agent={c.get('agent_pos', 0)}/{n}"
                 f"  {st}  ms={s.model['ms']}"
                 f"  hist={len(s.creator.runner.history.events) if s.creator else 0}"
                 f"  step={s.model.get('step_count', 0)}"
                 f"  mem={s.model['memory'].get(c['name'], {})}"
        )

    def toggle(s):
        s.model["playing"] = not s.model["playing"]
        s.btn.config(text="⏸" if s.model["playing"] else "▶")
        if s.model["playing"]:
            s.sync_from_ui()
            s.creator.start_all_threads()
        else:
            s.creator.stop_all_threads()
        s.update_status()

    def pause(s):
        if s.model["playing"]:
            s.model["playing"] = False
            s.btn.config(text="▶")
            s.creator.stop_all_threads()
            s.update_status()

    def step_forward(s):
        if s.model["playing"]: s.pause()
        s.sync_from_ui()
        s.creator.step_forward()
        for c in s.model["cycles"]:
            agent = s.creator.agents.get(c["name"])
            if agent and c["lines"]:
                agent.step = s.model.get("step_count", 0)
                pos = c.get("agent_pos", 0)
                if 0 <= pos < len(c["lines"]):
                    agent.focus = c["lines"][pos]
                    typ, _ = s.creator.resolve_line(agent.focus)
                    agent.line_type = typ
                    agent.typ = typ
                if agent.parse(c["lines"][0]) is not False:
                    c["lines"][0] = agent.to_line()
        s.refresh_ui()

    def step_back(s):
        if s.model["playing"]: s.pause()
        ev = s.creator.step_back()
        if ev is None: return
        s.refresh_ui()

    def on_key_change(s):
        if s.model["playing"]: return
        s.sync_from_ui()

    def sync_from_ui(s):
        with s.creator.lock:
            for c, ed in zip(s.model["cycles"], s.editors):
                t = ed.get_text().rstrip("\n")
                c["lines"] = t.split("\n") if t else [""]
                c["loop"] = c["name"].endswith(".cycle")
                ed.fit_height()
                if c["lines"]:
                    agent = Agent()
                    if agent.parse(c["lines"][0]):
                        s.creator.agents[c["name"]] = agent
                        c["has_agent"] = True
                    else:
                        s.creator.agents.pop(c["name"], None)
                        c["has_agent"] = False

    def close_editor(s, name):
        for i, (c, ed) in enumerate(zip(s.model["cycles"], s.editors)):
            if c["name"] == name:
                s.creator.stop_all_threads()
                s.model["cycles"].pop(i)
                s.creator.agents.pop(name, None)
                s.creator.threads.pop(name, None)
                ed.destroy()
                s.editors.pop(i)
                if s.model["cur"] >= len(s.model["cycles"]):
                    s.model["cur"] = max(0, len(s.model["cycles"]) - 1)
                s.refresh_ui()
                return

    def add_editor(s, name, initial_text=None):
        idx = len(s.editors)
        if idx > 0:
            tk.Frame(s.inner, bg=ACCENT, height=1).pack(fill="x", pady=S["s"])
        ed = Editor(s.inner, name, idx, s)
        ed.pack(fill="both", expand=True, padx=S["s"], pady=(S["s"], S["s"]))
        ed.on_change_cb = s.on_key_change
        ed.on_focus_cb = s.pause
        s.editors.append(ed)
        lines_init = initial_text.split("\n") if initial_text else [""]
        loop = name.endswith(".cycle")
        s.model["cycles"].append({"name": name, "lines": lines_init,
                                  "agent_pos": 0, "color": "#5fb85f", "loop": loop,
                                  "has_agent": False})
        if initial_text:
            ed.set_text(initial_text)
        if lines_init:
            agent = Agent()
            if agent.parse(lines_init[0]):
                s.creator.agents[name] = agent
                s.model["cycles"][-1]["has_agent"] = True
        path = os.path.join(BASE_DIR, name)
        if not os.path.isfile(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(initial_text or "")
            except Exception: pass

    def open_path(s, path):
        if os.path.isdir(path):
            for p in sorted(glob.glob(os.path.join(path, "*"))):
                s._open_file(p)
        else:
            s._open_file(path)

    def _open_file(s, path):
        if not os.path.isfile(path): return
        try:
            with open(path, "r", encoding="utf-8") as f: content = f.read()
        except Exception: return
        s.add_editor(os.path.basename(path), content)

    def refresh_samples(s):
        s.samples_list.delete(0, "end")
        s.samples_files = []
        if not os.path.isdir(SAMPLES_DIR): return
        filt = s.sample_filter.get() if hasattr(s, "sample_filter") else "true"
        if filt == "true":
            patterns = ["*.cycle", "*.tape"]
        else:
            patterns = ["*.fn"]
        files = []
        for pat in patterns:
            files.extend(glob.glob(os.path.join(SAMPLES_DIR, pat)))
        for path in sorted(files):
            name = os.path.basename(path)
            s.samples_list.insert("end", name)
            s.samples_files.append(path)

    def _on_sample_click(s, e):
        sel = s.samples_list.curselection()
        if not sel: return
        idx = sel[0]
        if idx >= len(s.samples_files): return
        path = s.samples_files[idx]
        name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return
        s.model["playing"] = False
        s.btn.config(text="▶")
        s.creator.stop_all_threads()
        s.add_editor(name, content)
        s.refresh_ui()

    def save_cycle(s):
        if not s.model["cycles"]: return
        cur = s.model["cycles"][s.model["cur"]]
        s.creator.save_cycle(cur["name"])

    def open_file_dialog(s):
        path = filedialog.askopenfilename(title="Open file")
        if path:
            s.open_path(path)

    def reset(s):
        s.model["playing"] = False
        s.btn.config(text="▶")
        s.creator.stop_all_threads()
        if s.model["cycles"]:
            c = s.model["cycles"][s.model["cur"]]
            path = os.path.join(BASE_DIR, c["name"])
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    if s.editors:
                        s.editors[s.model["cur"]].set_text(content)
                        s.sync_from_ui()
                except Exception:
                    pass
        s.creator.reset()
        s.refresh_ui()

def ensure_samples():
    if not os.path.isdir(SAMPLES_DIR):
        try: os.makedirs(SAMPLES_DIR)
        except Exception: return
    for old_name in ("classes.cycle", "matrix.cycle"):
        p = os.path.join(SAMPLES_DIR, old_name)
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
    for name, content in SAMPLES.items():
        path = os.path.join(SAMPLES_DIR, name)
        need_write = False
        if not os.path.exists(path):
            need_write = True
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    old = f.read()
                if ("Aim: 1" in old or "Aim:" not in old
                    or not old.lstrip().startswith("# version")
                    or "8 = floor" in old
                    or (name == "script.tape" and "0 = result" not in old)):
                    need_write = True
            except Exception:
                need_write = True
        if need_write:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception: pass

if __name__ == "__main__":
    LOG = "--log" in sys.argv
    QUIET = "--quiet" in sys.argv
    if "--test" in sys.argv:
        set_log_fh(open(TEST_LOG_PATH, "w", encoding="utf-8"))
        set_log_level("INFO" if QUIET else "DEBUG")
        import tests as _tests
        try:
            ok = _tests.run_tests()
        except Exception as e:
            print(f"TESTS CRASH: {e}")
            log(f"TESTS CRASH: {e}", "ERROR")
            ok = False
        set_log_fh(None)
        sys.exit(0 if ok else 1)
    if "--stress" in sys.argv:
        random.seed(42)
        bad = 0
        import true as T_stress
        for _ in range(5000):
            n = random.randint(0, 40)
            s = "".join(random.choice(string.printable) for _ in range(n))
            try:
                T_stress.resolve_line(s)
            except Exception as e:
                bad += 1
                print("STRESS FAIL:", repr(s), e)
        print(f"STRESS resolve_line: {5000-bad}/5000 ok")
        sys.exit(0 if bad == 0 else 1)
    ensure_samples()
    if LOG:
        set_log_fh(open(LOG_PATH, "w", encoding="utf-8"))
        set_log_level("DEBUG")
    log("=== Simple start ===")
    r = tk.Tk(); App(r)
    r.geometry(f"{S['xxl']*14}x{S['h']*5}")
    r.mainloop()