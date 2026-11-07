# not_true.py — interpreter for !true language
# Version: 0.9.6
# Changes: no tuples; ::cycleN; blank line resets stack; chain accumulates; guard 10000
import re, math, glob, os
from modules import DEBUG, log, eval_expr, valid_name, apply_op, NOT_TRUE_VERSION

# ===== LEXER =====
class FnToken:
    __slots__ = ("type", "value", "line")
    def __init__(self, type_, value, line=0):
        self.type = type_; self.value = value; self.line = line
    def __repr__(self):
        return f"FnToken({self.type!r}, {self.value!r})"

FN_ARGS="FN_ARGS"; FN_NAME="FN_NAME"; FN_CHAIN="FN_CHAIN"
FN_OP="FN_OP"; FN_EXT="FN_EXT"; FN_CYCLE="FN_CYCLE"
FN_EXPR="FN_EXPR"; FN_BLANK="FN_BLANK"; FN_COMMENT="FN_COMMENT"

def _is_name_char(ch): return ch.isalnum() or ch in "._"

def _tokenize_fn_line(line):
    s = line.strip()
    if not s: return FnToken(FN_BLANK, "")
    if s.startswith("#"): return FnToken(FN_COMMENT, s[1:].strip())
    if s.startswith("::"):
        rest = s[2:].strip()
        if re.match(r'^[\w.]*cycle\d+$', rest, re.IGNORECASE) or rest.startswith("cycle"):
            return FnToken(FN_CYCLE, rest)
        if all(_is_name_char(ch) or ch == "!" for ch in rest):
            return FnToken(FN_EXT, rest)
    if "=" in s:
        left, right = s.split("=", 1)
        left = left.strip(); right = right.strip()
        if right == "args": return FnToken(FN_ARGS, left)
        if left == "": return FnToken(FN_NAME, right)
    if "=>" in s: return FnToken(FN_CHAIN, s)
    i = 0
    while i < len(s) and s[i].isspace(): i += 1
    if i < len(s) and s[i] in "+-*/%^":
        op = s[i]
        expr = s[i+1:].strip()
        return FnToken(FN_OP, (op, expr))
    return FnToken(FN_EXPR, s)

def _tokenize_fn(text):
    tokens = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        t = _tokenize_fn_line(line)
        t.line = lineno
        tokens.append(t)
    return tokens

# ===== PARSER =====
class FnFunction:
    def __init__(self, name, args, body):
        self.name = name; self.args = args; self.body = body
    def __repr__(self):
        return f"FnFunction({self.name!r}, args={self.args}, body={self.body})"

def parse_fn_file(text):
    funcs = {}
    cur_name = None; cur_args = {}; cur_body = []
    for t in _tokenize_fn(text):
        if t.type == FN_COMMENT: continue
        if t.type == FN_BLANK:
            if cur_name is not None:
                cur_body.append(t)
            continue
        if t.type == FN_ARGS:
            if cur_name is not None:
                funcs[cur_name] = FnFunction(cur_name, cur_args, cur_body)
                cur_name = None; cur_args = {}; cur_body = []
            cur_args["args"] = t.value
            continue
        if t.type == FN_NAME:
            if cur_name is not None:
                funcs[cur_name] = FnFunction(cur_name, cur_args, cur_body)
                cur_name = t.value; cur_args = {}; cur_body = []
            else:
                cur_name = t.value
            continue
        if cur_name is None: continue
        if t.type in (FN_CHAIN, FN_OP, FN_EXT, FN_CYCLE, FN_EXPR):
            cur_body.append(t)
    if cur_name is not None:
        funcs[cur_name] = FnFunction(cur_name, cur_args, cur_body)
    return funcs

# ===== EXTENSION CALL =====
def _call_extension(name, value, ctx, depth=0):
    if not ctx: return None
    if "extensions_pure" in ctx:
        pure_fn = ctx["extensions_pure"].get(name)
        if pure_fn:
            try: return pure_fn(value, name, ctx)
            except Exception: return None
    if "extensions" in ctx:
        fn = ctx["extensions"].get(name)
        if fn:
            model = ctx.get("model")
            if model:
                cyc = model["cycles"][model["cur"]] if model.get("cycles") else None
                if cyc:
                    try:
                        fn(model, cyc, value if value is not None else "", "::" + name, "=>", False, None)
                        mem = model["memory"].setdefault(cyc["name"], {})
                        return mem.get("::" + name, mem.get(name))
                    except Exception:
                        return None
    return None

# ===== CALL FN =====
def call_fn(name, args, funcs, ctx=None, depth=0):
    if depth > 10000: return None
    if name.startswith("::!"):
        fname = name[3:]
        return call_fn(fname, args, funcs, ctx, depth)
    if name.startswith("::"):
        ext_name = name[2:]
        v = args[0] if args else None
        return _call_extension(ext_name, v, ctx, depth)
    if name in funcs:
        f = funcs[name]
        local = dict(f.args)
        for i, a in enumerate(args):
            local[f"arg{i+1}"] = a
            if i == 0: local["args"] = a
        return run_fn_body(f.body, local, funcs, ctx, depth)
    if ctx and "call_simple_fn" in ctx:
        return ctx["call_simple_fn"](name, args)
    return None

def _run_cycle(name, ctx):
    if ctx and "run_cycle_fn" in ctx:
        try:
            ok = ctx["run_cycle_fn"](name)
            return "1" if ok else "0"
        except Exception:
            return "0"
    return "0"

# ===== RUN BODY =====
def run_fn_body(body, mem, funcs, ctx=None, depth=0):
    if depth > 10000: return None
    stack = []
    for t in body:
        if t.type == FN_BLANK:
            stack = []
            continue
        if t.type == FN_CHAIN:
            line = t.value
            parts = line.split("=>")
            if len(parts) < 2: continue
            srcs_str = parts[0].strip()
            chain = [p.strip() for p in parts[1:] if p.strip()]
            srcs = [s.strip() for s in srcs_str.split(",") if s.strip()]
            args = [eval_expr(s, mem) for s in srcs]
            r = None
            for fname in chain:
                if fname.startswith("::!"):
                    r = call_fn(fname, args if r is None else [r], funcs, ctx, depth+1)
                elif re.match(r'^::[\w.]*cycle\d+$', fname, re.IGNORECASE):
                    r = _run_cycle(fname[2:], ctx)
                elif fname.startswith("::"):
                    r = _call_extension(fname[2:], args[0] if args else None, ctx, depth+1)
                else:
                    r = call_fn(fname, args if r is None else [r], funcs, ctx, depth+1)
                args = [r]
            if r is not None: stack.append(r)
            continue
        if t.type == FN_OP:
            op, expr = t.value
            if not stack: continue
            prev = stack.pop()
            right = eval_expr(expr, mem)
            stack.append(apply_op(prev, op, right))
            continue
        if t.type == FN_EXT:
            ext_name = t.value
            v = stack[-1] if stack else None
            r = _call_extension(ext_name, v, ctx, depth+1)
            if stack: stack.pop()
            if r is not None: stack.append(r)
            continue
        if t.type == FN_CYCLE:
            cycle_name = t.value
            r = _run_cycle(cycle_name, ctx)
            stack.append(r)
            continue
        if t.type == FN_EXPR:
            v = eval_expr(t.value, mem)
            stack.append(v)
    return stack[-1] if stack else None

# ===== INTEGRATION WITH TRUE =====
def ext_true(model, cyc, src, dst, op, eval_flag, bridge, ctx=None):
    fname = None
    if dst.startswith("::!"): fname = dst[3:]
    elif dst.endswith(".fn"):
        base = dst.split(":")[-1] if ":" in dst else dst
        fname = base[:-3] if base.endswith(".fn") else base
    else: return False
    funcs = model.get("functions", {})
    if fname not in funcs: return False
    mem = model["memory"].setdefault(cyc["name"], {})
    args = []
    if src:
        v = mem.get(src, src)
        args = [v]
    r = call_fn(fname, args, funcs, ctx)
    mem["::!" + fname] = r if r is not None else ""
    mem[fname] = r if r is not None else ""
    return True

# ===== LOAD ALL FNS =====
def load_all_fns(model, base_dir):
    funcs = {}
    for path in glob.glob(os.path.join(base_dir, "*.fn")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            funcs.update(parse_fn_file(text))
        except Exception: pass
    model["functions"] = funcs
    return funcs