# simple.py v0.16.2 — True / Simple
# F50 DEFAULT_PROGRAM; F51 initial_text; F52 main.cycle; F53 T22;
# F54 op light green; F55 named<->action swap
#
# EBNF (grammar):
#   cycle        = { line "\n" } ;
#   line         = agent | separator | jump | condition | action | named | container ;
#   agent        = name "," color "| Data as <" type "> | Aim:" text ;
#   separator    = "" | "---" ;
#   jump         = "^" ( ":" cycle_name ":" num | num | name ) ;
#   condition    = expr "?" { action } ;
#   action       = src { "," src } op { "," dst } [ op ... ] ;
#   named        = [ value ] "=" name { "," name } ;
#   container    = text ;
#   op           = "=>" | "->" | "<->" | "=>|" | "->|" ;
#   src          = name | expr | axis_ref | line_ref ;
#   dst          = name | axis_ref | "::" ext | "::nothing" ;
#   expr         = term { ("+" | "-" | "*" | "/" | "%" | "^") term } ;
#   axis_ref     = name ":" ("x" | "y") [ "(" sep ")" ] [ ":" ( num | "first" | "last" ) ] ;
#   line_ref     = ":" [ cycle_name ] ":line:" num ;
#   ext          = "math" | "nothing" | name ;
#
# Priorities: agent > separator > jump > condition > action > named > container
import re, tkinter as tk, sys, os

PHI = 1.618
S = {"s":8, "m":13, "l":21, "xl":34, "xxl":55, "h":89}
BG, FG, ACCENT = "#1a1a1a", "#e8e0d0", "#c8a04a"
EDITOR_BG = "#202020"
EDITOR_BORDER = "#333333"
PANEL_BG = "#141414"
DEBUG = True
ESC_NL = "\\n"
LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple.log")
TEST_LOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple_test.log")
_log_fh = None
_test_log_fh = None

# --- Syntax highlight palette (golden-ratio hues) ---
HL = {
    "agent":     {"fg": "#5fb85f", "bg": "#1e2a1e"},   # soft green
    "named":     {"fg": "#5b9bd5", "bg": None},         # blue (F55)
    "action":    {"fg": "#7fb069", "bg": None},         # green (F55)
    "act":       {"fg": "#7fb069", "bg": None},         # green (inside condition)
    "cond":      {"fg": "#e8c547", "bg": None},         # yellow
    "op":        {"fg": "#a8d888", "bg": "#2a2a3a"},    # light green (F54)
    "jump":      {"fg": "#b07fd5", "bg": None},         # purple
    "container": {"fg": "#888888", "bg": None},         # gray
    "separator": {"fg": "#444444", "bg": None},         # dark gray
}

# --- F50: default program ---
DEFAULT_PROGRAM = """Mr.Green, #5fb85f | Data as <condition> | Aim: 1
Поднимайся на лифте Mr.Green :)

6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor == max ? -1 => dir
floor == 1 ? 1 => dir

floor + dir => ::math => floor"""

def log(msg):
    if not DEBUG: return
    print(msg)
    if _log_fh:
        try: _log_fh.write(msg + "\n"); _log_fh.flush()
        except Exception: pass

def tlog(msg):
    print(msg)
    if _test_log_fh:
        try: _test_log_fh.write(msg + "\n"); _test_log_fh.flush()
        except Exception: pass

AGENT_RE   = re.compile(r'^(?P<name>[\w.]+),\s*(?P<color>#[0-9a-fA-F]{6})\s*\|\s*Data as <(?P<typ>[^>]+)>\s*\|\s*Aim:\s*(?P<aim>.*)$')
JUMP_RE    = re.compile(r'^\^\s*(?P<target>.+)$')
COND_RE    = re.compile(r'^(?P<cond>.+?)\?\s*(?P<act>.*)$')
NAMED_RE   = re.compile(r'^(?P<val>.*?)\s*=\s*(?P<names>[\w,\s:]+)$')
ACTION_OP  = re.compile(r'(=>\||->\||<->|=>|->)')
AXIS_RE    = re.compile(r'^(?P<base>[\w.]+):(?P<axis>[xy])(?:\((?P<sep>[^)]*)\))?(?::(?P<idx>[\w]+))?$')
LINE_RE    = re.compile(r'^:(?P<cycle>[\w.]*):line:(?P<n>\d+)$')
AGENT_TYPE_RE = re.compile(r'Data as <[^>]*>')

def unescape_line(s):
    return re.sub(r'\\(.)', r'\1', s)

def escape_nl(s):
    return s.replace("\n", ESC_NL)

def unescape_nl(s):
    return s.replace(ESC_NL, "\n")

def update_agent_type(line, typ):
    return AGENT_TYPE_RE.sub(f'Data as <{typ}>', line, count=1)

def resolve_line(line):
    if AGENT_RE.match(line): return "agent", AGENT_RE.match(line)
    if not line.strip() or line.strip() == "---": return "separator", None
    if JUMP_RE.match(line): return "jump", JUMP_RE.match(line)
    if "?" in line and COND_RE.match(line): return "condition", COND_RE.match(line)
    if ACTION_OP.search(line): return "action", ACTION_OP.search(line)
    if NAMED_RE.match(line): return "named", NAMED_RE.match(line)
    return "container", None

def parse_actions(line):
    ops = list(ACTION_OP.finditer(line))
    if not ops: return []
    pairs = []; prev_end = 0
    for i, m in enumerate(ops):
        op = m.group(1)
        src = line[prev_end:m.start()].strip() if i == 0 else pairs[-1][2]
        end = ops[i+1].start() if i+1 < len(ops) else len(line)
        dst = line[m.end():end].strip()
        pairs.append((src, op, dst))
        prev_end = m.end()
    return pairs

def find_line_by_name(lines, name):
    for i, ln in enumerate(lines):
        t, m = resolve_line(ln)
        if t == "named" and m:
            names = [n.strip() for n in re.split(r'[,\s]+', m.group("names")) if n.strip()]
            if name in names: return i
    return -1

def parse_axis_ref(ref):
    m = AXIS_RE.match(ref)
    if not m: return None
    sep = m.group("sep")
    if sep is None:
        sep = "," if m.group("axis") == "y" else ""
    return m.group("base"), m.group("axis"), sep, m.group("idx")

def parse_line_ref(ref):
    m = LINE_RE.match(ref)
    if not m: return None
    return m.group("cycle") or None, int(m.group("n"))

def split_by_sep(s, sep):
    if sep and sep in s: return s.split(sep)
    if not sep: return list(s)
    if "," in s: return [x.strip() for x in s.split(",")]
    return [s]

def join_by_sep(items, sep):
    if not sep: return "".join(items)
    if sep == ", ": return ", ".join(items)
    return sep.join(items)

def remove_from_axis(model, cyc, ref):
    parsed = parse_axis_ref(ref)
    if not parsed: return False
    base, axis, sep, idx = parsed
    mem = model["memory"].setdefault(cyc["name"], {})
    if base not in mem: return False
    items = split_by_sep(mem[base], sep)
    if idx in (None, "", "all"): mem[base] = ""; return True
    if idx == "last": i = len(items) - 1
    elif idx == "first": i = 0
    else:
        try: i = int(idx) - 1
        except ValueError: return False
    if 0 <= i < len(items):
        items.pop(i); mem[base] = join_by_sep(items, sep)
        return True
    return False

def remove_line(model, cyc, ref):
    parsed = parse_line_ref(ref)
    if not parsed: return False
    cycle_name, n = parsed
    target_cyc = cyc
    if cycle_name and cycle_name != cyc["name"]:
        for c in model["cycles"]:
            if c["name"] == cycle_name: target_cyc = c; break
        else: return False
    idx = n - 1
    lines = target_cyc["lines"]
    if 0 <= idx < len(lines):
        del lines[idx]
        if target_cyc["agent"] > idx: target_cyc["agent"] -= 1
        elif target_cyc["agent"] == idx: target_cyc["agent"] = max(0, idx - 1)
        return True
    return False

def eval_expr(expr, mem):
    e = expr.strip()
    for name in sorted(mem.keys(), key=len, reverse=True):
        if name.startswith("::"): continue
        e = re.sub(r'\b' + re.escape(name) + r'\b', str(mem[name]), e)
    try:
        e2 = e.replace("^","**").replace("&&"," and ").replace("||"," or ")
        v = eval(e2, {"__builtins__":{}}, {})
        if isinstance(v, bool): return "1" if v else "0"
        if isinstance(v, float) and v.is_integer(): return str(int(v))
        return str(v)
    except Exception:
        return expr

def do_jump(model, cyc, target):
    t = target.strip()
    if t.startswith(":"):
        parts = t.strip(":").split(":")
        if len(parts) == 2:
            cycle_name, n = parts[0], parts[1]
            for i, c in enumerate(model["cycles"]):
                if c["name"] == cycle_name:
                    model["cur"] = i
                    n_int = int(n) - 1
                    model["cycles"][i]["agent"] = max(0, min(n_int, len(model["cycles"][i]["lines"])-1))
                    return True
        return False
    if t.isdigit():
        n_int = int(t) - 1
        cyc["agent"] = max(0, min(n_int, len(cyc["lines"])-1))
        return True
    idx = find_line_by_name(cyc["lines"], t)
    if idx >= 0:
        cyc["agent"] = idx
        return True
    return False

def exec_action(model, cyc, line):
    mem = model["memory"].setdefault(cyc["name"], {})
    line = unescape_line(line)
    for src_raw, op, dst in parse_actions(line):
        log(f"  [exec] src={src_raw!r} op={op!r} dst={dst!r}")

        if dst == "::nothing":
            if op in ("->", "->|"):
                if remove_line(model, cyc, src_raw): continue
                if remove_from_axis(model, cyc, src_raw): continue
                if src_raw in mem: mem.pop(src_raw, None)
            continue

        if "," in src_raw and not parse_axis_ref(src_raw) and not parse_line_ref(src_raw):
            srcs = [s.strip() for s in src_raw.split(",") if s.strip()]
        else:
            srcs = [src_raw]

        for src in srcs:
            if re.search(r'[+\-*/%^()]', src) and not parse_axis_ref(src) and not parse_line_ref(src):
                sv = eval_expr(src, mem)
            else:
                sv = mem.get(src, src)

            if dst.startswith("::") and not parse_axis_ref(dst):
                ext = dst[2:]
                if ext == "math":
                    mem["::math"] = eval_expr(src, mem)
                    log(f"  [math] {src!r} -> {mem['::math']!r}")
                else:
                    mem[dst] = sv
                continue

            parsed_dst = parse_axis_ref(dst)
            if parsed_dst:
                base, axis, sep, idx = parsed_dst
                cur = mem.get(base, "")
                sep_eff = sep if sep else ("\n" if axis == "y" else "")
                if idx is not None and idx not in ("last", "first", "all"):
                    try:
                        items = split_by_sep(cur, sep_eff)
                        items.insert(int(idx)-1, sv)
                        mem[base] = join_by_sep(items, sep_eff)
                    except Exception:
                        mem[base] = cur + sep_eff + sv if cur else sv
                else:
                    mem[base] = cur + sep_eff + sv if cur else sv
                continue

            targets = [t.strip() for t in dst.split(",") if t.strip()] or [dst]
            for target in targets:
                if   op == "=>": mem[target] = sv
                elif op == "->": mem[target] = sv; mem.pop(src, None)
                elif op == "<->": mem[src], mem[target] = mem.get(target, target), sv
        log(f"  [exec] mem={mem}")

def flush_memory_to_lines(cyc, model):
    mem = model["memory"].setdefault(cyc["name"], {})
    lines = cyc["lines"]
    for i, ln in enumerate(lines):
        if AGENT_RE.match(ln): continue
        t, m = resolve_line(ln)
        if t == "named" and m:
            names = [n.strip() for n in re.split(r'[,\s]+', m.group("names")) if n.strip()]
            if not names: continue
            primary = names[0]
            if primary in mem:
                val_esc = escape_nl(str(mem[primary]))
                new = f"{val_esc} = {', '.join(names)}"
                if new != ln:
                    lines[i] = new
                    log(f"  [flush] {i}: {ln!r} -> {new!r}")

def execute_line(model, cyc, target_idx):
    line = cyc["lines"][target_idx]
    typ, m = resolve_line(line)
    log(f"[type] {typ} :: {line!r}")
    if typ == "named":
        mem = model["memory"].setdefault(cyc["name"], {})
        for n in re.split(r'[,\s]+', m.group("names")):
            if n: mem[n] = unescape_nl(m.group("val"))
    elif typ == "condition":
        cond = m.group("cond").strip()
        act = m.group("act").strip()
        res = eval_expr(cond, model["memory"].setdefault(cyc["name"], {}))
        log(f"  [cond] {cond!r} -> {res!r}")
        try:
            truthy = float(res) != 0 if res.lstrip("-").replace(".","",1).isdigit() else res not in ("0","","False")
        except Exception:
            truthy = res not in ("0","","False")
        if truthy and act:
            exec_action(model, cyc, act)
    elif typ == "jump":
        do_jump(model, cyc, m.group("target"))
    elif typ == "action":
        exec_action(model, cyc, line)
    return typ

def step_engine(model):
    if not model["cycles"]: return
    cyc = model["cycles"][model["cur"]]
    lines = cyc["lines"]; a = cyc["agent"]
    if not lines: return
    target = a + 1
    if target >= len(lines):
        agent_line = lines[a]
        del lines[a]
        lines.insert(0, agent_line)
        cyc["agent"] = 0
        log(f"\n[step] rotate agent {a}->0")
        return
    log(f"\n[step] agent={a} target={target} n={len(lines)}")
    typ_target = execute_line(model, cyc, target)
    if typ_target and AGENT_RE.match(lines[a]):
        new_agent_line = update_agent_type(lines[a], typ_target)
        if new_agent_line != lines[a]:
            lines[a] = new_agent_line
            log(f"  [agent] type -> <{typ_target}>")
    flush_memory_to_lines(cyc, model)
    lines[a], lines[target] = lines[target], lines[a]
    cyc["agent"] = target
    log(f"[swap] {a}<->{target} agent->{target}")

# ---------- TEST RUNNER (F53) ----------
def run_tests():
    AG = "Mr.Green, #00ff00 | Data as <sep> | Aim: 1"
    tests = [
        ("T1 named",  [AG, "1 = a"], {"a":"1"}, 2),
        ("T2 empty named", [AG, "1 = a", "= b"], {"a":"1","b":""}, 3),
        ("T3 copy",   [AG, "1 = a", "a => b"], {"a":"1","b":"1"}, 3),
        ("T4 move",   [AG, "1 = a", "a -> b"], {"b":"1"}, 3),
        ("T5 cond true", [AG, "1 = dir", "dir > 0 ? 5 => x"], {"dir":"1","x":"5"}, 3),
        ("T6 cond false",[AG, "1 = dir", "dir < 0 ? 5 => x"], {"dir":"1"}, 3),
        ("T7 chain",  [AG, "1 = a", "a => b => c"], {"a":"1","b":"1","c":"1"}, 3),
        ("T8 math",   [AG, "1 = a", "2 = b", "a + b => ::math"], {"a":"1","b":"2","::math":"3"}, 3),
        ("T9 math chain", [AG, "1 = a", "2 = b", "a + b => ::math => c"],
         {"a":"1","b":"2","::math":"3","c":"3"}, 3),
        ("T10 nothing name", [AG, "1 = a", "a -> ::nothing"], {}, 3),
        ("T11 nothing copy", [AG, "1 = a", "a => ::nothing"], {"a":"1"}, 3),
        ("T12 axis y", [AG, "1, 2, 3 = l", "l:y(, ):last -> ::nothing"], {"l":"1, 2"}, 3),
        ("T13 multi-src + axis", [AG, "1 = a", "2 = b", "a, b => l:y(, )"],
         {"a":"1","b":"2","l":"1, 2"}, 3),
        ("T14 jump", [AG, "1 = a", "^ 1"], {"a":"1"}, 3),
        ("T15 empty named at start", [AG, "= x"], {"x":""}, 2),
        ("T16 insert no multi", [AG, "1 = a", "a =>| l:y(, )"],
         {"a":"1","l":"1"}, 3),
        ("T17 multi-src insert values", [AG, "1 = a", "a, a =>| l:y(, )"],
         {"a":"1","l":"1, 1"}, 3),
    ]
    passed = 0
    tlog("=== Simple tests v0.16.2 ===")
    for name, lines, exp, steps in tests:
        m = {"cycles":[{"name":"t.cycle","lines":lines[:],"agent":0,"color":"#00ff00"}],
             "memory":{},"cur":0,"playing":False,"ms":0}
        for _ in range(steps): step_engine(m)
        mem = m["memory"].get("t.cycle", {})
        ok = all(mem.get(k) == v for k, v in exp.items()) and set(mem.keys()) == set(exp.keys())
        if ok:
            tlog(f"  {name}: PASS"); passed += 1
        else:
            tlog(f"  {name}: FAIL mem={mem} exp={exp}")
    # T18 dynamic type
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "= b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    step_engine(m)
    agent_line = m["cycles"][0]["lines"][m["cycles"][0]["agent"]]
    t18_ok = "Data as <named>" in agent_line
    if t18_ok: tlog("  T18 dynamic type named: PASS"); passed += 1
    else: tlog(f"  T18 dynamic type named: FAIL agent={agent_line!r}")
    # T20: Step
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    step_engine(m)
    t20_ok = m["cycles"][0]["agent"] == 1
    if t20_ok: tlog("  T20 step once: PASS"); passed += 1
    else: tlog(f"  T20 step once: FAIL agent={m['cycles'][0]['agent']}")
    # T21: condition parts
    line = "dir > 0 ? 5 => x"
    typ, m2 = resolve_line(line)
    t21_ok = typ == "condition" and m2.group("cond").strip() == "dir > 0" and m2.group("act").strip() == "5 => x"
    if t21_ok: tlog("  T21 condition parts: PASS"); passed += 1
    else: tlog(f"  T21 condition parts: FAIL typ={typ}")
    # T22: default program
    t22_lines = DEFAULT_PROGRAM.split("\n")
    t22_ok = (t22_lines[0].startswith("Mr.Green") and
              resolve_line(t22_lines[1])[0] == "container")
    if t22_ok: tlog("  T22 default program: PASS"); passed += 1
    else: tlog(f"  T22 default program: FAIL line1={t22_lines[1]!r} type={resolve_line(t22_lines[1])[0]}")
    tlog(f"\n{passed}/{len(tests)+4} passed")
    return passed == len(tests)+4

# ---------- UI ----------
class Editor(tk.Frame):
    def __init__(s, parent, name, index):
        super().__init__(parent, bg=BG)
        s.name = name
        head = tk.Frame(s, bg=BG); head.pack(fill="x", pady=(0, S["s"]))
        tk.Label(head, text=f"#{index+1}  ·  {name}", bg=BG, fg=FG,
                 font=("TkDefaultFont", S["m"])).pack(side="left")
        body = tk.Frame(s, bg=EDITOR_BG); body.pack(fill="x")
        s.gutter = tk.Canvas(body, width=S["xl"], bg=EDITOR_BG,
                             highlightthickness=0, bd=0)
        s.gutter.pack(side="left", fill="y")
        s.text = tk.Text(body, height=5, width=60, bg=EDITOR_BG, fg=FG,
                         insertbackground=ACCENT, insertwidth=2,
                         font=("Monospace", S["m"]),
                         wrap="none", undo=True, bd=0, relief="flat",
                         highlightthickness=1,
                         highlightbackground=EDITOR_BORDER,
                         highlightcolor=ACCENT,
                         padx=S["s"], pady=S["s"])
        s.text.pack(side="left", fill="x", expand=True)
        for typ, c in HL.items():
            kw = {"foreground": c["fg"]}
            if c.get("bg"): kw["background"] = c["bg"]
            s.text.tag_config(typ, **kw)
        s.text.tag_config("agent", foreground=HL["agent"]["fg"],
                          background=HL["agent"]["bg"])
        s.on_change_cb = None
        s.on_focus_cb = None
        s._agent_idx = -1
        s.text.bind("<Button-1>", s._on_click)
        s.text.bind("<KeyRelease>", lambda e: (s.redraw_gutter(), s.on_change(), s.highlight_syntax()))
        s.text.bind("<Configure>", lambda e: s.redraw_gutter())
        s.text.bind("<<Modified>>", s._on_mod)
        s.menu = tk.Menu(s.text, tearoff=0,
                         bg=EDITOR_BG, fg=FG,
                         activebackground=ACCENT, activeforeground=BG,
                         bd=0, relief="flat")
        s.menu.add_command(label="Copy",  command=lambda: s.text.event_generate("<<Copy>>"))
        s.menu.add_command(label="Paste", command=lambda: s.text.event_generate("<<Paste>>"))
        s.menu.add_command(label="Cut",   command=lambda: s.text.event_generate("<<Cut>>"))
        s.menu.add_separator()
        s.menu.add_command(label="Select All",
                           command=lambda: s.text.tag_add("sel", "1.0", "end-1c"))
        s.text.bind("<Button-3>", s._show_menu)
        s.redraw_gutter()
        s.highlight_syntax()

    def _on_click(s, e):
        s.text.focus_set()
        if s.on_focus_cb: s.on_focus_cb()
        return None

    def _show_menu(s, e):
        try: s.menu.tk_popup(e.x_root, e.y_root)
        finally: s.menu.grab_release()
        return "break"

    def _on_mod(s, e):
        if s.text.edit_modified():
            s.redraw_gutter(); s.text.edit_modified(False)

    def on_change(s):
        if s.on_change_cb: s.on_change_cb()

    def fit_height(s):
        n = int(s.text.index("end-1c").split(".")[0])
        s.text.config(height=max(5, n))

    def highlight_syntax(s):
        for typ in ("separator", "container", "jump", "condition", "named",
                    "action", "cond", "act", "op"):
            s.text.tag_remove(typ, "1.0", "end")
        lines = s.text.get("1.0", "end-1c").split("\n")
        for i, line in enumerate(lines):
            typ, m = resolve_line(line)
            row = i + 1
            if typ == "agent":
                continue
            if typ == "condition" and m:
                s.text.tag_add("cond", f"{row}.{m.start('cond')}", f"{row}.{m.end('cond')}")
                if m.group("act"):
                    act_start = m.start("act")
                    act_end = m.end("act")
                    s.text.tag_add("act", f"{row}.{act_start}", f"{row}.{act_end}")
                    act_text = line[act_start:act_end]
                    for op_m in ACTION_OP.finditer(act_text):
                        s.text.tag_add("op",
                                       f"{row}.{act_start + op_m.start()}",
                                       f"{row}.{act_start + op_m.end()}")
            elif typ == "action":
                s.text.tag_add("action", f"{row}.0", f"{row}.end")
                for op_m in ACTION_OP.finditer(line):
                    s.text.tag_add("op", f"{row}.{op_m.start()}", f"{row}.{op_m.end()}")
            elif typ in HL:
                s.text.tag_add(typ, f"{row}.0", f"{row}.end")
        for t in ("cond", "act", "action", "op", "agent"):
            try: s.text.tag_raise(t)
            except Exception: pass

    def set_agent(s, idx):
        s.text.tag_remove("agent", "1.0", "end")
        lines = s.text.get("1.0", "end-1c").split("\n")
        if 0 <= idx < len(lines):
            s.text.tag_add("agent", f"{idx+1}.0", f"{idx+1}.end")
        s.text.tag_raise("agent")
        s._agent_idx = idx
        s.redraw_gutter()

    def redraw_gutter(s):
        s.gutter.delete("all")
        lines = s.text.get("1.0", "end-1c").split("\n")
        total = len(lines)
        for i in range(1, total+1):
            d = s.text.dlineinfo(f"{i}.0")
            if d is None: continue
            y = d[1]
            if i-1 == s._agent_idx: color, label = ACCENT, str(i)
            elif not lines[i-1].strip(): color, label = "#333333", "·"
            else: color, label = "#666666", str(i)
            s.gutter.create_text(S["xl"]-S["s"], y, anchor="ne",
                                 text=label, fill=color,
                                 font=("Monospace", S["m"]))

    def get_text(s): return s.text.get("1.0", "end-1c")
    def set_text(s, t):
        s.text.delete("1.0", "end"); s.text.insert("1.0", t)
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
        root.title("Simple — True v0.16.2")
        root.configure(bg=BG)
        s.model = {"cycles": [], "memory": {}, "cur": 0, "playing": False, "ms": 390}
        s.editors = []
        s._last_n = -1
        s.build()
        root.bind("<space>", lambda e: s.toggle())

    def build(s):
        bar = tk.Frame(s.root, bg=PANEL_BG, height=S["xxl"]); bar.pack(fill="x")
        bar.pack_propagate(False)
        s.btn = TButton(bar, "▶", s.toggle); s.btn.pack(side="left", padx=S["s"], pady=S["s"])
        s.btn_step = TButton(bar, "⏭", s.step_once, bg=FG); s.btn_step.pack(side="left", padx=S["s"])
        s.ms = tk.StringVar(value="390")
        tk.Entry(bar, textvariable=s.ms, width=6, bg=BG, fg=FG,
                 insertbackground=ACCENT, relief="flat", bd=0,
                 font=("Monospace", S["m"])).pack(side="left", padx=S["s"])
        TButton(bar, "+", lambda: s.add_editor(f"cycle{len(s.editors)+1}.cycle"),
                bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "⏮", s.reset, bg=FG).pack(side="left")

        s.canvas = tk.Canvas(s.root, bg=BG); s.canvas.pack(fill="both", expand=True)
        s.inner = tk.Frame(s.canvas, bg=BG)
        s.canvas.create_window((0,0), window=s.inner, anchor="nw")
        s.inner.bind("<Configure>",
                     lambda e: s.canvas.configure(scrollregion=s.canvas.bbox("all")))
        s.canvas.bind_all("<MouseWheel>", s._on_wheel)

        s.status = tk.Label(s.root, text="", bg=PANEL_BG, fg=FG, anchor="w",
                            font=("Monospace", S["m"]), height=1, padx=S["s"])
        s.status.pack(fill="x", side="bottom")
        s.add_editor("main.cycle", DEFAULT_PROGRAM)   # F52

    def _on_wheel(s, e):
        s.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def add_editor(s, name, initial_text=None):   # F51
        idx = len(s.editors)
        if idx > 0:
            tk.Frame(s.inner, bg=ACCENT, height=1).pack(fill="x", pady=S["s"])
        ed = Editor(s.inner, name, idx)
        ed.pack(fill="x", padx=S["s"], pady=(S["s"], S["s"]))
        ed.on_change_cb = s.sync_from_ui
        ed.on_focus_cb = s.pause
        s.editors.append(ed)
        s.model["cycles"].append({"name": name, "lines": [""],
                                  "agent": 0, "color": "#5fb85f"})
        if initial_text:
            ed.set_text(initial_text)

    def pause(s):
        if s.model["playing"]:
            s.model["playing"] = False
            s.btn.config(text="▶")
            s.update_status()

    def step_once(s):
        if s.model["playing"]:
            s.pause()
        s.sync_from_ui()
        step_engine(s.model)
        s.refresh_ui()

    def sync_from_ui(s):
        if s.model["playing"]: return
        for c, ed in zip(s.model["cycles"], s.editors):
            t = ed.get_text().rstrip("\n")
            c["lines"] = t.split("\n") if t else [""]
            ed.fit_height()
            if DEBUG and len(c["lines"]) != s._last_n:
                log(f"[sync] {c['name']} n={len(c['lines'])}")
                s._last_n = len(c["lines"])

    def reset(s):
        s.model["playing"] = False
        s.btn.config(text="▶")
        for c in s.model["cycles"]: c["agent"] = 0
        s.model["memory"].clear()
        s.refresh_ui()

    def refresh_ui(s):
        for c, ed in zip(s.model["cycles"], s.editors):
            new = "\n".join(c["lines"])
            if ed.get_text() != new:
                ed.set_text(new)
            ed.set_agent(c["agent"])
        s.update_status()

    def update_status(s):
        if not s.model["cycles"]: return
        c = s.model["cycles"][s.model["cur"]]
        n = len(c["lines"])
        sep = sum(1 for l in c["lines"] if not l.strip())
        st = "⏸" if s.model["playing"] else "▶"
        s.status.config(
            text=f" cycle={s.model['cur']+1}/{len(s.model['cycles'])}"
                 f"  agent={c['agent']}/{n} (sep={sep})"
                 f"  {st}  ms={s.model['ms']}"
                 f"  mem={s.model['memory'].get(c['name'], {})}"
        )

    def toggle(s):
        s.model["playing"] = not s.model["playing"]
        s.btn.config(text="⏸" if s.model["playing"] else "▶")
        if s.model["playing"]:
            s.sync_from_ui()
            s.tick()
        s.update_status()

    def tick(s):
        if not s.model["playing"]: return
        try: s.model["ms"] = max(0, int(s.ms.get()))
        except Exception: pass
        step_engine(s.model)
        s.refresh_ui()
        s.root.after(s.model["ms"], s.tick)

if __name__ == "__main__":
    if "--test" in sys.argv:
        _test_log_fh = open(TEST_LOG_PATH, "w", encoding="utf-8")
        ok = run_tests()
        _test_log_fh.close()
        sys.exit(0 if ok else 1)
    _log_fh = open(LOG_PATH, "w", encoding="utf-8")
    log(f"=== Simple v0.16.2 log ===")
    r = tk.Tk(); App(r)
    r.geometry(f"{S['xxl']*12}x{S['h']*5}")
    r.mainloop()
    _log_fh.close()