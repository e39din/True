# creator.py — heart of the system
# Version: true 0.9.9 / !true 0.9.6
import re, os, glob, threading, time
from modules import (
    PHI, DEBUG, ESC_NL, ESC_CHAR, PH_OPEN, PH_CLOSE, HISTORY_MAX,
    TRUTH_PRINCIPLE, CORE_PRINCIPLE, TRUE_VERSION, NOT_TRUE_VERSION,
    log, set_log_fh,
    valid_name, entails, eval_expr, parse_ref,
    read_ref, write_ref, mem_of,
)
import true as T
import not_true as NT

class UIBridge:
    def __init__(s, app):
        s.app = app
    def play(s):
        if s.app and hasattr(s.app, "toggle"): s.app.toggle()
    def pause(s):
        if s.app and hasattr(s.app, "pause"): s.app.pause()
    def step(s):
        if s.app and hasattr(s.app, "step_forward"): s.app.step_forward()
    def step_back(s):
        if s.app and hasattr(s.app, "step_back"): s.app.step_back()
    def reset(s):
        if s.app and hasattr(s.app, "reset"): s.app.reset()
    def new(s, name):
        if s.app and hasattr(s.app, "add_editor"): s.app.add_editor(name)
    def open(s, path):
        if s.app and hasattr(s.app, "open_path"): s.app.open_path(path)
    def save(s):
        if s.app and hasattr(s.app, "save_cycle"): s.app.save_cycle()
    def close(s, name):
        if s.app and hasattr(s.app, "close_cycle"): s.app.close_cycle(name)
    def exit(s):
        if s.app and hasattr(s.app, "exit"): s.app.exit()
    def refresh_ui(s):
        if s.app and hasattr(s.app, "root"):
            s.app.root.after(0, s.app.refresh_ui)
    def call_fn(s, name, args):
        funcs = getattr(s, "model", {}).get("functions", {})
        return NT.call_fn(name, args, funcs)

class Agent:
    def __init__(s, name="Mr.Green", color="#5fb85f", typ="", aim="", step=0, mode=1):
        s.name = name; s.color = color; s.typ = typ
        s.aim = aim; s.step = step; s.mode = mode
        s.focus = ""; s.line_type = ""
        s.finished = False
        s.running = False

    def parse(s, line):
        parts = line.split("|")
        name_color = parts[0].strip()
        if "," not in name_color: return False
        name, color = name_color.split(",", 1)
        color = color.strip()
        if not color.startswith("#") or len(color) != 7: return False
        s.name = name.strip(); s.color = color
        for p in parts[1:]:
            p = p.strip()
            if p.startswith("Data as <"):
                s.typ = p[len("Data as <"):].rstrip(">").strip()
            elif p.startswith("Aim:"):
                aim = p[4:].strip()
                if "|" in aim:
                    aim, rest = aim.split("|", 1)
                    aim = aim.strip(); rest = rest.strip()
                    if rest.startswith("step:"):
                        try: s.step = int(rest[5:].strip())
                        except Exception: pass
                    elif rest.startswith("mode:"):
                        try: s.mode = int(rest[5:].strip())
                        except Exception: pass
                s.aim = aim
            elif p.startswith("step:"):
                try: s.step = int(p[5:].strip())
                except Exception: pass
            elif p.startswith("mode:"):
                try: s.mode = int(p[5:].strip())
                except Exception: pass
        return True

    def to_line(s):
        return (f"{s.name}, {s.color} | Data as <{s.typ}> | "
                f"Aim: {s.aim} | step: {s.step} | mode: {s.mode}")

class ThreadRunner:
    def __init__(s, creator, cycle_name):
        s.creator = creator
        s.cycle_name = cycle_name
        s.stop_flag = threading.Event()
        s.thread = None
        s.lock = threading.Lock()

    def start(s):
        if s.thread and s.thread.is_alive(): return
        s.stop_flag.clear()
        s.thread = threading.Thread(target=s._run, daemon=True)
        s.thread.start()
        log(f"[thread] start {s.cycle_name}")

    def stop(s):
        s.stop_flag.set()
        agent = s.creator.agents.get(s.cycle_name)
        if agent: agent.running = False
        log(f"[thread] stop {s.cycle_name}")

    def join(s, timeout=1.0):
        if s.thread and s.thread.is_alive():
            s.thread.join(timeout)

    def _run(s):
        agent = s.creator.agents.get(s.cycle_name)
        mode = agent.mode if agent else 1
        if agent: agent.running = True
        s.creator.ui.refresh_ui()
        try:
            while not s.stop_flag.is_set():
                with s.creator.lock:
                    if not s.creator.model.get("playing"):
                        break
                if s.stop_flag.is_set(): break
                with s.lock:
                    with s.creator.lock:
                        ev = T.step_engine(s.creator.model, s.creator.ui)
                        s.creator.runner.history.record(ev)
                        ms = s.creator.model.get("ms", 390)
                log(f"[thread] {s.cycle_name} ev.kind={ev.get('kind')}")
                if agent:
                    c = s.creator.model["cycles"][s.creator.model["cur"]]
                    pos = c.get("agent_pos", 0)
                    if 0 <= pos < len(c["lines"]):
                        agent.focus = c["lines"][pos]
                        typ, _ = T.resolve_line(agent.focus)
                        agent.line_type = typ
                        agent.typ = typ
                    agent.step = s.creator.model.get("step_count", 0)
                    if c["lines"] and agent.parse(c["lines"][0]) is not False:
                        c["lines"][0] = agent.to_line()
                s.creator.ui.refresh_ui()
                if mode == 1:
                    if ms > 0: time.sleep(ms / 1000.0)
                else:
                    if agent and agent.finished: break
                    if ev and ev.get("kind") == "end": break
        finally:
            if agent: agent.running = False
            s.creator.ui.refresh_ui()
            log(f"[thread] {s.cycle_name} finished")

class AgentRunner:
    def __init__(s, model, ui_bridge=None):
        s.model = model
        s.ui = ui_bridge
        s.history = T.History()

    def step_forward(s):
        if s.model.get("playing"): s.pause()
        ev = T.step_engine(s.model, s.ui)
        s.history.record(ev)
        log(f"[runner] step_forward kind={ev.get('kind')}")
        return ev

    def step_back(s):
        if s.model.get("playing"): s.pause()
        ev = s.history.undo(s.model)
        log(f"[runner] step_back -> {ev}")
        return ev

    def reset(s):
        s.model["playing"] = False
        for c in s.model["cycles"]:
            c["agent_pos"] = 0
        s.model["memory"].clear()
        s.model["step_count"] = 0
        s.history.clear()
        log(f"[runner] reset")

    def toggle(s):
        s.model["playing"] = not s.model.get("playing", False)
        log(f"[runner] toggle -> playing={s.model['playing']}")
        return s.model["playing"]

class Creator:
    def __init__(s, model, ui_bridge=None):
        s.model = model
        s.ui = ui_bridge or UIBridge(None)
        s.runner = AgentRunner(model, s.ui)
        s.agents = {}
        s.threads = {}
        s.lock = threading.Lock()
        s._register_extensions()

    def _register_extensions(s):
        T.register_extension("agent", s._ext_agent)
        T.register_extension("creator", s._ext_creator)

    def _ext_agent(s, model, cyc, src, dst, op, eval_flag, bridge):
        parts = dst.split(":")
        if len(parts) < 2: return False
        cmd = parts[-1]
        agent = s.agents.get(cyc["name"])
        if not agent: return False
        mem = model["memory"].setdefault(cyc["name"], {})
        if cmd == "finish":
            agent.finished = True
            model["playing"] = False
            s.ui.refresh_ui()
            mem["::agent:finish"] = "1"
        elif cmd == "aim": mem["::agent:aim"] = agent.aim
        elif cmd == "name": mem["::agent:name"] = agent.name
        elif cmd == "color": mem["::agent:color"] = agent.color
        elif cmd == "mode": mem["::agent:mode"] = str(agent.mode)
        elif cmd == "step": mem["::agent:step"] = str(agent.step)
        elif cmd == "focus": mem["::agent:focus"] = agent.focus
        elif cmd == "lineType": mem["::agent:lineType"] = agent.line_type
        log(f"[ext_agent] {cmd} -> mem={mem.get('::agent:'+cmd)}")
        return True

    def _ext_creator(s, model, cyc, src, dst, op, eval_flag, bridge):
        parts = dst.split(":")
        if len(parts) < 2: return False
        cmd = parts[-1]
        if cmd == "play" and not model.get("playing"): s.ui.play()
        elif cmd == "pause": s.ui.pause()
        elif cmd == "step": s.ui.step()
        elif cmd == "stepBack": s.ui.step_back()
        elif cmd == "restart": s.ui.reset()
        elif cmd == "new" and src: s.ui.new(src)
        elif cmd == "open" and src: s.ui.open(src)
        elif cmd == "save": s.ui.save()
        elif cmd == "close" and src:
            s.ui.save(); s.ui.close(src)
        elif cmd == "exit": s.ui.exit()
        log(f"[ext_creator] {cmd}")
        return True

    def _pure_math(s, value, ext_name, ctx):
        mem = {"__v": value if value is not None else ""}
        return eval_expr("__v", mem)
    def _pure_nothing(s, value, ext_name, ctx): return None
    def _pure_bang(s, value, ext_name, ctx):
        name = ext_name[1:] if ext_name.startswith("!") else ext_name
        funcs = ctx.get("model", {}).get("functions", {})
        return NT.call_fn(name, [value], funcs, ctx)

    def _call_simple_fn(s, model, name, args):
        if not model: return None
        for i, c in enumerate(model["cycles"]):
            if c["name"] == name:
                model["cur"] = i
                c["agent_pos"] = 0
                for _ in range(100):
                    T.step_engine(model)
                    if model.get("step_count", 0) == 0: break
                return model["memory"].get(name, {}).get("result", "")
        return None

    def _run_true_cycle(s, model, name):
        for i, c in enumerate(model["cycles"]):
            if c["name"] == name or c["name"] == name + ".cycle":
                c["agent_pos"] = 0
                def _run():
                    for _ in range(1000):
                        if model.get("step_count", 0) == 0: break
                        T.step_engine(model)
                        if c.get("agent_pos", 0) == 0 and model.get("step_count", 0) > 0: break
                t = threading.Thread(target=_run, daemon=True)
                t.start()
                return True
        return False

    def _ext_true_wrapper(s, model, cyc, src, dst, op, eval_flag, bridge):
        ctx = {
            "step_fn": T.step_engine,
            "read_ref_fn": read_ref,
            "write_ref_fn": write_ref,
            "eval_fn": eval_expr,
            "mem_of_fn": mem_of,
            "model": model,
            "extensions": dict(T.EXTENSIONS),
            "extensions_pure": {
                "math": s._pure_math,
                "nothing": s._pure_nothing,
                "!": s._pure_bang,
            },
            "call_simple_fn": lambda name, args: s._call_simple_fn(model, name, args),
            "run_cycle_fn": lambda name: s._run_true_cycle(model, name),
        }
        return NT.ext_true(model, cyc, src, dst, op, eval_flag, bridge, ctx)

    def load_all_fns(s, base_dir):
        return NT.load_all_fns(s.model, base_dir)

    def load_cycle(s, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return False
        name = os.path.basename(path)
        loop = path.endswith(".cycle")
        lines = content.split("\n")
        agent = None
        has_agent = False
        if lines:
            agent = Agent()
            if agent.parse(lines[0]):
                s.agents[name] = agent
                has_agent = True
        s.model["cycles"].append({"name": name, "lines": lines,
                                  "agent_pos": 0, "color": "#5fb85f", "loop": loop,
                                  "has_agent": has_agent})
        log(f"[creator] load_cycle {name} has_agent={has_agent}")
        return True

    def save_cycle(s, name):
        for c in s.model["cycles"]:
            if c["name"] == name:
                path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n".join(c["lines"]))
                    log(f"[creator] save_cycle {name}")
                    return True
                except Exception:
                    return False
        return False

    def list_files(s, directory):
        try: return sorted(os.listdir(directory))
        except Exception: return []
    def read_file(s, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception: return None
    def write_file(s, path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception: return False

    def step_forward(s): return s.runner.step_forward()
    def step_back(s): return s.runner.step_back()
    def reset(s): s.runner.reset()
    def toggle(s):
        playing = s.runner.toggle()
        if playing:
            s.start_all_threads()
        else:
            s.stop_all_threads()
        return playing

    def start_all_threads(s):
        for c in s.model["cycles"]:
            name = c["name"]
            if name not in s.threads:
                s.threads[name] = ThreadRunner(s, name)
            s.threads[name].start()
        s.ui.refresh_ui()

    def stop_all_threads(s):
        for runner in list(s.threads.values()):
            runner.stop()
        for agent in s.agents.values():
            agent.running = False
        for runner in list(s.threads.values()):
            runner.join(timeout=1.0)
        s.threads.clear()

    def play(s): s.ui.play()
    def pause(s): s.ui.pause()
    def step(s): s.ui.step()
    def step_back_ui(s): s.ui.step_back()
    def reset_ui(s): s.ui.reset()
    def new(s, name): s.ui.new(name)
    def open(s, path): s.ui.open(path)
    def save(s): s.ui.save()
    def close(s, name): s.ui.close(name)
    def exit(s): s.ui.exit()

    def resolve_line(s, line): return T.resolve_line(line)
    def is_named_node(s, m): return isinstance(m, T.NamedNode)
    def is_condition_node(s, m): return isinstance(m, T.ConditionNode)

    def highlight_tags(s, line):
        tags = []
        typ, m = T.resolve_line(line)
        if typ == "version":
            tags.append(("version", 0, len(line)))
        elif typ == "condition":
            q = line.find("?")
            if q < 0:
                tags.append(("cond", 0, len(line)))
            else:
                tags.append(("cond", 0, q))
                act_start = q + 1
                while act_start < len(line) and line[act_start] == " ":
                    act_start += 1
                if act_start < len(line):
                    tags.append(("act", act_start, len(line)))
                    for op_m in T.ACTION_OP.finditer(line[act_start:]):
                        tags.append(("op", act_start + op_m.start(), act_start + op_m.end()))
        elif typ == "action":
            tags.append(("action", 0, len(line)))
            for op_m in T.ACTION_OP.finditer(line):
                tags.append(("op", op_m.start(), op_m.end()))
        elif typ in ("named", "jump", "container", "separator"):
            tags.append((typ, 0, len(line)))
        return tags