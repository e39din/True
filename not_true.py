# not_true.py — interpreter for !true language
# Version: 0.9.6
import re, math, glob, os
from modules import DEBUG, log, eval_expr, valid_name, apply_op, NOT_TRUE_VERSION

class FnToken:
    __slots__ = ("type", "value", "line")
    def __init__(self, type_, value, line=0):
        self.type = type_; self.value = value; self.line = line
    def __repr__(self):
        return f"FnToken({self.type!r}, {self.value!r})"

FN_ARGS="FN_ARGS"; FN_NAME="FN_NAME"; FN_CHAIN="FN_CHAIN"
FN_OP="FN_OP"; FN_EXT="FN_EXT"; FN_CYCLE="FN_CYCLE"
FN_EXPR="FN_EXPR"; FN_BLANK="FN_BLANK"; FN_COMMENT="FN_COMMENT"
FN_INTERP="FN_INTERP"; FN_ERROR="FN_ERROR"

def _is_name_char(ch): return ch.isalnum() or ch in "._"

INTERP_RE = re.compile(r'\$\{(?P<expr>[^}]*)\}')

def _strip_comment(line):
    depth = 0; i = 0
    while i < len(line):
        if line.startswith("${", i):
            depth += 1; i += 2; continue
        if depth > 0 and line.startswith("}", i):
            depth -= 1; i += 1; continue
        if depth == 0 and line[i] == "#":
            return line[:i]
        i += 1
    return line

def _tokenize_fn_line(line):
    s = _strip_comment(line).strip()
    if not s:
        return FnToken(FN_BLANK, "")
    if s.startswith("#"):
        return FnToken(FN_COMMENT, s[1:].strip())
    if "${" in s:
        log(f"[tokenize_fn] {s!r} -> FN_INTERP")
        return FnToken(FN_INTERP, s)
    if s.startswith("::"):
        rest = s[2:].strip()
        if re.match(r'^[\w.]*cycle\d+$', rest, re.IGNORECASE) or rest.startswith("cycle"):
            log(f"[tokenize_fn] {s!r} -> FN_CYCLE {rest!r}")
            return FnToken(FN_CYCLE, rest)
        if all(_is_name_char(ch) or ch == "!" for ch in rest):
            log(f"[tokenize_fn] {s!r} -> FN_EXT {rest!r}")
            return FnToken(FN_EXT, rest)
    if s.startswith(":") and not s.startswith("::"):
        rest = s[1:].strip()
        if re.match(r'^[\w.]*cycle\d+$', rest, re.IGNORECASE) or rest.startswith("cycle"):
            log(f"[tokenize_fn] {s!r} -> FN_CYCLE {rest!r}")
            return FnToken(FN_CYCLE, rest)
    if "=>" in s:
        log(f"[tokenize_fn] {s!r} -> FN_CHAIN")
        return FnToken(FN_CHAIN, s)
    if "=" in s:
        left, right = s.split("=", 1)
        left = left.strip(); right = right.strip()
        if right == "args":
            if left:
                log(f"[tokenize_fn] {s!r} -> FN_ERROR (default args)")
                return FnToken(FN_ERROR, f"default args not supported: {s}")
            log(f"[tokenize_fn] {s!r} -> FN_ARGS")
            return FnToken(FN_ARGS, "")
        if left == "":
            log(f"[tokenize_fn] {s!r} -> FN_NAME {right!r}")
            return FnToken(FN_NAME, right)
    i = 0
    while i < len(s) and s[i].isspace(): i += 1
    if i < len(s) and s[i] in "+-*/%^":
        op = s[i]
        expr = s[i+1:].strip()
        log(f"[tokenize_fn] {s!r} -> FN_OP {(op, expr)!r}")
        return FnToken(FN_OP, (op, expr))
    log(f"[tokenize_fn] {s!r} -> FN_EXPR")
    return FnToken(FN_EXPR, s)

def _tokenize_fn(text):
    tokens = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        t = _tokenize_fn_line(line)
        t.line = lineno
        tokens.append(t)
    return tokens

class FnFunction:
    def __init__(self, name, args, body):
        self.name = name; self.args = args; self.body = body
    def __repr__(self):
        return f"FnFunction({self.name!r}, args={self.args}, body={self.body})"

def parse_fn_file(text):
    funcs = {}
    cur_name = None; cur_args = {}; cur_body = []
    in_func = False
    for t in _tokenize_fn(text):
        if t.type == FN_COMMENT: continue
        if t.type == FN_ERROR:
            log(f"[parse_fn_file] ERROR {t.value} (line {t.line})")
            in_func = False; cur_name = None; cur_args = {}; cur_body = []
            continue
        if t.type == FN_ARGS:
            if in_func and cur_name is not None:
                funcs[cur_name] = FnFunction(cur_name, cur_args, cur_body)
            cur_name = None; cur_args = {"args": t.value}; cur_body = []
            in_func = True
            continue
        if t.type == FN_NAME:
            if in_func:
                funcs[t.value] = FnFunction(t.value, cur_args, cur_body)
                log(f"[parse_fn_file] func {t.value!r} body={[x.type for x in cur_body]}")
            in_func = False; cur_name = None; cur_args = {}; cur_body = []
            continue
        if t.type == FN_BLANK:
            if in_func and cur_body:
                cur_body.append(t)
            continue
        if in_func and t.type in (FN_CHAIN, FN_OP, FN_EXT, FN_CYCLE, FN_EXPR, FN_INTERP):
            cur_body.append(t)
    log(f"[parse_fn_file] funcs={list(funcs)}")
    return funcs

def _eval_interp(text, mem, funcs, ctx, depth=0):
    def repl(m):
        expr = m.group("expr").strip()
        if not expr: return ""
        if expr.startswith("=>"):
            fname = expr[2:].strip()
            r = call_fn(fname, [], funcs, ctx, depth + 1)
            return "" if r is None else str(r)
        if expr in funcs:
            r = call_fn(expr, [], funcs, ctx, depth + 1)
            return "" if r is None else str(r)
        return str(eval_expr(expr, mem))
    r = INTERP_RE.sub(repl, text)
    log(f"[interp] {text!r} -> {r!r}")
    return r

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

def call_fn(name, args, funcs, ctx=None, depth=0):
    log(f"[call_fn] {name} args={args} depth={depth}")
    if depth > 10000: return None
    if name.startswith("::!"):
        return call_fn(name[3:], args, funcs, ctx, depth)
    if name.startswith("::"):
        return _call_extension(name[2:], args[0] if args else None, ctx, depth)
    if name in funcs:
        f = funcs[name]
        local = {"args": ""}
        for i, a in enumerate(args):
            local[f"arg{i+1}"] = a
            if i == 0: local["args"] = a
        r = run_fn_body(f.body, local, funcs, ctx, depth)
        log(f"[call_fn] {name} -> {r!r} local={local}")
        return r
    if ctx and "call_simple_fn" in ctx:
        return ctx["call_simple_fn"](name, args)
    log(f"[call_fn] {name} NOT FOUND")
    return None

def _run_cycle(name, ctx):
    if ctx and "run_cycle_fn" in ctx:
        try:
            ok = ctx["run_cycle_fn"](name)
            return "1" if ok else "0"
        except Exception:
            return "0"
    return "0"

def run_fn_body(body, mem, funcs, ctx=None, depth=0):
    if depth > 10000: return None
    stack = []
    log(f"[run_fn_body] body={[t.type for t in body]} mem={mem}")
    for idx, t in enumerate(body):
        if t.type == FN_BLANK:
            if idx == len(body) - 1:
                log(f"[run_fn_body] trailing FN_BLANK ignored")
                continue
            log(f"[run_fn_body] FN_BLANK reset stack")
            stack = []
            continue
        if t.type == FN_CHAIN:
            line = t.value
            parts = line.split("=>")
            if len(parts) < 2: continue
            srcs_str = parts[0].strip()
            chain = [p.strip() for p in parts[1:] if p.strip()]
            srcs = [s.strip() for s in srcs_str.split(",") if s.strip()]
            if srcs:
                args = [eval_expr(s, mem) for s in srcs]
            elif stack:
                args = [stack[-1]]
            else:
                args = []
            log(f"[run_fn_body] FN_CHAIN srcs={srcs} chain={chain} args={args}")
            r = None
            for fname in chain:
                if fname.startswith("::!"):
                    r = call_fn(fname, args if r is None else [r], funcs, ctx, depth+1)
                elif re.match(r'^:[\w.]*cycle\d+$', fname, re.IGNORECASE):
                    r = _run_cycle(fname[1:], ctx)
                elif fname.startswith("::"):
                    r = _call_extension(fname[2:], args[0] if args else None, ctx, depth+1)
                else:
                    r = call_fn(fname, args if r is None else [r], funcs, ctx, depth+1)
                args = [r]
            if r is not None: stack.append(r)
            continue
        if t.type == FN_OP:
            op, expr = t.value
            if not stack:
                stack.append(mem.get("args", ""))
                log(f"[run_fn_body] FN_OP empty stack -> base {stack[-1]!r}")
            prev = stack.pop()
            right = eval_expr(expr, mem)
            v = apply_op(prev, op, right)
            stack.append(v)
            log(f"[run_fn_body] FN_OP {prev!r} {op} {right!r} = {v!r}")
            continue
        if t.type == FN_EXT:
            ext_name = t.value
            v = stack[-1] if stack else None
            r = _call_extension(ext_name, v, ctx, depth+1)
            if stack: stack.pop()
            if stack or r is not None:
                stack.append(r if r is not None else v)
            log(f"[run_fn_body] FN_EXT {ext_name!r} v={v!r} -> {r!r}")
            continue
        if t.type == FN_CYCLE:
            cycle_name = t.value
            r = _run_cycle(cycle_name, ctx)
            stack.append(r)
            log(f"[run_fn_body] FN_CYCLE {cycle_name!r} -> {r!r}")
            continue
        if t.type == FN_INTERP:
            v = _eval_interp(t.value, mem, funcs, ctx, depth)
            stack.append(v)
            continue
        if t.type == FN_EXPR:
            v = eval_expr(t.value, mem)
            if v == t.value and "+" in t.value:
                parts = [p.strip() for p in t.value.split("+")]
                v = "".join(eval_expr(p, mem) for p in parts)
                log(f"[run_fn_body] FN_EXPR fallback concat {t.value!r} -> {v!r}")
            log(f"[run_fn_body] FN_EXPR {t.value!r} -> {v!r}")
            stack.append(v)
            continue
    log(f"[run_fn_body] return {stack[-1] if stack else None!r} stack={stack}")
    return stack[-1] if stack else None

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
    log(f"[ext_true] {fname} -> {r!r}")
    return True

def load_all_fns(model, base_dir):
    funcs = {}
    for path in glob.glob(os.path.join(base_dir, "*.fn")):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            funcs.update(parse_fn_file(text))
        except Exception: pass
    model["functions"] = funcs
    log(f"[load_all_fns] {list(funcs)}")
    return funcs