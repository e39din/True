# true.py — core of true language
# Version: 0.9.9
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
            nxt = line[i+1]
            if nxt == "n":
                tokens.append(Token(STRING, ESC_NL, lineno, i)); i += 2; continue
            tokens.append(Token(STRING, nxt, lineno, i)); i += 2; continue
        if ch == ":" and i + 1 < n and line[i+1] == ":":
            j = i + 2
            while j < n and (line[j].isalnum() or line[j] in "._!"): j += 1
            tokens.append(Token(EXT, line[i:j], lineno, i)); i = j; continue
        if line.startswith("?=>|", i): tokens.append(Token(OP, "?=>|", lineno, i)); i += 4; continue
        if line.startswith("=>|", i): tokens.append(Token(OP, "=>|", lineno, i)); i += 3; continue
        if line.startswith("->|", i): tokens.append(Token(OP, "->|", lineno, i)); i += 3; continue
        if line.startswith("<->", i): tokens.append(Token(OP, "<->", lineno, i)); i += 3; continue
        if line.startswith("?=>", i): tokens.append(Token(OP, "?=>", lineno, i)); i += 3; continue
        if line.startswith("=>", i): tokens.append(Token(OP, "=>", lineno, i)); i += 2; continue
        if line.startswith("->", i): tokens.append(Token(OP, "->", lineno, i)); i += 2; continue
        if ch == "?": tokens.append(Token(COND, "?", lineno, i)); i += 1; continue
        if ch == "=": tokens.append(Token(EQ, "=", lineno, i)); i += 1; continue
        if ch == "(":
            j = i + 1; depth = 1
            while j < n and depth > 0:
                if line[j] == "(": depth += 1
                elif line[j] == ")": depth -= 1
                j += 1
            sep_text = line[i+1:j-1] if depth == 0 else line[i+1:]
            tokens.append(Token(LPAREN, "(", lineno, i))
            if sep_text:
                tokens.append(Token(STRING, sep_text, lineno, i+1))
            if depth == 0:
                tokens.append(Token(RPAREN, ")", lineno, j-1))
                i = j
            else:
                i = n
            continue
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
        if t0.type == EXT:
            full = t0.value
            j = 1
            while j < len(tokens):
                if tokens[j].type == COLON and j + 1 < len(tokens) and tokens[j+1].type == NAME:
                    full += ":" + tokens[j+1].value
                    j += 2
                else:
                    break
            return ActionNode(
                [RefNode("name", base="")],
                ["=>"],
                [RefNode("name", base=full)],
                [False]
            )
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
        parts = []
        prev_eq = False
        for t in tokens:
            if t.type == EQ and prev_eq:
                parts[-1] += "="
                prev_eq = True
                continue
            parts.append(t.value)
            prev_eq = (t.type == EQ)
        s = " ".join(parts)
        return ExprNode("raw", value=s)
    def _parse_action(self, tokens):
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
        srcs = []; ops = []; dsts = []; evals = []
        for kind, val in segments:
            if kind == "src":
                if not val: continue
                if not ops:
                    srcs.append(self._parse_ref(val))
                else:
                    dsts.append(self._parse_ref(val))
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
        val = val.replace(" " + ESC_NL + " ", ESC_NL)
        val = val.replace(ESC_NL + " ", ESC_NL).replace(" " + ESC_NL, ESC_NL)
        val = re.sub(r'\s*,\s*', ', ', val)
        names = [t.value for t in name_tokens if t.type == NAME]
        return NamedNode(val, names)
    def _parse_ref(self, tokens):
        if not tokens: return RefNode("name", base="")
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
        if len(tokens) >= 3 and tokens[0].type == NAME and tokens[1].type == COLON and tokens[2].type == NAME and tokens[2].value in ("x", "y"):
            base = tokens[0].value
            parts = []; i = 2
            while i < len(tokens):
                if tokens[i].type == NAME and tokens[i].value in ("x", "y"):
                    axis = tokens[i].value; sep = None; idx = None; i += 1
                    if i < len(tokens) and tokens[i].type == LPAREN:
                        i += 1
                        if i < len(tokens) and tokens[i].type == STRING:
                            sep = tokens[i].value; i += 1
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
        if len(tokens) >= 3 and tokens[0].type == NAME and tokens[1].type == COLON:
            cycle = tokens[0].value
            node = self._parse_ref(tokens[2:])
            node.cycle = cycle
            return node
        if len(tokens) == 1 and tokens[0].type == NAME:
            return RefNode("name", base=tokens[0].value)
        if len(tokens) == 1 and tokens[0].type == NUMBER:
            return RefNode("line", n=int(tokens[0].value))
        return RefNode("name", base=" ".join(t.value for t in tokens))

def _parse_cycle_line(line):
    return CycleParser(_tokenize_cycle_line(line + "\n", 1)).parse()

JUMP_RE    = re.compile(r'^\^\s*(?P<target>.+)$')
COND_RE    = re.compile(r'^(?P<cond>.+?)(?<!\?)\?\s*(?!=>\||->\||<->|=>|->)(?P<act>.*)$')
NAMED_RE   = re.compile(r'^(?P<val>.*?)\s*=\s*(?P<names>[\w.,\s]+)$')
ACTION_OP  = re.compile(r'(?<!\u0002)(\?)?(=>\||->\||<->|=>|->)')
VERSION_RE = re.compile(r'^\s*#\s*version:\s*(\d+)\s*$')

def resolve_line(line):
    try:
        nodes = _parse_cycle_line(line)
    except Exception as e:
        log(f"[parser] error: {e}", "WARN")
        nodes = []
    if not nodes: typ = _resolve_line_regex(line)
    else:
        n = nodes[0]
        if isinstance(n, VersionNode): typ = ("version", n)
        elif isinstance(n, SeparatorNode): typ = ("separator", None)
        elif isinstance(n, JumpNode): typ = ("jump", n)
        elif isinstance(n, ConditionNode): typ = ("condition", n)
        elif isinstance(n, ActionNode): typ = ("action", n)
        elif isinstance(n, NamedNode): typ = ("named", n)
        elif isinstance(n, ContainerNode): typ = ("container", n)
        else: typ = ("container", None)
    log(f"[resolve_line] {line!r} -> {typ[0]}", "DEBUG")
    return typ

def _resolve_line_regex(line):
    if VERSION_RE.match(line): return "version", VERSION_RE.match(line)
    if line.lstrip().startswith("\\"): return "container", None
    if line.lstrip().startswith("::"):
        return "action", None
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
                    log(f"[jump] -> cycle={cycle_name} agent_pos={model['cycles'][i]['agent_pos']}", "DEBUG")
                    return True
        return False
    if t.isdigit():
        n_int = int(t) - 1
        cyc["agent_pos"] = max(0, min(n_int, len(cyc["lines"])-1))
        log(f"[jump] ^ {t} -> agent_pos={cyc['agent_pos']}", "DEBUG")
        return True
    idx = find_line_by_name(cyc["lines"], t, model, cyc["name"])
    if idx >= 0:
        cyc["agent_pos"] = idx
        log(f"[jump] ^ {t!r} -> agent_pos={cyc['agent_pos']}", "DEBUG")
        return True
    return False

EXTENSIONS = {}
def register_extension(name, fn): EXTENSIONS[name] = fn

def ext_math(model, cyc, src, dst, op, eval_flag, bridge):
    mem = model["memory"].setdefault(cyc["name"], {})
    mem["::math"] = eval_expr(src, mem)
    log(f"[ext_math] {src!r} -> {mem['::math']!r}", "DEBUG")
    return True

def ext_nothing(model, cyc, src, dst, op, eval_flag, bridge):
    if op in ("->", "->|"):
        remove_ref(model, cyc, src)
        log(f"[ext_nothing] removed {src!r}", "DEBUG")
    return True

def ext_random(model, cyc, src, dst, op, eval_flag, bridge):
    import random as _r
    mem = model["memory"].setdefault(cyc["name"], {})
    lo, hi = 1, 6
    if src:
        parts = [p.strip() for p in src.split(",") if p.strip()]
        if len(parts) >= 2:
            try: lo = int(float(eval_expr(parts[0], mem))); hi = int(float(eval_expr(parts[1], mem)))
            except Exception: pass
        elif len(parts) == 1:
            try: hi = int(float(eval_expr(parts[0], mem)))
            except Exception: pass
    v = str(_r.randint(lo, hi))
    mem["::random"] = v
    if dst and dst != "::random":
        write_ref(model, cyc, dst, v, op=op)
    log(f"[ext_random] {lo}..{hi} -> {v}", "DEBUG")
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
    mem = model["memory"].setdefault(cyc["name"], {})
    parts = [p.strip() for p in src.split(",") if p.strip()]
    if not parts: return False
    template_name = parts[0]
    args = {}
    if len(parts) > 1:
        arg_name = parts[1]
        raw = mem.get(arg_name, arg_name)
        args = _parse_gen_args(raw)
    template_text = _load_file_text(model, template_name)
    if template_text is None:
        template_text = _load_file_text(model, template_name + ".txt")
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
                            "agent_pos": 0, "color": "#5fb85f", "loop": False, "has_agent": False})
    _invalidate_name_index(model, new_name)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, new_name), "w", encoding="utf-8") as f:
            f.write(new_text)
    except Exception: pass
    mem["::gen"] = new_name
    mem["gen"] = new_name
    log(f"[ext_gen] {template_name!r} -> {new_name!r}", "DEBUG")
    return True

def ext_check(model, cyc, src, dst, op, eval_flag, bridge):
    if not src: return False
    mem = model["memory"].setdefault(cyc["name"], {})
    parts = [p.strip() for p in src.split(",") if p.strip()]
    if not parts: return False
    target = parts[0]
    args_str = ""
    if len(parts) > 1:
        arg_name = parts[1]
        args_str = mem.get(arg_name, arg_name)
    text = _load_file_text(model, target)
    if text is None: return False
    result = check_substrings(text, args_str)
    mem["::check"] = result
    mem["check"] = result
    log(f"[ext_check] {target!r} -> {result!r}", "DEBUG")
    return True

register_extension("math", ext_math)
register_extension("nothing", ext_nothing)
register_extension("random", ext_random)
register_extension("gen", ext_gen)
register_extension("check", ext_check)

def _apply_single_op(model, cyc, src_raw, op, dst, eval_flag, bridge=None):
    mem = model["memory"].setdefault(cyc["name"], {})
    log(f"[apply] src={src_raw!r} op={op!r} dst={dst!r} eval={eval_flag} mem={mem}", "DEBUG")
    if dst in mem and isinstance(mem[dst], str) and mem[dst].startswith("::"):
        dst = mem[dst]
    if dst.startswith("::!"):
        fname = dst[3:]
        args = []
        if src_raw:
            sv = read_ref(model, cyc, src_raw)
            if sv is None: sv = mem.get(src_raw, src_raw)
            args = [sv]
        r = None
        if bridge is not None and hasattr(bridge, "call_fn"):
            r = bridge.call_fn(fname, args)
        if r is not None:
            mem[fname] = r
            mem[":!" + fname] = r
        log(f"[apply] ::!{fname} -> {r!r}", "DEBUG")
        return
    if dst.startswith("::"):
        ext_name = dst[2:].split(":")[0]
        fn = EXTENSIONS.get(ext_name)
        if fn:
            fn(model, cyc, src_raw, dst, op, eval_flag, bridge)
            log(f"[apply] ::{ext_name} done, mem={mem}", "DEBUG")
        return
    if dst.startswith(":") and not dst.startswith("::"):
        fname = dst[1:]
        args = []
        if src_raw:
            sv = read_ref(model, cyc, src_raw)
            if sv is None: sv = mem.get(src_raw, src_raw)
            args = [sv]
        r = None
        if bridge is not None and hasattr(bridge, "call_fn"):
            r = bridge.call_fn(fname, args)
        if r is not None:
            mem[fname] = r
            mem[":!" + fname] = r
        log(f"[apply] :{fname} -> {r!r}", "DEBUG")
        return
    if op == "<->":
        if swap_axis(mem, src_raw, dst):
            log(f"[apply] <-> {src_raw!r} {dst!r} mem={mem}", "DEBUG")
            return
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
        if "," in dst and not parse_axis_ref(dst) and not parse_line_ref(dst):
            targets = [t.strip() for t in dst.split(",") if t.strip()]
        else:
            targets = [dst]
        for target in targets:
            if not valid_name(target) and not parse_axis_ref(target) and not parse_line_ref(target):
                continue
            write_ref(model, cyc, target, sv, op=op)
            if op in ("->", "->|"): remove_ref(model, cyc, src)
            log(f"[apply]   {src!r} -> {target!r} = {sv!r}", "DEBUG")
    log(f"[apply] mem after={mem}", "DEBUG")

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
        if i == 0 and cyc.get("has_agent"):
            continue
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
                    log(f"[flush] line {i}: {new!r}", "DEBUG")

def _exec_action_ast(model, cyc, node, bridge=None):
    srcs, ops, dsts, evals = node.srcs, node.ops, node.dsts, node.evals
    for i, op in enumerate(ops):
        if i == 0:
            src_node = srcs[0] if srcs else None
        else:
            src_node = dsts[i-1] if i-1 < len(dsts) else None
        dst_node = dsts[i] if i < len(dsts) else None
        if op == "^":
            if dst_node: do_jump(model, cyc, _ref_to_str(dst_node))
            continue
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

def execute_line(model, cyc, target_idx, bridge=None):
    line = cyc["lines"][target_idx]
    typ, node = resolve_line(line)
    log(f"[execute_line] idx={target_idx} line={line!r} typ={typ}", "DEBUG")
    if typ == "named":
        mem = model["memory"].setdefault(cyc["name"], {})
        if isinstance(node, NamedNode):
            val = unescape_nl(unescape_after_parse(node.val))
            if val == "":
                collected = []
                for j in range(target_idx - 1, -1, -1):
                    if cyc.get("has_agent") and j == 0:
                        break
                    ln_j = cyc["lines"][j]
                    t2, n2 = resolve_line(ln_j)
                    if t2 == "container":
                        text = n2.text if isinstance(n2, ContainerNode) else ln_j
                        collected.insert(0, text)
                    elif t2 in ("separator", "named", "condition", "action", "jump"):
                        break
                val = "\n".join(collected)
            for n in node.names:
                if valid_name(n): mem[n] = val
        elif hasattr(node, "group"):
            val_raw = unescape_after_parse(escape_for_parse(node.group("val")))
            val = unescape_nl(val_raw)
            names_raw = unescape_after_parse(escape_for_parse(node.group("names")))
            for n in re.split(r'[,\s]+', names_raw):
                if n and valid_name(n): mem[n] = val
        _invalidate_name_index(model, cyc["name"])
        log(f"[execute_line] named -> mem={mem}", "DEBUG")
    elif typ == "condition":
        mem = model["memory"].setdefault(cyc["name"], {})
        fired = False
        if isinstance(node, ConditionNode):
            cond_str = node.cond.value if hasattr(node.cond, "value") else str(node.cond)
            if entails(cond_str, mem) and node.act:
                _exec_action_ast(model, cyc, node.act, bridge)
                fired = True
        elif hasattr(node, "group"):
            cond = node.group("cond").strip()
            act = node.group("act").strip()
            if entails(cond, mem) and act:
                exec_action(model, cyc, act, bridge)
                fired = True
        if fired:
            j = target_idx + 1
            while j < len(cyc["lines"]):
                t2, _ = resolve_line(cyc["lines"][j])
                if t2 == "separator":
                    break
                execute_line(model, cyc, j, bridge)
                j += 1
    elif typ == "jump":
        if isinstance(node, JumpNode): do_jump(model, cyc, node.target)
        elif hasattr(node, "group"): do_jump(model, cyc, node.group("target"))
    elif typ == "action":
        if isinstance(node, ActionNode): _exec_action_ast(model, cyc, node, bridge)
        else: exec_action(model, cyc, line, bridge)
    elif typ == "version": pass
    elif typ == "container":
        text = node.text if isinstance(node, ContainerNode) else line
        mem = model["memory"].setdefault(cyc["name"], {})
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
                    if primary in mem:
                        mem[primary] += "\n" + text; break
            elif t2 == "separator": break
        log(f"[execute_line] container -> mem={mem}", "DEBUG")
    return typ

def step_engine(model, bridge=None):
    event = {"kind": None, "cycle": None, "old": {}, "new": {}}
    if not model["cycles"]: return event
    cyc = model["cycles"][model["cur"]]
    event["cycle"] = cyc["name"]
    lines = cyc["lines"]; a = cyc.get("agent_pos", 0)
    log(f"[step] cycle={cyc['name']!r} agent_pos={a} target={a+1} lines={lines}", "DEBUG")
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
            log(f"[step] END", "DEBUG")
            return event
        event["kind"] = "rotate"
        cyc["agent_pos"] = 0
        event["new"] = {"agent_pos": 0, "lines": lines[:]}
        _invalidate_name_index(model, cyc["name"])
        log(f"[step] ROTATE -> agent_pos=0", "DEBUG")
        return event
    old_mem = dict(model["memory"].setdefault(cyc["name"], {}))
    old_lines = lines[:]; old_agent = a
    if target == 0:
        typ_target = "agent"
        log(f"[step] target=0 -> agent line (skip)", "DEBUG")
    else:
        typ_target = execute_line(model, cyc, target, bridge)
        log(f"[step] execute_line({target}) -> {typ_target}", "DEBUG")
    if typ_target == "jump":
        event["kind"] = "jump"
        event["old"] = {"agent_pos": old_agent, "mem": old_mem}
        event["new"] = {"agent_pos": cyc.get("agent_pos", 0), "mem": dict(model["memory"][cyc["name"]])}
        log(f"[step] JUMP -> agent_pos={cyc.get('agent_pos')}", "DEBUG")
        return event
    if typ_target == "condition":
        j = target + 1
        while j < len(cyc["lines"]):
            t2, _ = resolve_line(cyc["lines"][j])
            if t2 == "separator":
                break
            j += 1
        target = j
    dirty = model.get("dirty", set())
    dirty.add(cyc["name"])
    for name in list(dirty):
        for c in model["cycles"]:
            if c["name"] == name: flush_memory_to_lines(c, model)
    model["dirty"] = set()
    cyc["agent_pos"] = target
    model["step_count"] = model.get("step_count", 0) + 1
    event["kind"] = "step"
    event["old"] = {"agent_pos": old_agent, "mem": old_mem, "lines": old_lines}
    event["new"] = {"agent_pos": target, "mem": dict(model["memory"][cyc["name"]]), "lines": lines[:]}
    log(f"[step] STEP -> agent_pos={target} mem={model['memory'][cyc['name']]}", "DEBUG")
    return event

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