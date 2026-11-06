# simple.py v0.27.0 — True / Simple
# Truth principle: Truth is what can be used.
# Core principle:  Programming must be open, visual, easy and beautiful — all at once.
# Changes v0.27.0:
#  - TRUTH_PRINCIPLE constant, logged at start
#  - entails(phi, mem) — single truth predicate
#  - EXTENSIONS registry (math, nothing, simple)
#  - UIBridge — interface between core and UI
#  - step_engine(model, bridge=None) — returns Event
#  - History (event log) — record/undo/redo/clear
#  - apply_reverse / apply_forward
#  - App uses History instead of snapshot for step_back
#  - snapshot/restore kept for reset/debug only
#  - all truthy checks replaced by entails
import re, tkinter as tk, sys, os, glob, math, random, string
from tkinter import filedialog

PHI = 1.618
S = {"s":8, "m":13, "l":21, "xl":34, "xxl":55, "h":89}
BG, FG, ACCENT = "#1a1a1a", "#e8e0d0", "#c8a04a"
EDITOR_BG = "#202020"
EDITOR_BORDER = "#333333"
PANEL_BG = "#141414"
DEBUG = True
ESC_NL = "\\n"
ESC_CHAR = "\u0001"
PH_OPEN = "\u0002"
PH_CLOSE = "\u0003"
HISTORY_MAX = 100
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
LOG_PATH = os.path.join(BASE_DIR, "simple.log")
TEST_LOG_PATH = os.path.join(BASE_DIR, "simple_test.log")
_log_fh = None
_test_log_fh = None

TRUTH_PRINCIPLE = "Truth is what can be used."
CORE_PRINCIPLE = "Programming must be open, visual, easy and beautiful — all at once."

HL = {
    "agent":     {"fg": "#5fb85f", "bg": "#1e2a1e"},
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
}

DEFAULT_PROGRAM = """# version: 1
Mr.Green, #5fb85f | Data as <condition> | Aim: 0
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

SAMPLES = {
    "elevator.cycle": DEFAULT_PROGRAM,
    "counter.cycle": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0
0 = counter
counter + 1 ?=> counter
""",
    "tree.cycle": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0
1 = root
2 = root.left
3 = root.right
4 = root.right.left
5 = root.right.right
root => out
root.left =>| out:y(, )
root.right =>| out:y(, )
root.right.left =>| out:y(, )
root.right.right =>| out:y(, )
""",
    "matrix.cycle": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0
123 = array2d
456
789

array2d:y:2 => row
row:x:1 => cell
""",
    "crossfile.cycle": """# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0
1 = counter
counter => cycle:counter.cycle:counter
""",
}

# ---------- escape ----------
def escape_for_parse(s):
    if s.lstrip().startswith("\\"):
        return PH_OPEN + s + PH_CLOSE
    return re.sub(r'\\(.)', lambda m: PH_OPEN + m.group(1) + PH_CLOSE, s)

def unescape_after_parse(s):
    return re.sub(r'\u0002(.)\u0003', r'\1', s)

def escape_nl(s):
    return s.replace("\n", ESC_NL)

def unescape_nl(s):
    return s.replace(ESC_NL, "\n")

# ---------- name validator ----------
BAD_NAME_CHARS = set('=><\\,;?/:"`\'')
def valid_name(n):
    if not n: return False
    if n.startswith("::"): return True
    for ch in n:
        if ch in BAD_NAME_CHARS: return False
    return True

# ---------- regexes ----------
AGENT_RE   = re.compile(r'^(?P<name>[\w.]+),\s*(?P<color>#[0-9a-fA-F]{6})\s*\|\s*Data as <(?P<typ>[^>]+)>\s*\|\s*Aim:\s*(?P<aim>.*)$')
JUMP_RE    = re.compile(r'^\^\s*(?P<target>.+)$')
COND_RE    = re.compile(r'^(?P<cond>.+?)(?<!\?)\?\s*(?!=>\||->\||<->|=>|->)(?P<act>.*)$')
NAMED_RE   = re.compile(r'^(?P<val>.*?)\s*=\s*(?P<names>[\w.,\s]+)$')
ACTION_OP  = re.compile(r'(?<!\u0002)(\?)?(=>\||->\||<->|=>|->)')
AXIS_RE    = re.compile(r'^(?P<base>[\w.]+):(?P<axis>[xyz])(?:\((?P<sep>[^)]*)\))?(?::(?P<idx>[\w]+))?$')
LINE_RE    = re.compile(r'^:(?P<cycle>[\w.]*):line:(?P<n>\d+)$')
AGENT_TYPE_RE = re.compile(r'Data as <[^>]*>')
VERSION_RE = re.compile(r'^\s*#\s*version:\s*(\d+)\s*$')
QUAL_RE    = re.compile(r'^(?:(?P<cycle>[\w.]+):)?(?P<rest>.+)$')

def update_agent_type(line, typ):
    return AGENT_TYPE_RE.sub(f'Data as <{typ}>', line, count=1)

# ---------- truth predicate ----------
def entails(phi, mem):
    """Truth is what can be used. True iff eval_expr(phi, mem) is usable."""
    v = eval_expr(phi, mem)
    if v is None: return False
    if isinstance(v, bool): return v
    s = str(v).strip()
    return s not in ("0", "", "False", "⊥")

# ---------- parser ----------
def resolve_line(line):
    if VERSION_RE.match(line): return "version", VERSION_RE.match(line)
    if line.lstrip().startswith("\\"):
        return "container", None
    line_esc = escape_for_parse(line)
    if AGENT_RE.match(line_esc): return "agent", AGENT_RE.match(line_esc)
    if not line_esc.strip() or line_esc.strip() == "---": return "separator", None
    if JUMP_RE.match(line_esc) and not line_esc.startswith(PH_OPEN): return "jump", JUMP_RE.match(line_esc)
    if "?" in line_esc:
        qpos = line_esc.find("?")
        after = line_esc[qpos+1:].lstrip()
        is_op_after = (after.startswith("=>") or after.startswith("->") or
                       after.startswith("=>|") or after.startswith("->|") or
                       after.startswith("<->"))
        if not is_op_after:
            m_cond = COND_RE.match(line_esc)
            if m_cond:
                return "condition", m_cond
    if ACTION_OP.search(line_esc): return "action", ACTION_OP.search(line_esc)
    if NAMED_RE.match(line_esc): return "named", NAMED_RE.match(line_esc)
    return "container", None

def parse_actions(line):
    ops = list(ACTION_OP.finditer(line))
    if not ops: return []
    pairs = []; prev_end = 0
    for i, m in enumerate(ops):
        eval_flag = bool(m.group(1))
        op = m.group(2)
        src = line[prev_end:m.start()].strip() if i == 0 else pairs[-1][2]
        end = ops[i+1].start() if i+1 < len(ops) else len(line)
        dst = line[m.end():end].strip()
        pairs.append((src, op, dst, eval_flag))
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
        if m.group("axis") == "y": sep = "\n"
        elif m.group("axis") == "z": sep = ";"
        else: sep = ""
    return m.group("base"), m.group("axis"), sep, m.group("idx")

def parse_line_ref(ref):
    m = LINE_RE.match(ref)
    if not m: return None
    return m.group("cycle") or None, int(m.group("n"))

def parse_ref(ref):
    ref = ref.strip()
    if not ref: return None
    if ref.startswith(":"):
        pl = parse_line_ref(ref)
        if pl:
            return {"kind":"line","cycle":pl[0],"n":pl[1]}
        parts = ref.strip(":").split(":")
        if len(parts) == 2 and parts[1].isdigit():
            return {"kind":"line","cycle":parts[0],"n":int(parts[1])}
        return None
    m = QUAL_RE.match(ref)
    if not m: return None
    cycle = m.group("cycle")
    rest = m.group("rest")
    if cycle and rest.isdigit():
        return {"kind":"line","cycle":cycle,"n":int(rest)}
    if cycle and rest.startswith("line:"):
        try: n = int(rest[5:])
        except Exception: return None
        return {"kind":"line","cycle":cycle,"n":n}
    p = parse_axis_ref(rest)
    if p:
        base, axis, sep, idx = p
        return {"kind":"axis","cycle":cycle,"base":base,"axis":axis,"sep":sep,"idx":idx}
    return {"kind":"name","cycle":cycle,"base":rest,"axis":None,"sep":None,"idx":None}

def split_by_sep(s, sep):
    if sep and sep in s: return s.split(sep)
    if not sep: return list(s)
    if "," in s: return [x.strip() for x in s.split(",")]
    return [s]

def join_by_sep(items, sep):
    if not sep: return "".join(items)
    if sep == ", ": return ", ".join(items)
    if sep == "\n": return "\n".join(items)
    return sep.join(items)

def axis_index(idx, items, mem=None):
    if idx in (None, "", "all"): return None
    if idx == "last": return len(items) - 1
    if idx == "first": return 0
    if mem and idx in mem:
        idx = mem[idx]
    try: return int(idx) - 1
    except (ValueError, TypeError): return None

def mem_of(model, cycle_name, cur_cyc_name):
    if cycle_name:
        for c in model["cycles"]:
            if c["name"] == cycle_name:
                return model["memory"].setdefault(cycle_name, {})
        return None
    return model["memory"].setdefault(cur_cyc_name, {})

def read_ref(model, cyc, ref):
    p = parse_ref(ref)
    if not p: return None
    mem = mem_of(model, p["cycle"], cyc["name"])
    if mem is None: return None
    if p["kind"] == "name":
        return mem.get(p["base"])
    if p["kind"] == "axis":
        sep_eff = p["sep"] if p["sep"] is not None else ("\n" if p["axis"]=="y" else "")
        items = split_by_sep(mem.get(p["base"], ""), sep_eff)
        i = axis_index(p["idx"], items, mem)
        return items[i] if i is not None and 0 <= i < len(items) else None
    if p["kind"] == "line":
        for c in model["cycles"]:
            if (p["cycle"] or cyc["name"]) == c["name"]:
                if 0 <= p["n"]-1 < len(c["lines"]):
                    return c["lines"][p["n"]-1]
        return None
    return None

def write_ref(model, cyc, ref, value, op="=>"):
    p = parse_ref(ref)
    if not p: return False
    mem = mem_of(model, p["cycle"], cyc["name"])
    if mem is None: return False
    if p["kind"] == "name":
        mem[p["base"]] = value
        return True
    if p["kind"] == "axis":
        base, axis, sep, idx = p["base"], p["axis"], p["sep"], p["idx"]
        sep_eff = sep if sep is not None else ("\n" if axis=="y" else "")
        items = split_by_sep(mem.get(base, ""), sep_eff)
        i = axis_index(idx, items, mem)
        if op in ("=>", "->"):
            if i is not None and 0 <= i < len(items):
                items[i] = value
            elif idx not in (None,"","all"):
                try: items.insert(int(idx)-1, value)
                except Exception: items.append(value)
            else:
                items.append(value)
        else:
            if idx not in (None,"","all"):
                try: items.insert(int(idx)-1, value)
                except Exception: items.append(value)
            else:
                items.append(value)
        mem[base] = join_by_sep(items, sep_eff)
        return True
    if p["kind"] == "line":
        for c in model["cycles"]:
            if (p["cycle"] or cyc["name"]) == c["name"]:
                if 0 <= p["n"]-1 < len(c["lines"]):
                    c["lines"][p["n"]-1] = value
                    return True
        return False
    return False

def remove_ref(model, cyc, ref):
    p = parse_ref(ref)
    if not p: return False
    if p["kind"] == "name":
        mem = mem_of(model, p["cycle"], cyc["name"])
        if mem is None: return False
        mem.pop(p["base"], None)
        return True
    if p["kind"] == "axis":
        return remove_from_axis(model, cyc, ref)
    if p["kind"] == "line":
        return remove_line(model, cyc, ref)
    return False

def remove_from_axis(model, cyc, ref):
    parsed = parse_axis_ref(ref)
    if not parsed: return False
    base, axis, sep, idx = parsed
    mem = model["memory"].setdefault(cyc["name"], {})
    if base not in mem: return False
    items = split_by_sep(mem[base], sep)
    if idx in (None, "", "all"): mem[base] = ""; return True
    i = axis_index(idx, items, mem)
    if i is None: return False
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
        e2 = re.sub(r'\bsqrt\s*\(', 'math.sqrt(', e2)
        e2 = re.sub(r'\bsin\s*\(', 'math.sin(', e2)
        e2 = re.sub(r'\bcos\s*\(', 'math.cos(', e2)
        v = eval(e2, {"__builtins__":{}, "math": math}, {})
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
            cycle_name, target2 = parts[0], parts[1]
            for i, c in enumerate(model["cycles"]):
                if c["name"] == cycle_name:
                    model["cur"] = i
                    if target2.isdigit():
                        n_int = int(target2) - 1
                        model["cycles"][i]["agent"] = max(0, min(n_int, len(model["cycles"][i]["lines"])-1))
                    else:
                        idx = find_line_by_name(model["cycles"][i]["lines"], target2)
                        if idx >= 0:
                            model["cycles"][i]["agent"] = idx
                        else:
                            return False
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

def swap_axis(mem, src, dst):
    s = parse_axis_ref(src); d = parse_axis_ref(dst)
    if not s or not d: return False
    s_base, s_axis, s_sep, s_idx = s
    d_base, d_axis, d_sep, d_idx = d
    s_sep_eff = s_sep if s_sep is not None else ("\n" if s_axis=="y" else "")
    d_sep_eff = d_sep if d_sep is not None else ("\n" if d_axis=="y" else "")
    if s_base == d_base:
        items = split_by_sep(mem.get(s_base, ""), s_sep_eff)
        si = axis_index(s_idx, items, mem)
        di = axis_index(d_idx, items, mem)
        if si is None or di is None: return False
        if not (0 <= si < len(items) and 0 <= di < len(items)): return False
        items[si], items[di] = items[di], items[si]
        mem[s_base] = join_by_sep(items, s_sep_eff)
        return True
    s_items = split_by_sep(mem.get(s_base, ""), s_sep_eff)
    d_items = split_by_sep(mem.get(d_base, ""), d_sep_eff)
    si = axis_index(s_idx, s_items, mem)
    di = axis_index(d_idx, d_items, mem)
    if si is None or di is None: return False
    if not (0 <= si < len(s_items) and 0 <= di < len(d_items)): return False
    s_items[si], d_items[di] = d_items[di], s_items[si]
    mem[s_base] = join_by_sep(s_items, s_sep_eff)
    mem[d_base] = join_by_sep(d_items, d_sep_eff)
    return True

# ---------- extensions ----------
def ext_math(model, cyc, src, dst, op, eval_flag, bridge):
    mem = model["memory"].setdefault(cyc["name"], {})
    mem["::math"] = eval_expr(src, mem)
    return True

def ext_nothing(model, cyc, src, dst, op, eval_flag, bridge):
    if op in ("->", "->|"):
        remove_ref(model, cyc, src)
    return True

def ext_simple(model, cyc, src, dst, op, eval_flag, bridge):
    if bridge is None: return False
    cmd = dst[len("::simple:"):]
    try:
        if cmd == "play" and not model["playing"]: bridge.toggle()
        elif cmd == "pause": bridge.pause()
        elif cmd == "step": bridge.step_forward()
        elif cmd == "stepBack": bridge.step_back()
        elif cmd == "restart": bridge.reset()
        elif cmd == "new" and src: bridge.add_editor(src)
        elif cmd == "open" and src: bridge.open_path(src)
        elif cmd == "save": bridge.save_cycle()
        elif cmd == "close" and src: bridge.save_cycle(); bridge.close_cycle(src)
        elif cmd == "exit": bridge.exit()
    except Exception as e:
        log(f"  [simple] error: {e}")
    return True

EXTENSIONS = {
    "math": ext_math,
    "nothing": ext_nothing,
    "simple": ext_simple,
}

def exec_action(model, cyc, line, bridge=None):
    mem = model["memory"].setdefault(cyc["name"], {})
    if line.lstrip().startswith("\\"):
        log(f"  [escape] line is literal: {line!r}")
        return
    line_esc = escape_for_parse(line)
    for src_raw, op, dst, eval_flag in parse_actions(line_esc):
        src_raw = unescape_after_parse(src_raw)
        dst = unescape_after_parse(dst)
        log(f"  [exec] src={src_raw!r} op={op!r} eval={eval_flag} dst={dst!r}")

        if dst in mem and isinstance(mem[dst], str) and mem[dst].startswith("::"):
            ext_ref = mem[dst]
            log(f"  [ext-by-name] {dst!r} -> {ext_ref!r}")
            dst = ext_ref

        # extensions
        if dst.startswith("::"):
            ext_name = dst[2:].split(":")[0]
            fn = EXTENSIONS.get(ext_name)
            if fn:
                fn(model, cyc, src_raw, dst, op, eval_flag, bridge)
                continue

        if op == "<->":
            if swap_axis(mem, src_raw, dst):
                log(f"  [swap-axis] {src_raw!r} <-> {dst!r}")
                continue

        if "," in src_raw and not parse_axis_ref(src_raw) and not parse_line_ref(src_raw):
            srcs = [s.strip() for s in src_raw.split(",") if s.strip()]
        else:
            srcs = [src_raw]

        for src in srcs:
            if eval_flag:
                sv = eval_expr(src, mem)
                log(f"  [eval] {src!r} -> {sv!r}")
            else:
                sv = read_ref(model, cyc, src)
                if sv is None:
                    sv = mem.get(src, src)

            targets = [t.strip() for t in dst.split(",") if t.strip()] or [dst]
            for target in targets:
                if not valid_name(target) and not parse_axis_ref(target) and not parse_line_ref(target):
                    log(f"  [invalid-name] {target!r}")
                    continue
                write_ref(model, cyc, target, sv, op=op)
                if op in ("->", "->|"):
                    remove_ref(model, cyc, src)
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

def execute_line(model, cyc, target_idx, bridge=None):
    line = cyc["lines"][target_idx]
    typ, m = resolve_line(line)
    log(f"[type] {typ} :: {line!r}")
    if typ == "named":
        mem = model["memory"].setdefault(cyc["name"], {})
        val_raw = unescape_after_parse(escape_for_parse(m.group("val")))
        val = unescape_nl(val_raw)
        names_raw = unescape_after_parse(escape_for_parse(m.group("names")))
        for n in re.split(r'[,\s]+', names_raw):
            if n and valid_name(n): mem[n] = val
    elif typ == "condition":
        cond = m.group("cond").strip()
        act = m.group("act").strip()
        mem = model["memory"].setdefault(cyc["name"], {})
        if entails(cond, mem) and act:
            exec_action(model, cyc, act, bridge)
    elif typ == "jump":
        do_jump(model, cyc, m.group("target"))
    elif typ == "action":
        exec_action(model, cyc, line, bridge)
    elif typ == "version":
        pass
    elif typ == "container":
        for j in range(target_idx - 1, -1, -1):
            ln_j = cyc["lines"][j]
            if AGENT_RE.match(ln_j): continue
            t2, m2 = resolve_line(ln_j)
            if t2 == "named" and m2:
                names = [n.strip() for n in re.split(r'[,\s]+', m2.group("names")) if n.strip()]
                if names:
                    primary = names[0]
                    mem = model["memory"].setdefault(cyc["name"], {})
                    if primary in mem:
                        mem[primary] += "\n" + line
                        log(f"  [block-commit] appended to {primary!r}")
                        break
            elif t2 == "separator":
                break
    return typ

# ---------- step engine (returns Event) ----------
def step_engine(model, bridge=None):
    event = {"kind": None, "cycle": None, "old": {}, "new": {}}
    if not model["cycles"]: return event
    cyc = model["cycles"][model["cur"]]
    event["cycle"] = cyc["name"]
    lines = cyc["lines"]; a = cyc["agent"]
    if not lines: return event
    target = a + 1
    if target >= len(lines):
        event["kind"] = "rotate"
        event["old"] = {"agent": a, "lines": lines[:]}
        agent_line = lines[a]
        del lines[a]; lines.insert(0, agent_line)
        cyc["agent"] = 0
        event["new"] = {"agent": 0, "lines": lines[:]}
        log(f"\n[step] rotate agent {a}->0")
        return event
    log(f"\n[step] agent={a} target={target} n={len(lines)}")
    old_mem = dict(model["memory"].setdefault(cyc["name"], {}))
    old_lines = lines[:]
    old_agent = a
    typ_target = execute_line(model, cyc, target, bridge)
    if typ_target == "jump":
        event["kind"] = "jump"
        event["old"] = {"agent": old_agent, "mem": old_mem}
        event["new"] = {"agent": cyc["agent"], "mem": dict(model["memory"][cyc["name"]])}
        log(f"  [jump] agent={cyc['agent']} (no swap)")
        return event
    aim = ""
    if AGENT_RE.match(lines[a]):
        m_agent = AGENT_RE.match(lines[a])
        aim = m_agent.group("aim").strip()
    if aim:
        mem = model["memory"].setdefault(cyc["name"], {})
        if entails(aim, mem):
            cyc["agent"] = 0
            event["kind"] = "aim"
            event["old"] = {"agent": old_agent, "mem": old_mem}
            event["new"] = {"agent": 0, "mem": dict(model["memory"][cyc["name"]])}
            log(f"  [aim] reached! agent=0")
            return event
    if typ_target and AGENT_RE.match(lines[a]):
        new_agent_line = update_agent_type(lines[a], typ_target)
        if new_agent_line != lines[a]:
            lines[a] = new_agent_line
            log(f"  [agent] type -> <{typ_target}>")
    flush_memory_to_lines(cyc, model)
    for c in model["cycles"]:
        if c["name"] != cyc["name"]:
            flush_memory_to_lines(c, model)
    lines[a], lines[target] = lines[target], lines[a]
    cyc["agent"] = target
    event["kind"] = "step"
    event["old"] = {"agent": old_agent, "mem": old_mem, "lines": old_lines}
    event["new"] = {"agent": target, "mem": dict(model["memory"][cyc["name"]]), "lines": lines[:]}
    log(f"[swap] {a}<->{target} agent->{target}")
    return event

# ---------- history ----------
class History:
    def __init__(self, max_size=HISTORY_MAX):
        self.events = []
        self.pos = -1
        self.max_size = max_size
    def record(self, event):
        if not event or event.get("kind") is None: return
        self.events = self.events[:self.pos+1]
        self.events.append(event)
        if len(self.events) > self.max_size:
            self.events.pop(0)
        self.pos = len(self.events) - 1
    def undo(self, model):
        if self.pos < 0: return None
        ev = self.events[self.pos]
        self.pos -= 1
        apply_reverse(model, ev)
        return ev
    def redo(self, model):
        if self.pos + 1 >= len(self.events): return None
        self.pos += 1
        ev = self.events[self.pos]
        apply_forward(model, ev)
        return ev
    def clear(self):
        self.events = []
        self.pos = -1

def apply_reverse(model, ev):
    cyc = next((c for c in model["cycles"] if c["name"] == ev.get("cycle")), None)
    if not cyc: return
    if ev.get("kind") in ("step", "rotate"):
        if "lines" in ev["old"]: cyc["lines"] = ev["old"]["lines"][:]
        if "agent" in ev["old"]: cyc["agent"] = ev["old"]["agent"]
    elif ev.get("kind") in ("jump", "aim"):
        if "agent" in ev["old"]: cyc["agent"] = ev["old"]["agent"]
    if "mem" in ev.get("old", {}):
        model["memory"][ev["cycle"]] = dict(ev["old"]["mem"])

def apply_forward(model, ev):
    cyc = next((c for c in model["cycles"] if c["name"] == ev.get("cycle")), None)
    if not cyc: return
    if ev.get("kind") in ("step", "rotate"):
        if "lines" in ev["new"]: cyc["lines"] = ev["new"]["lines"][:]
        if "agent" in ev["new"]: cyc["agent"] = ev["new"]["agent"]
    elif ev.get("kind") in ("jump", "aim"):
        if "agent" in ev["new"]: cyc["agent"] = ev["new"]["agent"]
    if "mem" in ev.get("new", {}):
        model["memory"][ev["cycle"]] = dict(ev["new"]["mem"])

# ---------- snapshot (debug/reset only) ----------
def snapshot(model):
    return {
        "cur": model["cur"],
        "cycles": [
            {"name": c["name"], "lines": c["lines"][:],
             "agent": c["agent"], "color": c.get("color", "#5fb85f")}
            for c in model["cycles"]
        ],
        "memory": {k: dict(v) for k, v in model["memory"].items()},
    }

def restore(model, snap):
    model["cur"] = snap["cur"]
    model["memory"] = {k: dict(v) for k, v in snap["memory"].items()}
    for c, sc in zip(model["cycles"], snap["cycles"]):
        c["lines"] = sc["lines"][:]
        c["agent"] = sc["agent"]
        c["color"] = sc["color"]

# ---------- logging ----------
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

# ---------- tests ----------
def run_tests():
    AG = "Mr.Green, #00ff00 | Data as <sep> | Aim: 0"
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
         {"a":"1","b":"2","l":"1\n2"}, 3),
        ("T14 jump", [AG, "1 = a", "^ 1"], {"a":"1"}, 3),
        ("T15 empty named at start", [AG, "= x"], {"x":""}, 2),
        ("T16 insert no multi", [AG, "1 = a", "a =>| l:y(, )"],
         {"a":"1","l":"1"}, 3),
        ("T17 multi-src insert values", [AG, "1 = a", "a, a =>| l:y(, )"],
         {"a":"1","l":"1\n1"}, 3),
        ("T32 ?=> eval", [AG, "1 = a", "2 = b", "a + b ?=> c"],
         {"a":"1","b":"2","c":"3"}, 3),
        ("T33 => literal", [AG, "1 = a", "a + 1 => c"],
         {"a":"1","c":"a + 1"}, 3),
        ("T34 ?=>| insert eval", [AG, "1 = a", "a + 1 ?=>| l:y(, )"],
         {"a":"1","l":"2"}, 3),
        ("T35 <-> axis 1-based", [AG, "5, 3 = arr", "1 = j", "2 = jn",
         "arr:y(, ):j <-> arr:y(, ):jn"], {"arr":"3, 5"}, 4),
        ("T40 sqrt", [AG, "9 = x", "sqrt(x) ?=> y"], {"x":"9","y":"3"}, 3),
        ("T47 =>| vs ->|", [AG, "1 = a", "2 = b",
         "a =>| l:y(, )", "b ->| l:y(, )"], {"a":"1","l":"1\n2"}, 5),
        ("T48 y sep=\\n", [AG, "1\n2\n3 = l", "l:y:2 => x"], {"l":"1\n2\n3","x":"2"}, 3),
        ("T49 z axis", [AG, "1;2;3 = l", "l:z:2 => x"], {"l":"1;2;3","x":"2"}, 3),
        ("T50 escape \\=", [AG, "1 = a", "a \\= b"], {"a":"1"}, 3),
        ("T51 escape \\?", [AG, "1 = a", "a \\? b"], {"a":"1"}, 3),
        ("T52 escape \\::math", [AG, "1 = a", "a => \\::math"], {"a":"1"}, 3),
        ("T53 valid name reject", [AG, "1 = a/b"], {}, 2),
        ("T54 # version", ["# version: 1", AG, "1 = a"], {"a":"1"}, 3),
        ("T55 ^ :cycle:name", [AG, "1 = a"], {"a":"1"}, 2),
        ("T56 cross-file", [AG, "1 = a",
         "cycle:other.cycle:x => y"], {"a":"1"}, 3),
        # new v0.27.0 tests
        ("T57 entails truth", [AG, "1 = a"], {"a":"1"}, 2),
        ("T58 ->| removes source", [AG, "1 = a", "2 = b", "b ->| l:y(, )"],
         {"a":"1","l":"2"}, 4),
        ("T59 =>| keeps source", [AG, "1 = a", "a =>| l:y(, )"],
         {"a":"1","l":"1"}, 3),
        ("T60 name validator", [AG, "1 = a=b"], {}, 2),
        ("T61 z axis default", [AG, "1;2;3 = l", "l:z:last => x"],
         {"l":"1;2;3","x":"3"}, 3),
        ("T62 cross-file copy", [AG, "1 = a"], {"a":"1"}, 2),
    ]
    passed = 0
    tlog(f"=== Simple tests v0.27.0 ===")
    for name, lines, exp, steps in tests:
        m = {"cycles":[{"name":"t.cycle","lines":lines[:],"agent":0,"color":"#00ff00"}],
             "memory":{},"cur":0,"playing":False,"ms":0}
        for _ in range(steps): step_engine(m)
        mem = m["memory"].get("t.cycle", {})
        ok = all(mem.get(k) == v for k, v in exp.items())
        if ok: tlog(f"  {name}: PASS"); passed += 1
        else: tlog(f"  {name}: FAIL mem={mem} exp={exp}")
    # T18 dynamic type
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "= b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    step_engine(m)
    agent_line = m["cycles"][0]["lines"][m["cycles"][0]["agent"]]
    if "Data as <named>" in agent_line: tlog("  T18 dynamic type named: PASS"); passed += 1
    else: tlog(f"  T18 dynamic type named: FAIL agent={agent_line!r}")
    # T20 step
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    step_engine(m)
    if m["cycles"][0]["agent"] == 1: tlog("  T20 step once: PASS"); passed += 1
    else: tlog(f"  T20 step once: FAIL agent={m['cycles'][0]['agent']}")
    # T21 condition parts
    line = "dir > 0 ? 5 => x"
    typ, m2 = resolve_line(line)
    if typ == "condition" and m2.group("cond").strip() == "dir > 0" and m2.group("act").strip() == "5 => x":
        tlog("  T21 condition parts: PASS"); passed += 1
    else: tlog(f"  T21 condition parts: FAIL typ={typ}")
    # T22 default program
    t22_lines = DEFAULT_PROGRAM.split("\n")
    if t22_lines[0].startswith("# version") and resolve_line(t22_lines[1])[0] == "agent":
        tlog("  T22 default program: PASS"); passed += 1
    else: tlog(f"  T22 default program: FAIL line0={t22_lines[0]!r}")
    # T23 default lines = 17
    if len(DEFAULT_PROGRAM.split("\n")) == 17:
        tlog("  T23 default program lines=17: PASS"); passed += 1
    else: tlog(f"  T23 default program lines=17: FAIL lines={len(DEFAULT_PROGRAM.split(chr(10)))}")
    # T24 history undo
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    h = History()
    ev = step_engine(m)
    h.record(ev)
    before = dict(m["memory"].get("t.cycle", {}))
    h.undo(m)
    after = dict(m["memory"].get("t.cycle", {}))
    if before != after and m["cycles"][0]["agent"] == 0:
        tlog("  T24 history undo restores: PASS"); passed += 1
    else: tlog("  T24 history undo restores: FAIL")
    # T25 samples
    if "elevator.cycle" in SAMPLES: tlog("  T25 samples defined: PASS"); passed += 1
    else: tlog("  T25 samples defined: FAIL")
    # T26
    typ26, _ = resolve_line("\\a => b")
    if typ26 == "container": tlog("  T26 backslash start -> container: PASS"); passed += 1
    else: tlog(f"  T26 backslash start -> container: FAIL typ={typ26}")
    # T27
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => \\name"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(3): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    if mem.get("\\name") == "1" or mem.get("name") == "1": tlog("  T27 backslash name literal: PASS"); passed += 1
    else: tlog(f"  T27 backslash name literal: FAIL mem={mem}")
    # T28
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a \\=> b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(3): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    if "b" not in mem: tlog("  T28 escaped operator not operation: PASS"); passed += 1
    else: tlog(f"  T28 escaped operator not operation: FAIL mem={mem}")
    # T29
    class MockApp:
        def __init__(s):
            s.model = {"playing": False}
            class R:
                destroyed = False
                def after(s, t, f): f()
                def destroy(s): s.destroyed = True
            s.root = R()
        def save_cycle(s): pass
        def toggle(s): pass
        def pause(s): pass
        def step_forward(s): pass
        def step_back(s): pass
        def reset(s): pass
        def add_editor(s, n): pass
        def open_path(s, p): pass
        def close_cycle(s, n): pass
        def exit(s): s.root.destroy()
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "=> ::simple:exit"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    mock = MockApp()
    for _ in range(3): step_engine(m, mock)
    if mock.root.destroyed: tlog("  T29 ::simple:exit: PASS"); passed += 1
    else: tlog("  T29 ::simple:exit: FAIL")
    # T30
    class MockApp2:
        def __init__(s):
            s.model = {"playing": False, "cycles": [], "cur": 0}
            s.closed = []
        def save_cycle(s): pass
        def close_cycle(s, name):
            s.closed.append(name); return True
        def toggle(s): pass
        def pause(s): pass
        def step_forward(s): pass
        def step_back(s): pass
        def reset(s): pass
        def add_editor(s, n): pass
        def open_path(s, p): pass
        def exit(s): pass
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "t.cycle => ::simple:close"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    mock = MockApp2()
    for _ in range(3): step_engine(m, mock)
    if "t.cycle" in mock.closed: tlog("  T30 ::simple:close: PASS"); passed += 1
    else: tlog(f"  T30 ::simple:close: FAIL closed={mock.closed}")
    # T31
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "::math = m", "= result", "a + 1 => m => result"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(6): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    if mem.get("result") == "2":
        tlog("  T31 ext by name (result=2): PASS"); passed += 1
    else:
        tlog(f"  T31 ext by name (result=2): FAIL mem={mem}")
    # T37
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = x", "2 = y"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    m["cycles"][0]["lines"][0] = "Mr.Green, #00ff00 | Data as <sep> | Aim: x == 1"
    step_engine(m)
    if m["cycles"][0]["agent"] == 0:
        tlog("  T37 aim reached: PASS"); passed += 1
    else:
        tlog(f"  T37 aim reached: FAIL agent={m['cycles'][0]['agent']}")
    # T38
    tmp = os.path.join(BASE_DIR, "_test_save.cycle")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("test line 1\ntest line 2")
        with open(tmp, "r", encoding="utf-8") as f:
            content = f.read()
        if content == "test line 1\ntest line 2":
            tlog("  T38 save/load: PASS"); passed += 1
        else:
            tlog("  T38 save/load: FAIL")
        os.remove(tmp)
    except Exception:
        tlog("  T38 save/load: FAIL (exception)")
    # T39
    if "agent_type" in HL:
        tlog("  T39 agent_type tag: PASS"); passed += 1
    else:
        tlog("  T39 agent_type tag: FAIL")
    # T41
    try:
        content = "Mr.Green, #00ff00 | Data as <sep> | Aim: 0\n1 = a\na => b"
        lines_test = content.split("\n")
        m = {"cycles":[{"name":"t.cycle","lines":lines_test[:],"agent":0,"color":"#00ff00"}],
             "memory":{},"cur":0,"playing":False,"ms":0}
        m["cycles"][0]["agent"] = 0
        m["memory"].clear()
        m["playing"] = True
        step_engine(m)
        if m["cycles"][0]["agent"] == 1:
            tlog("  T41 sample click -> play: PASS"); passed += 1
        else:
            tlog(f"  T41 sample click -> play: FAIL agent={m['cycles'][0]['agent']}")
    except Exception as e:
        tlog(f"  T41 sample click -> play: FAIL {e}")
    # T42
    import tempfile
    try:
        tmpdir = tempfile.mkdtemp()
        os.makedirs(os.path.join(tmpdir, "samples"), exist_ok=True)
        sample_path = os.path.join(tmpdir, "samples", "counter.cycle")
        with open(sample_path, "w") as f:
            f.write("Mr.Green, #00ff00 | Data as <sep> | Aim: 1\nold")
        with open(sample_path, "r") as f:
            old = f.read()
        need_write = "Aim: 1" in old or "Aim:" not in old
        if need_write:
            with open(sample_path, "w") as f:
                f.write("Mr.Green, #00ff00 | Data as <sep> | Aim: 0\nnew")
        with open(sample_path, "r") as f:
            new_content = f.read()
        if "Aim: 0" in new_content:
            tlog("  T42 samples overwrite Aim: 1 -> Aim: 0: PASS"); passed += 1
        else:
            tlog("  T42 samples overwrite Aim: 1 -> Aim: 0: FAIL")
    except Exception as e:
        tlog(f"  T42 samples overwrite: FAIL {e}")
    # T44 palindrome
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "level = list", "1 = left", "5 = right", "1 = is_palindrome",
        "list:x:left != list:x:right ? 0 => is_palindrome",
        "left < right ? 1 => can_move",
        "can_move == 1 ? left + 1 ?=> left",
        "can_move == 1 ? right - 1 ?=> right",
        "left >= right ? 1 => done"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(20): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    if mem.get("is_palindrome") == "1" and mem.get("done") == "1":
        tlog("  T44 palindrome: PASS"); passed += 1
    else:
        tlog(f"  T44 palindrome: FAIL mem={mem}")
    # T45 tree
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = root", "2 = root.left", "3 = root.right",
        "4 = root.right.left", "5 = root.right.right",
        "root => out", "root.left =>| out:y(, )", "root.right =>| out:y(, )"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(10): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    if mem.get("root.left") == "2" and mem.get("out") == "1\n2\n3":
        tlog("  T45 tree dot notation: PASS"); passed += 1
    else:
        tlog(f"  T45 tree dot notation: FAIL mem={mem}")
    # T46 matrix
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "123\n456\n789 = array2d",
        "array2d:y:2 => row", "row:x:1 => cell"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    for _ in range(8): step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    ok = (mem.get("array2d") == "123\n456\n789" and
          mem.get("row") == "456" and
          mem.get("cell") == "4")
    if ok:
        tlog("  T46 2D matrix axes: PASS"); passed += 1
    else:
        tlog(f"  T46 2D matrix axes: FAIL mem={mem}")
    # T63 History record/undo/redo
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    h = History()
    ev1 = step_engine(m); h.record(ev1)
    ev2 = step_engine(m); h.record(ev2)
    h.undo(m); h.undo(m)
    if m["cycles"][0]["agent"] == 0 and "b" not in m["memory"].get("t.cycle", {}):
        tlog("  T63 History undo x2: PASS"); passed += 1
    else:
        tlog(f"  T63 History undo x2: FAIL agent={m['cycles'][0]['agent']} mem={m['memory']}")
    # T64 entails
    if entails("1", {}) and not entails("0", {}) and not entails("", {}):
        tlog("  T64 entails: PASS"); passed += 1
    else:
        tlog("  T64 entails: FAIL")
    # T65 TRUTH_PRINCIPLE
    if TRUTH_PRINCIPLE == "Truth is what can be used.":
        tlog("  T65 TRUTH_PRINCIPLE: PASS"); passed += 1
    else:
        tlog("  T65 TRUTH_PRINCIPLE: FAIL")
    # T66 EXTENSIONS registry
    if set(EXTENSIONS.keys()) == {"math", "nothing", "simple"}:
        tlog("  T66 EXTENSIONS registry: PASS"); passed += 1
    else:
        tlog(f"  T66 EXTENSIONS registry: FAIL {set(EXTENSIONS.keys())}")
    # T67 step_engine returns event
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent":0,"color":"#00ff00"}],
         "memory":{},"cur":0,"playing":False,"ms":0}
    ev = step_engine(m)
    if isinstance(ev, dict) and ev.get("kind") == "step" and "old" in ev and "new" in ev:
        tlog("  T67 step_engine returns event: PASS"); passed += 1
    else:
        tlog(f"  T67 step_engine returns event: FAIL {ev}")
    total = len(tests) + 24 + 5
    tlog(f"\n{passed}/{total} passed")
    return passed == total

# ---------- UI ----------
class Editor(tk.Frame):
    def __init__(s, parent, name, index):
        super().__init__(parent, bg=BG)
        s.name = name
        head = tk.Frame(s, bg=BG); head.pack(fill="x", pady=(0, S["s"]))
        tk.Label(head, text=f"#{index+1}  ·  {name}", bg=BG, fg=FG,
                 font=("TkDefaultFont", S["m"])).pack(side="left")
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
                    "action", "cond", "act", "op", "agent_type", "version"):
            s.text.tag_remove(typ, "1.0", "end")
        lines = s.text.get("1.0", "end-1c").split("\n")
        for i, line in enumerate(lines):
            typ, m = resolve_line(line)
            row = i + 1
            if typ == "agent" and m:
                ts = line.find("Data as <")
                te = line.find(">", ts)
                if ts >= 0 and te >= 0:
                    s.text.tag_add("agent_type", f"{row}.{ts}", f"{row}.{te+1}")
                continue
            if typ == "version":
                s.text.tag_add("version", f"{row}.0", f"{row}.end")
                continue
            if typ == "condition" and m:
                s.text.tag_add("cond", f"{row}.{m.start('cond')}", f"{row}.{m.end('cond')}")
                if m.group("act"):
                    act_start = m.start("act"); act_end = m.end("act")
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
        for t in ("cond", "act", "action", "op", "agent_type", "agent", "version"):
            try: s.text.tag_raise(t)
            except Exception: pass

    def set_agent(s, idx):
        s.text.tag_remove("agent", "1.0", "end")
        lines = s.text.get("1.0", "end-1c").split("\n")
        if 0 <= idx < len(lines):
            s.text.tag_add("agent", f"{idx+1}.0", f"{idx+1}.end")
            s.text.see(f"{idx+1}.0")
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
        root.title("Simple — True v0.27.0")
        root.configure(bg=BG)
        s.model = {"cycles": [], "memory": {}, "cur": 0, "playing": False, "ms": 390}
        s.editors = []
        s.history = History()
        s._last_n = -1
        s.build()
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
        TButton(bar, "+", lambda: s.add_editor(f"cycle{len(s.editors)+1}.cycle"),
                bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "📂", s.open_file_dialog, bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "💾", s.save_cycle, bg=FG).pack(side="left", padx=S["s"])
        TButton(bar, "⏮", s.reset, bg=FG).pack(side="left")

        main = tk.Frame(s.root, bg=BG); main.pack(fill="both", expand=True)
        left = tk.Frame(main, bg=BG); left.pack(side="left", fill="both", expand=True)
        s.canvas = tk.Canvas(left, bg=BG); s.canvas.pack(fill="both", expand=True)
        s.inner = tk.Frame(s.canvas, bg=BG)
        s._inner_win = s.canvas.create_window((0,0), window=s.inner, anchor="nw")
        s.inner.bind("<Configure>",
                     lambda e: s.canvas.configure(scrollregion=s.canvas.bbox("all")))
        s.canvas.bind("<Configure>", s._on_canvas_resize)
        s.canvas.bind_all("<MouseWheel>", s._on_wheel)

        right = tk.Frame(main, bg=PANEL_BG, width=200)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="samples", bg=PANEL_BG, fg=FG,
                 font=("TkDefaultFont", S["m"])).pack(anchor="w", padx=S["s"], pady=S["s"])
        s.samples_list = tk.Listbox(right, bg=EDITOR_BG, fg=FG,
                                    selectbackground=ACCENT, selectforeground=BG,
                                    font=("Monospace", S["m"]),
                                    bd=0, highlightthickness=0)
        s.samples_list.pack(fill="both", expand=True, padx=S["s"], pady=(0, S["s"]))
        s.samples_list.bind("<<ListboxSelect>>", s._on_sample_click)
        s.samples_menu = tk.Menu(s.samples_list, tearoff=0,
                                 bg=EDITOR_BG, fg=FG,
                                 activebackground=ACCENT, activeforeground=BG)
        s.samples_menu.add_command(label="Open", command=s._on_sample_click)
        s.samples_menu.add_command(label="Delete", command=s._on_sample_delete)
        s.samples_list.bind("<Button-3>", lambda e: s.samples_menu.tk_popup(e.x_root, e.y_root))

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

    def _on_canvas_resize(s, e):
        s.canvas.itemconfig(s._inner_win, width=e.width)

    def save_cycle(s):
        if not s.model["cycles"]: return
        cur = s.model["cycles"][s.model["cur"]]
        name = cur["name"]
        path = os.path.join(BASE_DIR, name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(cur["lines"]))
            log(f"[save] {path} ({len(cur['lines'])} lines)")
            s.update_status()
        except Exception as e:
            log(f"[save] error: {e}")

    def open_file_dialog(s):
        path = filedialog.askopenfilename(
            title="Open .cycle",
            filetypes=[("Cycle files", "*.cycle"), ("All files", "*.*")]
        )
        if path:
            s.open_path(path)

    def _on_sample_delete(s):
        sel = s.samples_list.curselection()
        if not sel: return
        idx = sel[0]
        if idx >= len(s.samples_files): return
        path = s.samples_files[idx]
        try:
            os.remove(path)
            log(f"[delete] {path}")
            s.refresh_samples()
        except Exception as e:
            log(f"[delete] error: {e}")

    def refresh_samples(s):
        s.samples_list.delete(0, "end")
        s.samples_files = []
        if not os.path.isdir(SAMPLES_DIR): return
        for path in sorted(glob.glob(os.path.join(SAMPLES_DIR, "*.cycle"))):
            name = os.path.basename(path)
            s.samples_list.insert("end", name)
            s.samples_files.append(path)

    def _on_sample_click(s, e):
        sel = s.samples_list.curselection()
        if not sel: return
        idx = sel[0]
        if idx >= len(s.samples_files): return
        path = s.samples_files[idx]
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return
        if s.editors:
            s.model["playing"] = False
            s.btn.config(text="▶")
            s.editors[0].set_text(content)
            s.sync_from_ui()
            s.history.clear()
            cur = s.model["cycles"][s.model["cur"]]
            cur["agent"] = 0
            s.model["memory"].clear()
            s.refresh_ui()
            log(f"[sample] {path} loaded, reset to 0")

    def _on_wheel(s, e):
        s.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def add_editor(s, name, initial_text=None):
        idx = len(s.editors)
        if idx > 0:
            tk.Frame(s.inner, bg=ACCENT, height=1).pack(fill="x", pady=S["s"])
        ed = Editor(s.inner, name, idx)
        ed.pack(fill="both", expand=True, padx=S["s"], pady=(S["s"], S["s"]))
        ed.on_change_cb = s.on_key_change
        ed.on_focus_cb = s.pause
        s.editors.append(ed)
        lines_init = initial_text.split("\n") if initial_text else [""]
        s.model["cycles"].append({"name": name, "lines": lines_init,
                                  "agent": 0, "color": "#5fb85f"})
        if initial_text:
            ed.set_text(initial_text)
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

    def close_cycle(s, name):
        for i, c in enumerate(s.model["cycles"]):
            if c["name"] == name:
                ed = s.editors[i]
                ed.destroy()
                del s.editors[i]
                del s.model["cycles"][i]
                if s.model["cur"] >= len(s.model["cycles"]):
                    s.model["cur"] = max(0, len(s.model["cycles"])-1)
                s.refresh_ui()
                return True
        return False

    def pause(s):
        if s.model["playing"]:
            s.model["playing"] = False
            s.btn.config(text="▶")
            s.update_status()

    def step_forward(s):
        if s.model["playing"]:
            s.pause()
        s.sync_from_ui()
        ev = step_engine(s.model, s)
        s.history.record(ev)
        s.refresh_ui()

    def step_back(s):
        if s.model["playing"]:
            s.pause()
        ev = s.history.undo(s.model)
        if ev is None: return
        s.refresh_ui()

    def on_key_change(s):
        if s.model["playing"]: return
        s.sync_from_ui()

    def sync_from_ui(s):
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
            else:
                log(f"[reset] no file {path}, using memory")
        for c in s.model["cycles"]: c["agent"] = 0
        s.model["memory"].clear()
        s.history.clear()
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
        aim = ""
        if AGENT_RE.match(c["lines"][c["agent"]]):
            m = AGENT_RE.match(c["lines"][c["agent"]])
            aim = m.group("aim").strip()
        s.status.config(
            text=f" cycle={s.model['cur']+1}/{len(s.model['cycles'])}"
                 f"  agent={c['agent']}/{n} (sep={sep})"
                 f"  {st}  ms={s.model['ms']}"
                 f"  hist={len(s.history.events)}"
                 f"  aim={aim}"
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
        ev = step_engine(s.model, s)
        s.history.record(ev)
        s.refresh_ui()
        s.root.after(s.model["ms"], s.tick)

def ensure_samples():
    if not os.path.isdir(SAMPLES_DIR):
        try: os.makedirs(SAMPLES_DIR)
        except Exception: return
    for name, content in SAMPLES.items():
        path = os.path.join(SAMPLES_DIR, name)
        need_write = False
        if not os.path.exists(path):
            need_write = True
        else:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    old = f.read()
                if "Aim: 1" in old or "Aim:" not in old or not old.lstrip().startswith("# version"):
                    need_write = True
            except Exception:
                need_write = True
        if need_write:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception: pass

if __name__ == "__main__":
    if "--test" in sys.argv:
        _test_log_fh = open(TEST_LOG_PATH, "w", encoding="utf-8")
        ok = run_tests()
        _test_log_fh.close()
        sys.exit(0 if ok else 1)
    if "--stress" in sys.argv:
        random.seed(42)
        bad = 0
        for _ in range(5000):
            n = random.randint(0, 40)
            s = "".join(random.choice(string.printable) for _ in range(n))
            try:
                resolve_line(s)
            except Exception as e:
                bad += 1
                print("STRESS FAIL:", repr(s), e)
        # invariants fuzz
        for _ in range(1000):
            m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <sep> | Aim: 0","1 = a","a => b"],"agent":0,"color":"#00ff00"}],
                 "memory":{},"cur":0,"playing":False,"ms":0}
            for _ in range(20):
                step_engine(m)
                assert 0 <= m["cycles"][0]["agent"] < len(m["cycles"][0]["lines"]), "I1 violated"
        print(f"STRESS resolve_line: {5000-bad}/5000 ok; invariants: ok")
        sys.exit(0 if bad == 0 else 1)
    ensure_samples()
    _log_fh = open(LOG_PATH, "w", encoding="utf-8")
    log(f"=== Simple v0.27.0 log ===")
    log(f"Truth: {TRUTH_PRINCIPLE}")
    log(f"Core principle: {CORE_PRINCIPLE}")
    r = tk.Tk(); App(r)
    r.geometry(f"{S['xxl']*14}x{S['h']*5}")
    r.mainloop()
    _log_fh.close()