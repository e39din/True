# modules.py — shared utilities for true and !true
# Version: true 0.9.9 / !true 0.9.6
import re, math

PHI = 1.618
DEBUG = True
ESC_NL = "\\n"
ESC_CHAR = "\u0001"
PH_OPEN = "\u0002"
PH_CLOSE = "\u0003"
HISTORY_MAX = 100
TRUTH_PRINCIPLE = "Truth is what can be used."
CORE_PRINCIPLE = "Programming must be open, visual, easy and beautiful — all at once."
TRUE_VERSION = "0.9.9"
NOT_TRUE_VERSION = "0.9.6"

LOG_LEVELS = {"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}
_log_fh = None
_log_level = "INFO"

def set_log_level(level):
    global _log_level
    if level in LOG_LEVELS:
        _log_level = level

def log(msg, level="INFO"):
    if _log_fh is None: return
    if LOG_LEVELS.get(level, 0) < LOG_LEVELS.get(_log_level, 0): return
    if level != "INFO":
        msg = f"[{level}] {msg}"
    try:
        _log_fh.write(msg + "\n"); _log_fh.flush()
    except Exception: pass

def set_log_fh(fh):
    global _log_fh
    _log_fh = fh

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

BAD_NAME_CHARS = set('=><\\,;?/:"`\'')
def valid_name(n):
    if not n: return False
    if n.startswith("::"): return True
    for ch in n:
        if ch in BAD_NAME_CHARS: return False
    return True

def _is_number(s):
    try:
        float(s); return True
    except (ValueError, TypeError):
        return False

def apply_op(prev, op, right):
    if op == "+":
        if not (_is_number(prev) and _is_number(right)):
            v = str(prev) + str(right)
            log(f"[apply_op] {prev!r} + {right!r} (str) -> {v!r}", "DEBUG")
            return v
    try:
        e = f"({prev}) {op} ({right})"
        if op == "^": e = f"({prev}) ** ({right})"
        v = eval(e, {"__builtins__":{}, "math": math}, {})
        if isinstance(v, bool): v = "1" if v else "0"
        elif isinstance(v, float) and v.is_integer(): v = str(int(v))
        else: v = str(v)
        log(f"[apply_op] {prev!r} {op} {right!r} -> {v!r}", "DEBUG")
        return v
    except Exception:
        log(f"[apply_op] FAIL {prev!r} {op} {right!r} -> {prev!r}", "WARN")
        return str(prev)

def eval_expr(expr, mem):
    e = expr.strip()
    log(f"[eval_expr] {expr!r} mem={mem}", "DEBUG")
    if "?" in e and ":" in e:
        try:
            qpos = e.find("?"); cpos = e.rfind(":")
            if 0 < qpos < cpos:
                cond = e[:qpos].strip(); a = e[qpos+1:cpos].strip(); b = e[cpos+1:].strip()
                r = eval_expr(a if entails(cond, mem) else b, mem)
                log(f"[eval_expr] ternary {cond!r} -> {r!r}", "DEBUG")
                return r
        except Exception: pass
    orig = e
    e = e.replace("= =", "==").replace("! =", "!=").replace("> =", ">=").replace("< =", "<=")
    for name in sorted(mem.keys(), key=len, reverse=True):
        if name.startswith("::"): continue
        e = re.sub(r'\b' + re.escape(name) + r'\b', str(mem[name]), e)
    if e != orig: log(f"[eval_expr] subst {orig!r} -> {e!r}", "DEBUG")
    try:
        e2 = e.replace("^","**").replace("&&"," and ").replace("||"," or ")
        e2 = re.sub(r'\bsqrt\s*\(', 'math.sqrt(', e2)
        e2 = re.sub(r'\bsin\s*\(', 'math.sin(', e2)
        e2 = re.sub(r'\bcos\s*\(', 'math.cos(', e2)
        v = eval(e2, {"__builtins__":{}, "math": math}, {})
        if isinstance(v, bool): v = "1" if v else "0"
        elif isinstance(v, float) and v.is_integer(): v = str(int(v))
        else: v = str(v)
        log(f"[eval_expr] -> {v!r}", "DEBUG")
        return v
    except Exception as ex:
        if e != orig:
            stripped = e.rstrip(" +-*/%^")
            r = stripped if stripped != "" else ""
        else:
            r = orig
        log(f"[eval_expr] FAIL {e!r} ({ex}) -> {r!r}", "WARN")
        return r

def entails(phi, mem):
    v = eval_expr(phi, mem)
    if v is None: r = False
    elif isinstance(v, bool): r = v
    else:
        s = str(v).strip()
        if "=" in s or "<" in s or ">" in s:
            r = False
        else:
            r = s not in ("0", "", "False", "⊥")
    log(f"[entails] {phi!r} -> {r}", "DEBUG")
    return r

def split_by_sep(s, sep):
    if not s: r = []
    elif sep and sep in s: r = s.split(sep)
    elif not sep: r = list(s)
    elif "," in s: r = [x.strip() for x in s.split(",")]
    else: r = [s]
    log(f"[split_by_sep] {s!r} sep={sep!r} -> {r!r}", "DEBUG")
    return r

def join_by_sep(items, sep):
    if not sep: r = "".join(items)
    elif sep == ", ": r = ", ".join(items)
    elif sep == "\n": r = "\n".join(items)
    else: r = sep.join(items)
    log(f"[join_by_sep] {items!r} sep={sep!r} -> {r!r}", "DEBUG")
    return r

def axis_index(idx, items, mem=None):
    if idx in (None, "", "all"): r = None
    elif idx == "last": r = len(items) - 1
    elif idx == "first": r = 0
    else:
        if mem and idx in mem: idx = mem[idx]
        try: r = int(idx) - 1
        except (ValueError, TypeError): r = None
    log(f"[axis_index] {idx!r} items={items!r} -> {r}", "DEBUG")
    return r

QUAL_RE    = re.compile(r'^(?:(?P<cycle>[\w.]+):)?(?P<rest>.+)$')
AXIS_RE    = re.compile(r'^(?P<base>[\w.]+):(?P<axis>[xy])(?:\((?P<sep>[^)]*)\))?(?::(?P<idx>[\w]+))?$')
AXIS_CHAIN_RE = re.compile(r'^(?P<base>[\w.]+)(?P<axes>(?::[xy](?:\([^)]*\))?(?::[\w]+)?)+)$')
LINE_RE    = re.compile(r'^:(?P<cycle>[\w.]*):line:(?P<n>\d+)$')

def parse_axis_ref(ref):
    m = AXIS_RE.match(ref)
    if not m: return None
    sep = m.group("sep")
    if sep is None:
        if m.group("axis") == "y": sep = "\n"
        else: sep = ""
    return m.group("base"), m.group("axis"), sep, m.group("idx")

def parse_axis_chain(ref):
    m = AXIS_CHAIN_RE.match(ref)
    if not m: return None
    base = m.group("base")
    axes_str = m.group("axes")
    parts = re.findall(r':([xy])(?:\(([^)]*)\))?(?::([\w]+))?', axes_str)
    return base, parts

def parse_line_ref(ref):
    m = LINE_RE.match(ref)
    if not m: return None
    return m.group("cycle") or None, int(m.group("n"))

def parse_ref(ref):
    ref = ref.strip()
    if not ref: r = None
    elif ref.startswith(":"):
        pl = parse_line_ref(ref)
        if pl: r = {"kind":"line","cycle":pl[0],"n":pl[1]}
        else:
            parts = ref.strip(":").split(":")
            if len(parts) == 2 and parts[1].isdigit():
                r = {"kind":"line","cycle":parts[0],"n":int(parts[1])}
            else: r = None
    else:
        p = parse_axis_ref(ref)
        if p:
            base, axis, sep, idx = p
            r = {"kind":"axis","cycle":None,"base":base,"axis":axis,"sep":sep,"idx":idx}
        else:
            chain = parse_axis_chain(ref)
            if chain:
                base, parts = chain
                r = {"kind":"axis_chain","cycle":None,"base":base,"parts":parts}
            else:
                m = QUAL_RE.match(ref)
                if not m: r = None
                else:
                    cycle = m.group("cycle"); rest = m.group("rest")
                    if cycle and rest.isdigit():
                        r = {"kind":"line","cycle":cycle,"n":int(rest)}
                    elif cycle and rest.startswith("line:"):
                        try: n = int(rest[5:])
                        except Exception: n = 0
                        r = {"kind":"line","cycle":cycle,"n":n}
                    else:
                        p2 = parse_axis_ref(rest)
                        if p2:
                            base, axis, sep, idx = p2
                            r = {"kind":"axis","cycle":cycle,"base":base,"axis":axis,"sep":sep,"idx":idx}
                        else:
                            chain2 = parse_axis_chain(rest)
                            if chain2:
                                base, parts = chain2
                                r = {"kind":"axis_chain","cycle":cycle,"base":base,"parts":parts}
                            else:
                                r = {"kind":"name","cycle":cycle,"base":rest,"axis":None,"sep":None,"idx":None}
    log(f"[parse_ref] {ref!r} -> {r}", "DEBUG")
    return r

def mem_of(model, cycle_name, cur_cyc_name):
    if cycle_name:
        for c in model["cycles"]:
            if c["name"] == cycle_name:
                return model["memory"].setdefault(cycle_name, {})
        return None
    return model["memory"].setdefault(cur_cyc_name, {})

def read_axis_chain(mem, base, parts):
    v = mem.get(base, "")
    for axis, sep, idx in parts:
        sep_eff = sep if sep is not None else ("\n" if axis=="y" else "")
        items = split_by_sep(v, sep_eff)
        i = axis_index(idx, items, mem)
        if i is None or not (0 <= i < len(items)): return None
        v = items[i]
    return v

def write_axis_chain(mem, base, parts, value, op):
    if len(parts) == 1:
        axis, sep, idx = parts[0]
        sep_eff = sep if sep is not None else ("\n" if axis=="y" else "")
        items = split_by_sep(mem.get(base, ""), sep_eff)
        i = axis_index(idx, items, mem)
        if op in ("=>", "->"):
            if i is not None and 0 <= i < len(items): items[i] = value
            elif idx not in (None,"","all"): items.insert(int(idx)-1, value)
            else: items.append(value)
        else:
            if idx not in (None,"","all"): items.insert(int(idx)-1, value)
            else: items.append(value)
        mem[base] = join_by_sep(items, sep_eff)
        return True
    axis, sep, idx = parts[0]
    sep_eff = sep if sep is not None else ("\n" if axis=="y" else "")
    items = split_by_sep(mem.get(base, ""), sep_eff)
    i = axis_index(idx, items, mem)
    if i is None or not (0 <= i < len(items)): return False
    sub = items[i]
    sub_mem = {"__sub": sub}
    ok = write_axis_chain(sub_mem, "__sub", parts[1:], value, op)
    if ok:
        items[i] = sub_mem["__sub"]
        mem[base] = join_by_sep(items, sep_eff)
    return ok

def read_ref(model, cyc, ref):
    p = parse_ref(ref)
    if not p: r = None
    else:
        mem = mem_of(model, p["cycle"], cyc["name"])
        if mem is None: r = None
        elif p["kind"] == "name": r = mem.get(p["base"])
        elif p["kind"] == "axis":
            sep_eff = p["sep"] if p["sep"] is not None else ("\n" if p["axis"]=="y" else "")
            items = split_by_sep(mem.get(p["base"], ""), sep_eff)
            i = axis_index(p["idx"], items, mem)
            r = items[i] if i is not None and 0 <= i < len(items) else None
        elif p["kind"] == "axis_chain": r = read_axis_chain(mem, p["base"], p["parts"])
        elif p["kind"] == "line":
            r = None
            for c in model["cycles"]:
                if (p["cycle"] or cyc["name"]) == c["name"]:
                    if 0 <= p["n"]-1 < len(c["lines"]):
                        r = c["lines"][p["n"]-1]
        else: r = None
    log(f"[read_ref] {ref!r} -> {r!r}", "DEBUG")
    return r

def write_ref(model, cyc, ref, value, op="=>"):
    p = parse_ref(ref)
    if not p: return False
    mem = mem_of(model, p["cycle"], cyc["name"])
    if mem is None: return False
    if p["kind"] == "name":
        mem[p["base"]] = value
        log(f"[write_ref] {ref!r} = {value!r} (name)", "DEBUG")
        return True
    if p["kind"] == "axis":
        base, axis, sep, idx = p["base"], p["axis"], p["sep"], p["idx"]
        sep_eff = sep if sep is not None else ("\n" if axis=="y" else "")
        items = split_by_sep(mem.get(base, ""), sep_eff)
        i = axis_index(idx, items, mem)
        if op in ("=>", "->"):
            if i is not None and 0 <= i < len(items): items[i] = value
            elif idx not in (None,"","all"):
                try: items.insert(int(idx)-1, value)
                except Exception: items.append(value)
            else: items.append(value)
        else:
            if idx not in (None,"","all"):
                try: items.insert(int(idx)-1, value)
                except Exception: items.append(value)
            else: items.append(value)
        mem[base] = join_by_sep(items, sep_eff)
        log(f"[write_ref] {ref!r} = {value!r} (axis) -> {mem[base]!r}", "DEBUG")
        return True
    if p["kind"] == "axis_chain":
        ok = write_axis_chain(mem, p["base"], p["parts"], value, op)
        log(f"[write_ref] {ref!r} = {value!r} (chain) -> {ok}", "DEBUG")
        return ok
    if p["kind"] == "line":
        for c in model["cycles"]:
            if (p["cycle"] or cyc["name"]) == c["name"]:
                if 0 <= p["n"]-1 < len(c["lines"]):
                    c["lines"][p["n"]-1] = value
                    log(f"[write_ref] {ref!r} = {value!r} (line)", "DEBUG")
                    return True
        return False
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
        items.pop(i); mem[base] = join_by_sep(items, sep); return True
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
        if target_cyc["agent_pos"] > idx: target_cyc["agent_pos"] -= 1
        elif target_cyc["agent_pos"] == idx: target_cyc["agent_pos"] = max(0, idx - 1)
        return True
    return False

def remove_ref(model, cyc, ref):
    p = parse_ref(ref)
    if not p: return False
    if p["kind"] == "name":
        mem = mem_of(model, p["cycle"], cyc["name"])
        if mem is None: return False
        mem.pop(p["base"], None)
        log(f"[remove_ref] {ref!r} (name)", "DEBUG")
        return True
    if p["kind"] == "axis":
        ok = remove_from_axis(model, cyc, ref)
        log(f"[remove_ref] {ref!r} (axis) -> {ok}", "DEBUG")
        return ok
    if p["kind"] == "line": return remove_line(model, cyc, ref)
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
        si = axis_index(s_idx, items, mem); di = axis_index(d_idx, items, mem)
        if si is None or di is None: return False
        if not (0 <= si < len(items) and 0 <= di < len(items)): return False
        items[si], items[di] = items[di], items[si]
        mem[s_base] = join_by_sep(items, s_sep_eff); return True
    s_items = split_by_sep(mem.get(s_base, ""), s_sep_eff)
    d_items = split_by_sep(mem.get(d_base, ""), d_sep_eff)
    si = axis_index(s_idx, s_items, mem); di = axis_index(d_idx, d_items, mem)
    if si is None or di is None: return False
    if not (0 <= si < len(s_items) and 0 <= di < len(d_items)): return False
    s_items[si], d_items[di] = d_items[di], s_items[si]
    mem[s_base] = join_by_sep(s_items, s_sep_eff)
    mem[d_base] = join_by_sep(d_items, d_sep_eff)
    return True

def check_substrings(text, substrings):
    if not substrings: return "0"
    for sub in substrings.split(";"):
        sub = sub.strip()
        if not sub: continue
        if sub not in text: return "0"
    return "1"