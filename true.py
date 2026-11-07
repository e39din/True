# true.py — core of true language (no agent; agent is part of creator)
# Version: 0.9.9
# Axes: only x (chars) and y (lines), no z

# ===== IMPORTS =====
import re, math, os
from modules import (
    PHI, DEBUG, ESC_NL, ESC_CHAR, PH_OPEN, PH_CLOSE, HISTORY_MAX,
    TRUTH_PRINCIPLE, CORE_PRINCIPLE, TRUE_VERSION, NOT_TRUE_VERSION,
    log, set_log_fh,
    escape_for_parse, unescape_after_parse, escape_nl, unescape_nl,
    valid_name, BAD_NAME_CHARS,
    entails, eval_expr, apply_op, check_substrings,
    split_by_sep, join_by_sep, axis_index,
    parse_axis_ref, parse_axis_chain, parse_line_ref, parse_ref,
    mem_of, read_axis_chain, write_axis_chain, read_ref, write_ref,
    remove_from_axis, remove_line, remove_ref,
    swap_axis,
    QUAL_RE, AXIS_RE, AXIS_CHAIN_RE, LINE_RE,
)

# ===== LEXER =====
class Token:
    __slots__ = ("type", "value", "line", "col")
    def __init__(self, type_, value, line=0, col=0):
        self.type = type_; self.value = value
        self.line = line; self.col = col
    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r})"

NAME="NAME"; NUMBER="NUMBER"; STRING="STRING"; COLOR="COLOR"; OP="OP"
COND="COND"; EQ="EQ"; EXT="EXT"; VERSION="VERSION"; SEP="SEP"
JUMP="JUMP"; LPAREN="LPAREN"; RPAREN="RPAREN"
COMMA="COMMA"; COLON="COLON"

def _is_name_char(ch): return ch.isalnum() or ch in "._"
def _is_digit(ch): return ch.isdigit()
def _is_color_char(ch): return ch in "0123456789abcdefABCDEF"

def _tokenize_cycle(text):
    tokens = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        tokens.extend(_tokenize_cycle_line(line, lineno))
    return tokens

def _tokenize_cycle_line(line, lineno):
    tokens = []
    s = line.strip()
    if s.startswith("#"):
        if s.startswith("# version:"):
            tokens.append(Token(VERSION, s[10:].strip(), lineno, 1))
        return tokens
    if not s or s == "---":
        tokens.append(Token(SEP, "", lineno, 1)); return tokens
    if s.startswith("^"):
        tokens.append(Token(JUMP, s[1:].strip(), lineno, 1)); return tokens
    i = 0; n = len(line)
    while i < n:
        ch = line[i]
        if ch.isspace(): i += 1; continue
        if ch == "\\" and i + 1 < n:
            tokens.append(Token(STRING, line[i+1], lineno, i)); i += 2; continue
        if ch == ":" and i + 1 < n and line[i+1] == ":":
            j = i + 2
            while j < n and (line[j].isalnum() or line[j] in "._!"): j += 1
            tokens.append(Token(EXT, line[i:j], lineno, i)); i = j; continue
        if line.startswith("=>|", i): tokens.append(Token(OP, "=>|", lineno, i)); i += 3; continue
        if line.startswith("->|", i): tokens.append(Token(OP, "->|", lineno, i)); i += 3; continue
        if line.startswith("<->", i): tokens.append(Token(OP, "<->", lineno, i)); i += 3; continue
        if line.startswith("?=>", i): tokens.append(Token(OP, "?=>", lineno, i)); i += 3; continue
        if line.startswith("=>", i): tokens.append(Token(OP, "=>", lineno, i)); i += 2; continue
        if line.startswith("->", i): tokens.append(Token(OP, "->", lineno, i)); i += 2; continue
        if ch == "?": tokens.append(Token(COND, "?", lineno, i)); i += 1; continue
        if ch == "=": tokens.append(Token(EQ, "=", lineno, i)); i += 1; continue
        if ch == "(": tokens.append(Token(LPAREN, "(", lineno, i)); i += 1; continue
        if ch == ")": tokens.append(Token(RPAREN, ")", lineno, i)); i += 1; continue
        if ch == ",": tokens.append(Token(COMMA, ",", lineno, i)); i += 1; continue
        if ch == ":": tokens.append(Token(COLON, ":", lineno, i)); i += 1; continue
        if ch == "#":
            j = i + 1
            while j < n and _is_color_char(line[j]): j += 1
            if j - i == 7: tokens.append(Token(COLOR, line[i:j], lineno, i)); i = j; continue
            tokens.append(Token(STRING, ch, lineno, i)); i += 1; continue
        if _is_name_char(ch):
            j = i
            while j < n and _is_name_char(line[j]): j += 1
            tokens.append(Token(NAME, line[i:j], lineno, i)); i = j; continue
        if _is_digit(ch):
            j = i
            while j < n and (_is_digit(line[j]) or line[j] == "."): j += 1
            tokens.append(Token(NUMBER, line[i:j], lineno, i)); i = j; continue
        tokens.append(Token(STRING, ch, lineno, i)); i += 1
    return tokens

# ===== AST =====
class Node:
    def __repr__(self): return f"{self.__class__.__name__}({self.__dict__})"

class SeparatorNode(Node): pass
class VersionNode(Node):
    def __init__(self, n): self.n = n
class JumpNode(Node):
    def __init__(self, target): self.target = target
class ConditionNode(Node):
    def __init__(self, cond, act): self.cond = cond; self.act = act
class ActionNode(Node):
    def __init__(self, srcs, ops, dsts, evals):
        self.srcs = srcs; self.ops = ops
        self.dsts = dsts; self.evals = evals
class NamedNode(Node):
    def __init__(self, val, names): self.val = val; self.names = names
class ContainerNode(Node):
    def __init__(self, text): self.text = text
class RefNode(Node):
    def __init__(self, kind, cycle=None, base=None, axis=None, sep=None,
                 idx=None, parts=None, n=None):
        self.kind = kind; self.cycle = cycle; self.base = base
        self.axis = axis; self.sep = sep; self.idx = idx
        self.parts = parts; self.n = n
class ExprNode(Node):
    def __init__(self, kind, value=None, left=None, op=None, right=None):
        self.kind = kind; self.value = value
        self.left = left; self.op = op; self.right = right

# ===== PARSER =====
class CycleParser:
    def __init__(self, tokens):
        self.tokens = tokens; self.pos = 0
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def next(self):
        t = self.peek()
        if t: self.pos += 1
        return t
    def parse(self):
        nodes = []
        for line_tokens in self._group_by_lines():
            node = self.parse_line(line_tokens)
            if node is not None: nodes.append(node)
        return nodes
    def _group_by_lines(self):
        lines = {}
        for t in self.tokens:
            lines.setdefault(t.line, []).append(t)
        return [lines[k] for k in sorted(lines)]
    def parse_line(self, tokens):
        if not tokens: return SeparatorNode()
        t0 = tokens[0]
        if t0.type == VERSION: return VersionNode(t0.value)
        if t0.type == SEP: return SeparatorNode()
        if t0.type == JUMP: return JumpNode(t0.value)
        if any(t.type == COND for t in tokens): return self._parse_condition(tokens)
        if any(t.type == OP for t in tokens): return self._parse_action(tokens)
        if any(t.type == EQ for t in tokens): return self._parse_named(tokens)
        return ContainerNode(" ".join(t.value for t in tokens))
    def _parse_condition(self, tokens):
        cond_tokens = []; act_tokens = []; seen = False
        for t in tokens:
            if t.type == COND and not seen:
                seen = True; continue
            if seen: act_tokens.append(t)
            else: cond_tokens.append(t)
        cond = self._parse_expr(cond_tokens)
        act = self._parse_action(act_tokens) if act_tokens else None
        return ConditionNode(cond, act)
    def _parse_expr(self, tokens):
        if not tokens:
            return ExprNode("literal", value="")
        s = " ".join(t.value for t in tokens)
        return ExprNode("raw", value=s)
    def _parse_action(self, tokens):
        srcs = []; ops = []; dsts = []; evals = []
        segments = []; cur = []
        for t in tokens:
            if t.type == OP:
                segments.append(("src", cur)); cur = []
                segments.append(("op", t.value))
            elif t.type == JUMP:
                segments.append(("src", cur)); cur = []
                segments.append(("jump", t.value))
            else:
                cur.append(t)
        if cur: segments.append(("src", cur))
        for kind, val in segments:
            if kind == "src":
                if not val: continue
                if ops and len(srcs) > len(dsts):
                    dsts.append(self._parse_ref(val))
                else:
                    srcs.append(self._parse_ref(val))
            elif kind == "op":
                ops.append(val)
                evals.append(val.startswith("?"))
            elif kind == "jump":
                ops.append("^")
                dsts.append(RefNode("jump_target", base=val))
                evals.append(False)
        while len(dsts) < len(ops):
            dsts.append(None)
        return ActionNode(srcs, ops, dsts, evals)
    def _parse_named(self, tokens):
        val_tokens = []; name_tokens = []; seen = False
        for t in tokens:
            if t.type == EQ and not seen:
                seen = True; continue
            if seen: name_tokens.append(t)
            else: val_tokens.append(t)
        val = " ".join(t.value for t in val_tokens)
        names = [t.value for t in name_tokens if t.type == NAME]
        return NamedNode(val, names)
    def _parse_ref(self, tokens):
        if not tokens: return RefNode("name", base="")
        if len(tokens) >= 3 and tokens[0].type == NAME and tokens[1].type == COLON:
            cycle = tokens[0].value
            node = self._parse_ref(tokens[2:])
            node.cycle = cycle
            return node
        if tokens[0].type == COLON:
            rest = tokens[1:]
            if len(rest) >= 1 and rest[0].type == NAME and rest[0].value == "line":
                if len(rest) >= 3 and rest[1].type == COLON:
                    try: n = int(rest[2].value)
                    except Exception: n = 0
                    return RefNode("line", n=n)
            if len(rest) >= 3 and rest[0].type == NAME and rest[1].type == COLON:
                cycle = rest[0].value
                try: n = int(rest[2].value)
                except Exception: n = 0
                return RefNode("line", cycle=cycle, n=n)
        if len(tokens) >= 3 and tokens[0].type == NAME and tokens[1].type == COLON:
            base = tokens[0].value
            parts = []; i = 2
            while i < len(tokens):
                if tokens[i].type == NAME and tokens[i].value in ("x", "y"):
                    axis = tokens[i].value; sep = None; idx = None; i += 1
                    if i < len(tokens) and tokens[i].type == LPAREN:
                        i += 1; sep_chars = []
                        while i < len(tokens) and tokens[i].type != RPAREN:
                            sep_chars.append(tokens[i].value); i += 1
                        sep = "".join(sep_chars)
                        if i < len(tokens) and tokens[i].type == RPAREN: i += 1
                    if i < len(tokens) and tokens[i].type == COLON:
                        i += 1
                        if i < len(tokens) and tokens[i].type in (NAME, NUMBER):
                            idx = tokens[i].value; i += 1
                    parts.append((axis, sep, idx))
                else: break
            if len(parts) == 1:
                axis, sep, idx = parts[0]
                return RefNode("axis", base=base, axis=axis, sep=sep, idx=idx)
            return RefNode("axis_chain", base=base, parts=parts)
        if len(tokens) == 1 and tokens[0].type == NAME:
            return RefNode("name", base=tokens[0].value)
        if len(tokens) == 1 and tokens[0].type == NUMBER:
            return RefNode("line", n=int(tokens[0].value))
        return RefNode("name", base=" ".join(t.value for t in tokens))

def _parse_cycle_line(line):
    return CycleParser(_tokenize_cycle_line(line + "\n", 1)).parse()

# ===== REGEX =====
JUMP_RE    = re.compile(r'^\^\s*(?P<target>.+)$')
COND_RE    = re.compile(r'^(?P<cond>.+?)(?<!\?)\?\s*(?!=>\||->\||<->|=>|->)(?P<act>.*)$')
NAMED_RE   = re.compile(r'^(?P<val>.*?)\s*=\s*(?P<names>[\w.,\s]+)$')
ACTION_OP  = re.compile(r'(?<!\u0002)(\?)?(=>\||->\||<->|=>|->)')
VERSION_RE = re.compile(r'^\s*#\s*version:\s*(\d+)\s*$')

# ===== RESOLVE LINE =====
def resolve_line(line):
    try:
        nodes = _parse_cycle_line(line)
    except Exception as e:
        log(f"[parser] error: {e}")
        nodes = []
    if not nodes: return _resolve_line_regex(line)
    n = nodes[0]
    if isinstance(n, VersionNode): return "version", n
    if isinstance(n, SeparatorNode): return "separator", None
    if isinstance(n, JumpNode): return "jump", n
    if isinstance(n, ConditionNode): return "condition", n
    if isinstance(n, ActionNode): return "action", n
    if isinstance(n, NamedNode): return "named", n
    if isinstance(n, ContainerNode): return "container", n
    return "container", None

def _resolve_line_regex(line):
    if VERSION_RE.match(line): return "version", VERSION_RE.match(line)
    if line.lstrip().startswith("\\"): return "container", None
    line_esc = escape_for_parse(line)
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
            if m_cond: return "condition", m_cond
    if ACTION_OP.search(line_esc): return "action", ACTION_OP.search(line_esc)
    if NAMED_RE.match(line_esc): return "named", NAMED_RE.match(line_esc)
    return "container", None

# ===== FIND LINE BY NAME =====
def find_line_by_name(lines, name, model=None, cycle_name=None):
    if model is not None and cycle_name is not None:
        idx_cache = model.setdefault("name_index", {}).setdefault(cycle_name, None)
        if idx_cache is None:
            idx_cache = {}
            for i, ln in enumerate(lines):
                t, m = resolve_line(ln)
                if t == "named":
                    if isinstance(m, NamedNode):
                        for n in m.names: idx_cache[n] = i
                    elif hasattr(m, "group"):
                        try:
                            for n in re.split(r'[,\s]+', m.group("names")):
                                if n.strip(): idx_cache[n.strip()] = i
                        except Exception: pass
            model["name_index"][cycle_name] = idx_cache
        return idx_cache.get(name, -1)
    for i, ln in enumerate(lines):
        t, m = resolve_line(ln)
        if t == "named":
            if isinstance(m, NamedNode) and name in m.names: return i
            if hasattr(m, "group"):
                try:
                    if name in [n.strip() for n in re.split(r'[,\s]+', m.group("names")) if n.strip()]:
                        return i
                except Exception: pass
    return -1

def _invalidate_name_index(model, cycle_name):
    if "name_index" in model and cycle_name in model["name_index"]:
        del model["name_index"][cycle_name]

# ===== DO JUMP =====
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
                        model["cycles"][i]["agent_pos"] = max(0, min(n_int, len(model["cycles"][i]["lines"])-1))
                    else:
                        idx = find_line_by_name(model["cycles"][i]["lines"], target2, model, cycle_name)
                        if idx >= 0: model["cycles"][i]["agent_pos"] = idx
                        else: return False
                    return True
        return False
    if t.isdigit():
        n_int = int(t) - 1
        cyc["agent_pos"] = max(0, min(n_int, len(cyc["lines"])-1))
        return True
    idx = find_line_by_name(cyc["lines"], t, model, cyc["name"])
    if idx >= 0: cyc["agent_pos"] = idx; return True
    return False

# ===== EXTENSIONS =====
EXTENSIONS = {}
def register_extension(name, fn): EXTENSIONS[name] = fn

def ext_math(model, cyc, src, dst, op, eval_flag, bridge):
    mem = model["memory"].setdefault(cyc["name"], {})
    mem["::math"] = eval_expr(src, mem); return True

def ext_nothing(model, cyc, src, dst, op, eval_flag, bridge):
    if op in ("->", "->|"): remove_ref(model, cyc, src)
    return True

def _load_file_text(model, name_or_path):
    if os.path.sep in name_or_path or name_or_path.startswith("."):
        if os.path.exists(name_or_path):
            try:
                with open(name_or_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception: return None
    for c in model["cycles"]:
        if c["name"] == name_or_path or c["name"] == name_or_path + ".cycle":
            return "\n".join(c["lines"])
    if os.path.exists(name_or_path):
        try:
            with open(name_or_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception: return None
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, name_or_path)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception: return None
    return None

def _parse_gen_args(src):
    args = {}
    if "= args" in src: src = src.split("= args")[0].strip()
    for part in src.split(";"):
        part = part.strip()
        if not part: continue
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip().lstrip("$").lstrip("_")
            args[k] = v.strip()
    return args

def _substitute(text, args):
    for k, v in args.items():
        text = re.sub(r'[\$_]' + re.escape(k) + r'\b', v, text)
    return text

def ext_gen(model, cyc, src, dst, op, eval_flag, bridge):
    if not src: return False
    args = _parse_gen_args(src)
    template_name = None
    if dst and dst != "::gen": template_name = dst
    elif "args" in args: template_name = args.pop("args")
    else: return False
    template_text = _load_file_text(model, template_name)
    if template_text is None: return False
    new_text = _substitute(template_text, args)
    base_name = os.path.basename(template_name).rsplit(".", 1)[0]
    counter = 1
    existing = {c["name"] for c in model["cycles"]}
    new_name = f"{base_name}_{counter}.cycle"
    while new_name in existing:
        counter += 1
        new_name = f"{base_name}_{counter}.cycle"
    model["cycles"].append({"name": new_name, "lines": new_text.split("\n"),
                            "agent_pos": 0, "color": "#5fb85f", "loop": True, "has_agent": False})
    _invalidate_name_index(model, new_name)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, new_name), "w", encoding="utf-8") as f:
            f.write(new_text)
    except Exception: pass
    mem = model["memory"].setdefault(cyc["name"], {})
    mem["::gen"] = new_name
    mem["gen"] = new_name
    return True

def ext_check(model, cyc, src, dst, op, eval_flag, bridge):
    if not src: return False
    args_str = src
    if "= args" in args_str: args_str = args_str.split("= args")[0].strip()
    target = None
    if dst and dst != "::check": target = dst
    elif "args" in _parse_gen_args(src): target = _parse_gen_args(src).get("args")
    if not target: return False
    text = _load_file_text(model, target)
    if text is None: return False
    result = check_substrings(text, args_str)
    mem = model["memory"].setdefault(cyc["name"], {})
    mem["::check"] = result
    mem["check"] = result
    return True

register_extension("math", ext_math)
register_extension("nothing", ext_nothing)
register_extension("gen", ext_gen)
register_extension("check", ext_check)

# ===== ACTION EXECUTION =====
def _apply_single_op(model, cyc, src_raw, op, dst, eval_flag, bridge=None):
    mem = model["memory"].setdefault(cyc["name"], {})
    if dst in mem and isinstance(mem[dst], str) and mem[dst].startswith("::"):
        dst = mem[dst]
    if dst.startswith("::"):
        ext_name = dst[2:].split(":")[0]
        fn = EXTENSIONS.get(ext_name)
        if fn: fn(model, cyc, src_raw, dst, op, eval_flag, bridge); return
    if op == "<->":
        if swap_axis(mem, src_raw, dst): return
    if op == "^":
        do_jump(model, cyc, dst); return
    if "," in src_raw and not parse_axis_ref(src_raw) and not parse_line_ref(src_raw):
        srcs = [s.strip() for s in src_raw.split(",") if s.strip()]
    else:
        srcs = [src_raw]
    for src in srcs:
        if eval_flag: sv = eval_expr(src, mem)
        else:
            sv = read_ref(model, cyc, src)
            if sv is None: sv = mem.get(src, src)
        targets = [t.strip() for t in dst.split(",") if t.strip()] or [dst]
        for target in targets:
            if not valid_name(target) and not parse_axis_ref(target) and not parse_line_ref(target):
                continue
            write_ref(model, cyc, target, sv, op=op)
            if op in ("->", "->|"): remove_ref(model, cyc, src)

def exec_action(model, cyc, line, bridge=None):
    if line.lstrip().startswith("\\"): return
    line_esc = escape_for_parse(line)
    ops_found = list(ACTION_OP.finditer(line_esc))
    if not ops_found: return
    pairs = []; prev_end = 0
    for i, m in enumerate(ops_found):
        eval_flag = bool(m.group(1)); op = m.group(2)
        src = line_esc[prev_end:m.start()].strip() if i == 0 else pairs[-1][2]
        end = ops_found[i+1].start() if i+1 < len(ops_found) else len(line_esc)
        dst = line_esc[m.end():end].strip()
        pairs.append((src, op, dst, eval_flag))
        prev_end = m.end()
    for src_raw, op, dst, eval_flag in pairs:
        src_raw = unescape_after_parse(src_raw)
        dst = unescape_after_parse(dst)
        _apply_single_op(model, cyc, src_raw, op, dst, eval_flag, bridge)

def flush_memory_to_lines(cyc, model):
    mem = model["memory"].setdefault(cyc["name"], {})
    lines = cyc["lines"]
    for i, ln in enumerate(lines):
        t, m = resolve_line(ln)
        if t == "named":
            names = []
            if isinstance(m, NamedNode): names = m.names
            elif hasattr(m, "group"):
                try: names = [n.strip() for n in re.split(r'[,\s]+', m.group("names")) if n.strip()]
                except Exception: names = []
            if not names: continue
            primary = names[0]
            if primary in mem:
                val_esc = escape_nl(str(mem[primary]))
                new = f"{val_esc} = {', '.join(names)}"
                if new != ln:
                    lines[i] = new
                    _invalidate_name_index(model, cyc["name"])

def _exec_action_ast(model, cyc, node, bridge=None):
    srcs, ops, dsts, evals = node.srcs, node.ops, node.dsts, node.evals
    for i, op in enumerate(ops):
        src_node = srcs[i] if i < len(srcs) else None
        dst_node = dsts[i] if i < len(dsts) else None
        if not src_node or not dst_node: continue
        src_ref = _ref_to_str(src_node); dst_ref = _ref_to_str(dst_node)
        eval_flag = evals[i] if i < len(evals) else False
        _apply_single_op(model, cyc, src_ref, op, dst_ref, eval_flag, bridge)

def _ref_to_str(node):
    if node.kind == "name": return node.base
    if node.kind == "axis":
        s = f"{node.base}:{node.axis}"
        if node.sep is not None: s += f"({node.sep})"
        if node.idx is not None: s += f":{node.idx}"
        return s
    if node.kind == "axis_chain":
        s = node.base
        for axis, sep, idx in node.parts:
            s += f":{axis}"
            if sep is not None: s += f"({sep})"
            if idx is not None: s += f":{idx}"
        return s
    if node.kind == "line":
        if node.cycle: return f":{node.cycle}:{node.n}"
        return f":{node.n}"
    if node.kind == "jump_target": return node.base
    return ""

# ===== EXECUTE LINE =====
def execute_line(model, cyc, target_idx, bridge=None):
    line = cyc["lines"][target_idx]
    typ, node = resolve_line(line)
    if typ == "named":
        mem = model["memory"].setdefault(cyc["name"], {})
        if isinstance(node, NamedNode):
            val = unescape_nl(unescape_after_parse(node.val))
            for n in node.names:
                if valid_name(n): mem[n] = val
        elif hasattr(node, "group"):
            val_raw = unescape_after_parse(escape_for_parse(node.group("val")))
            val = unescape_nl(val_raw)
            names_raw = unescape_after_parse(escape_for_parse(node.group("names")))
            for n in re.split(r'[,\s]+', names_raw):
                if n and valid_name(n): mem[n] = val
        _invalidate_name_index(model, cyc["name"])
    elif typ == "condition":
        mem = model["memory"].setdefault(cyc["name"], {})
        if isinstance(node, ConditionNode):
            cond_str = node.cond.value if hasattr(node.cond, "value") else str(node.cond)
            if entails(cond_str, mem) and node.act:
                _exec_action_ast(model, cyc, node.act, bridge)
        elif hasattr(node, "group"):
            cond = node.group("cond").strip()
            act = node.group("act").strip()
            if entails(cond, mem) and act:
                exec_action(model, cyc, act, bridge)
    elif typ == "jump":
        if isinstance(node, JumpNode): do_jump(model, cyc, node.target)
        elif hasattr(node, "group"): do_jump(model, cyc, node.group("target"))
    elif typ == "action":
        if isinstance(node, ActionNode): _exec_action_ast(model, cyc, node, bridge)
        else: exec_action(model, cyc, line, bridge)
    elif typ == "version": pass
    elif typ == "container":
        text = node.text if isinstance(node, ContainerNode) else line
        for j in range(target_idx - 1, -1, -1):
            ln_j = cyc["lines"][j]
            t2, n2 = resolve_line(ln_j)
            if t2 == "named":
                names = []
                if isinstance(n2, NamedNode): names = n2.names
                elif hasattr(n2, "group"):
                    try: names = [n.strip() for n in re.split(r'[,\s]+', n2.group("names")) if n.strip()]
                    except Exception: names = []
                if names:
                    primary = names[0]
                    mem = model["memory"].setdefault(cyc["name"], {})
                    if primary in mem:
                        mem[primary] += "\n" + text; break
            elif t2 == "separator": break
    return typ

# ===== STEP ENGINE =====
def step_engine(model, bridge=None):
    event = {"kind": None, "cycle": None, "old": {}, "new": {}}
    if not model["cycles"]: return event
    cyc = model["cycles"][model["cur"]]
    event["cycle"] = cyc["name"]
    lines = cyc["lines"]; a = cyc.get("agent_pos", 0)
    if not lines: return event
    loop = cyc.get("loop", True)
    target = a + 1
    if target >= len(lines):
        event["old"] = {"agent_pos": a, "lines": lines[:]}
        if not loop:
            event["kind"] = "end"
            event["new"] = {"agent_pos": a, "lines": lines[:]}
            cyc["agent_pos"] = a
            model["playing"] = False
            return event
        event["kind"] = "rotate"
        agent_line = lines[a]
        del lines[a]; lines.insert(0, agent_line)
        cyc["agent_pos"] = 0
        event["new"] = {"agent_pos": 0, "lines": lines[:]}
        _invalidate_name_index(model, cyc["name"])
        return event
    old_mem = dict(model["memory"].setdefault(cyc["name"], {}))
    old_lines = lines[:]; old_agent = a
    if a == 0 and cyc.get("has_agent", False):
        typ_target = "agent"
    else:
        typ_target = execute_line(model, cyc, target, bridge)
    if typ_target == "jump":
        event["kind"] = "jump"
        event["old"] = {"agent_pos": old_agent, "mem": old_mem}
        event["new"] = {"agent_pos": cyc.get("agent_pos", 0), "mem": dict(model["memory"][cyc["name"]])}
        return event
    dirty = model.get("dirty", set())
    dirty.add(cyc["name"])
    for name in list(dirty):
        for c in model["cycles"]:
            if c["name"] == name: flush_memory_to_lines(c, model)
    model["dirty"] = set()
    lines[a], lines[target] = lines[target], lines[a]
    cyc["agent_pos"] = target
    model["step_count"] = model.get("step_count", 0) + 1
    event["kind"] = "step"
    event["old"] = {"agent_pos": old_agent, "mem": old_mem, "lines": old_lines}
    event["new"] = {"agent_pos": target, "mem": dict(model["memory"][cyc["name"]]), "lines": lines[:]}
    return event

# ===== HISTORY =====
class History:
    def __init__(self, max_size=HISTORY_MAX):
        self.events = []; self.pos = -1; self.max_size = max_size
    def record(self, event):
        if not event or event.get("kind") is None: return
        self.events = self.events[:self.pos+1]
        self.events.append(event)
        if len(self.events) > self.max_size: self.events.pop(0)
        self.pos = len(self.events) - 1
    def undo(self, model):
        if self.pos < 0: return None
        ev = self.events[self.pos]; self.pos -= 1
        apply_reverse(model, ev); return ev
    def redo(self, model):
        if self.pos + 1 >= len(self.events): return None
        self.pos += 1; ev = self.events[self.pos]
        apply_forward(model, ev); return ev
    def clear(self): self.events = []; self.pos = -1

def apply_reverse(model, ev):
    cyc = next((c for c in model["cycles"] if c["name"] == ev.get("cycle")), None)
    if not cyc: return
    if ev.get("kind") in ("step", "rotate"):
        if "lines" in ev["old"]: cyc["lines"] = ev["old"]["lines"][:]
        if "agent_pos" in ev["old"]: cyc["agent_pos"] = ev["old"]["agent_pos"]
    elif ev.get("kind") in ("jump",):
        if "agent_pos" in ev["old"]: cyc["agent_pos"] = ev["old"]["agent_pos"]
    if "mem" in ev.get("old", {}): model["memory"][ev["cycle"]] = dict(ev["old"]["mem"])

def apply_forward(model, ev):
    cyc = next((c for c in model["cycles"] if c["name"] == ev.get("cycle")), None)
    if not cyc: return
    if ev.get("kind") in ("step", "rotate"):
        if "lines" in ev["new"]: cyc["lines"] = ev["new"]["lines"][:]
        if "agent_pos" in ev["new"]: cyc["agent_pos"] = ev["new"]["agent_pos"]
    elif ev.get("kind") in ("jump",):
        if "agent_pos" in ev["new"]: cyc["agent_pos"] = ev["new"]["agent_pos"]
    if "mem" in ev.get("new", {}): model["memory"][ev["cycle"]] = dict(ev["new"]["mem"])

def snapshot(model):
    return {"cur": model["cur"],
            "cycles": [{"name": c["name"], "lines": c["lines"][:], "agent_pos": c.get("agent_pos", 0), "color": c.get("color", "#5fb85f"), "loop": c.get("loop", True), "has_agent": c.get("has_agent", False)} for c in model["cycles"]],
            "memory": {k: dict(v) for k, v in model["memory"].items()}}

def restore(model, snap):
    model["cur"] = snap["cur"]
    model["memory"] = {k: dict(v) for k, v in snap["memory"].items()}
    for c, sc in zip(model["cycles"], snap["cycles"]):
        c["lines"] = sc["lines"][:]; c["agent_pos"] = sc.get("agent_pos", 0); c["color"] = sc["color"]
        c["loop"] = sc.get("loop", True); c["has_agent"] = sc.get("has_agent", False)