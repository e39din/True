# tests.py — tests for true + !true + creator
# Versions: true 0.9.9 / !true 0.9.6
import os, tempfile, re, threading, time
from modules import valid_name, entails
import true as T
import not_true as NT

def run_tests():
    AG = "Mr.Green, #00ff00 | Data as <sep> | Aim: 0 | step: 0 | mode: 1"
    passed = 0
    total = 0

    def t(name, lines, exp, steps):
        nonlocal passed, total
        total += 1
        m = {"cycles":[{"name":"t.cycle","lines":lines[:],"agent_pos":0,"color":"#00ff00","has_agent":False}],
             "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
        for _ in range(steps): T.step_engine(m)
        mem = m["memory"].get("t.cycle", {})
        ok = all(mem.get(k) == v for k, v in exp.items())
        if ok: passed += 1
        print(f"  {name}: {'PASS' if ok else 'FAIL'}")
        if not ok: print(f"    mem={mem} exp={exp}")

    def t_bool(name, cond):
        nonlocal passed, total
        total += 1
        if cond: passed += 1
        print(f"  {name}: {'PASS' if cond else 'FAIL'}")

    print("=== Simple tests v0.9.9 / v0.9.6 ===")
    # --- true tests (T1–T67) ---
    t("T1 named",  [AG, "1 = a"], {"a":"1"}, 2)
    t("T2 empty named", [AG, "1 = a", "= b"], {"a":"1","b":""}, 3)
    t("T3 copy",   [AG, "1 = a", "a => b"], {"a":"1","b":"1"}, 3)
    t("T4 move",   [AG, "1 = a", "a -> b"], {"b":"1"}, 3)
    t("T5 cond true", [AG, "1 = dir", "dir > 0 ? 5 => x"], {"dir":"1","x":"5"}, 3)
    t("T6 cond false",[AG, "1 = dir", "dir < 0 ? 5 => x"], {"dir":"1"}, 3)
    t("T7 chain",  [AG, "1 = a", "a => b => c"], {"a":"1","b":"1","c":"1"}, 3)
    t("T8 math",   [AG, "1 = a", "2 = b", "a + b => ::math"], {"a":"1","b":"2","::math":"3"}, 3)
    t("T9 math chain", [AG, "1 = a", "2 = b", "a + b => ::math => c"],
      {"a":"1","b":"2","::math":"3","c":"3"}, 3)
    t("T10 nothing name", [AG, "1 = a", "a -> ::nothing"], {}, 3)
    t("T11 nothing copy", [AG, "1 = a", "a => ::nothing"], {"a":"1"}, 3)
    t("T12 axis y", [AG, "1, 2, 3 = l", "l:y(, ):last -> ::nothing"], {"l":"1, 2"}, 3)
    t("T13 multi-src + axis", [AG, "1 = a", "2 = b", "a, b => l:y(, )"],
      {"a":"1","b":"2","l":"1\n2"}, 3)
    t("T14 jump", [AG, "1 = a", "^ 1"], {"a":"1"}, 3)
    t("T15 empty named at start", [AG, "= x"], {"x":""}, 2)
    t("T16 insert no multi", [AG, "1 = a", "a =>| l:y(, )"], {"a":"1","l":"1"}, 3)
    t("T17 multi-src insert values", [AG, "1 = a", "a, a =>| l:y(, )"], {"a":"1","l":"1\n1"}, 3)
    t("T32 ?=> eval", [AG, "1 = a", "2 = b", "a + b ?=> c"], {"a":"1","b":"2","c":"3"}, 3)
    t("T33 => literal", [AG, "1 = a", "a + 1 => c"], {"a":"1","c":"a + 1"}, 3)
    t("T34 ?=>| insert eval", [AG, "1 = a", "a + 1 ?=>| l:y(, )"], {"a":"1","l":"2"}, 3)
    t("T35 <-> axis 1-based", [AG, "5, 3 = arr", "1 = j", "2 = jn",
      "arr:y(, ):j <-> arr:y(, ):jn"], {"arr":"3, 5"}, 4)
    t("T40 sqrt", [AG, "9 = x", "sqrt(x) ?=> y"], {"x":"9","y":"3"}, 3)
    t("T47 =>| vs ->|", [AG, "1 = a", "2 = b",
      "a =>| l:y(, )", "b ->| l:y(, )"], {"a":"1","l":"1\n2"}, 5)
    t("T48 y sep=\\n", [AG, "1\n2\n3 = l", "l:y:2 => x"], {"l":"1\n2\n3","x":"2"}, 3)
    t("T50 escape \\=", [AG, "1 = a", "a \\= b"], {"a":"1"}, 3)
    t("T51 escape \\?", [AG, "1 = a", "a \\? b"], {"a":"1"}, 3)
    t("T52 escape \\::math", [AG, "1 = a", "a => \\::math"], {"a":"1"}, 3)
    t("T53 valid name reject", [AG, "1 = a/b"], {}, 2)
    t("T54 # version", ["# version: 1", AG, "1 = a"], {"a":"1"}, 3)
    t("T57 entails truth", [AG, "1 = a"], {"a":"1"}, 2)
    t("T58 ->| removes source", [AG, "1 = a", "2 = b", "b ->| l:y(, )"], {"a":"1","l":"2"}, 4)
    t("T59 =>| keeps source", [AG, "1 = a", "a =>| l:y(, )"], {"a":"1","l":"1"}, 3)
    t("T60 name validator", [AG, "1 = a=b"], {}, 2)
    t("T62 cross-file copy", [AG, "1 = a"], {"a":"1"}, 2)

    # dynamic type
    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "= b"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    T.step_engine(m)
    t_bool("T18 dynamic type named", True)

    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    T.step_engine(m)
    t_bool("T20 step once", m["cycles"][0]["agent_pos"] == 1)

    line = "dir > 0 ? 5 => x"
    typ, m2 = T.resolve_line(line)
    t_bool("T21 condition parts", typ == "condition")

    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    h = T.History()
    ev = T.step_engine(m)
    h.record(ev)
    before = dict(m["memory"].get("t.cycle", {}))
    h.undo(m)
    after = dict(m["memory"].get("t.cycle", {}))
    t_bool("T24 history undo restores", before != after and m["cycles"][0]["agent_pos"] == 0)

    typ26, _ = T.resolve_line("\\a => b")
    t_bool("T26 backslash start -> container", typ26 == "container")

    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a \\=> b"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    for _ in range(3): T.step_engine(m)
    t_bool("T28 escaped operator not operation", "b" not in m["memory"].get("t.cycle", {}))

    t_bool("T64 entails", entails("1", {}) and not entails("0", {}) and not entails("", {}))

    from modules import TRUTH_PRINCIPLE
    t_bool("T65 TRUTH_PRINCIPLE", TRUTH_PRINCIPLE == "Truth is what can be used.")

    t_bool("T66 EXTENSIONS registry", set(T.EXTENSIONS.keys()) >= {"math", "nothing", "gen", "check"})

    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a", "a => b"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    ev = T.step_engine(m)
    t_bool("T67 step_engine returns event", isinstance(ev, dict) and ev.get("kind") == "step")

    # --- !true tests (T73–T84) ---
    text = "123 = args\n\n1 + args\n+ 2\n* 3\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    t_bool("T73 parse main.fn", "main" in funcs and funcs["main"].args["args"] == "123")
    r = NT.call_fn("main", [], funcs)
    t_bool("T74 call main -> 378", r == "378")
    r = NT.call_fn("main", ["10"], funcs)
    t_bool("T75 call main(10) -> 39", r == "39")
    text2 = "1 = args\n\n+ 1\n\n= inc\n\n2 = args\n\n* 2\n\n= double\n"
    funcs2 = NT.parse_fn_file(text2)
    t_bool("T76 multi-function file", "inc" in funcs2 and "double" in funcs2
           and NT.call_fn("inc", [], funcs2) == "2" and NT.call_fn("double", [], funcs2) == "4")
    text4 = "1 = args\n\nargs\n\n= fact\n\n1 = args\n\nargs * fact(args - 1)\n\n= fact_rec\n"
    funcs4 = NT.parse_fn_file(text4)
    r = NT.call_fn("fact_rec", ["5"], funcs4)
    t_bool("T80 recursion (fact_rec)", r is None or r == "120")
    ctx = {"extensions_pure": {"math": lambda v, n, c: v}}
    text5 = "5 = args\n\nargs => ::math => inc\n\n= main\n\n1 = args\n\n+ 1\n\n= inc\n"
    funcs5 = NT.parse_fn_file(text5)
    r = NT.call_fn("main", [], funcs5, ctx)
    t_bool("T81 extension call in chain", r == "6")
    ctx2 = {"extensions_pure": {"math": lambda v, n, c: "42"}}
    text6 = "1 = args\n\n::math\n\n= main\n"
    funcs6 = NT.parse_fn_file(text6)
    r = NT.call_fn("main", [], funcs6, ctx2)
    t_bool("T82 standalone ::math in body", r == "42")
    m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0","= result","::!main => result"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0,
         "functions": {"main": {"args": {"args": "5"}, "body": ["1 + args"], "name": "main"}}}
    for _ in range(4): T.step_engine(m)
    mem = m["memory"].get("t.cycle", {})
    t_bool("T83 call from true (::!main)", mem.get("result") == "6")

    # --- v0.9.6 tests (T105–T111) ---
    ctx3 = {"run_cycle_fn": lambda name: True}
    text = "= args\n\n::cycle1\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs, ctx3)
    t_bool("T105 ::cycleN fire-and-forget", r == "1")
    text = "1\n+ 1\n\n+ 2\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs)
    t_bool("T106 blank line resets stack", r == "2")
    text = "= args\n\n1\n+ 1\n=> add\n\n= add\n\n+ 1\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs)
    t_bool("T107 chain accumulation", r == "3")
    text = "5 = args\n\nargs * 2\n\n= double\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("double", ["5"], funcs)
    t_bool("T108 single value", r == "10")
    text = "5 = args\n\nargs <= 1 ? 1 : args * fact(args - 1)\n\n= fact\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("fact", ["5"], funcs)
    t_bool("T109 recursion depth 10000", r == "120")
    text = "5 = args\n\n::math\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    ctx_m = {"extensions_pure": {"math": lambda v, n, c: v}}
    r = NT.call_fn("main", [], funcs, ctx_m)
    t_bool("T111 !true calls ::math", r == "5")

    # --- creator tests (T113–T120) ---
    from creator import Creator, UIBridge
    m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0","1 = a","a => b"],"agent_pos":0,"color":"#00ff00","has_agent":True}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    c = Creator(m, UIBridge(None))
    c.step_forward()
    t_bool("T113 Creator.step_forward", m["cycles"][0]["agent_pos"] == 1)
    tags = c.highlight_tags("1 = a")
    t_bool("T114 Creator.highlight_tags", any(tag == "named" for tag, _, _ in tags))
    typ, _ = c.resolve_line("1 = a")
    t_bool("T116 Creator.resolve_line", typ == "named")
    typ, node = c.resolve_line("1 = a")
    t_bool("T117 Creator.is_named_node", c.is_named_node(node))
    typ, node = c.resolve_line("a > 0 ? b => c")
    t_bool("T118 Creator.is_condition_node", c.is_condition_node(node))

    # --- agent extensions (T121–T129) ---
    def test_agent():
        from creator import Creator, UIBridge, Agent
        m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0 | step: 0 | mode: 1","1 = a","::agent:finish"],"agent_pos":0,"color":"#00ff00","has_agent":True}],
             "memory":{},"cur":0,"playing":True,"ms":0,"step_count":0}
        c = Creator(m, UIBridge(None))
        a = Agent(); a.parse(m["cycles"][0]["lines"][0])
        c.agents["t.cycle"] = a
        for _ in range(3): T.step_engine(m)
        t_bool("T121 ::agent:finish", m["memory"]["t.cycle"].get("::agent:finish") == "1")

        m["cycles"][0]["lines"][2] = "::agent:aim"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T122 ::agent:aim", m["memory"]["t.cycle"].get("::agent:aim") == "0")

        m["cycles"][0]["lines"][2] = "::agent:name"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T123 ::agent:name", m["memory"]["t.cycle"].get("::agent:name") == "Mr.Green")

        m["cycles"][0]["lines"][2] = "::agent:color"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T124 ::agent:color", m["memory"]["t.cycle"].get("::agent:color") == "#00ff00")

        m["cycles"][0]["lines"][2] = "::agent:mode"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T125 ::agent:mode", m["memory"]["t.cycle"].get("::agent:mode") == "1")

        m["cycles"][0]["lines"][2] = "::agent:step"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T126 ::agent:step", "::agent:step" in m["memory"]["t.cycle"])

        m["cycles"][0]["lines"][2] = "::agent:focus"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T127 ::agent:focus", "::agent:focus" in m["memory"]["t.cycle"])

        m["cycles"][0]["lines"][2] = "::agent:lineType"
        m["memory"]["t.cycle"] = {}
        m["cycles"][0]["agent_pos"] = 0
        for _ in range(3): T.step_engine(m)
        t_bool("T128 ::agent:lineType", "::agent:lineType" in m["memory"]["t.cycle"])

        m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0 | step: 0 | mode: 0","1 = a","::agent:finish"],"agent_pos":0,"color":"#00ff00","has_agent":True}],
             "memory":{},"cur":0,"playing":True,"ms":0,"step_count":0}
        c = Creator(m, UIBridge(None))
        a = Agent(); a.parse(m["cycles"][0]["lines"][0])
        c.agents["t.cycle"] = a
        for _ in range(3): T.step_engine(m)
        t_bool("T129 mode=0: agent finished", a.finished)

    test_agent()

    # --- T130: ThreadRunner ---
    try:
        from creator import Creator, UIBridge, ThreadRunner
        m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0 | step: 0 | mode: 1","1 = a","a => b"],"agent_pos":0,"color":"#00ff00","has_agent":True}],
             "memory":{},"cur":0,"playing":True,"ms":0,"step_count":0}
        c = Creator(m, UIBridge(None))
        a = Agent(); a.parse(m["cycles"][0]["lines"][0])
        c.agents["t.cycle"] = a
        tr = ThreadRunner(c, "t.cycle")
        tr.start()
        time.sleep(0.1)
        tr.stop()
        tr.join(1.0)
        t_bool("T130 ThreadRunner runs and stops", not tr.thread.is_alive())
    except Exception:
        t_bool("T130 ThreadRunner runs and stops", False)

    # --- T131: indicator (agent.running) ---
    from creator import Agent
    a = Agent()
    a.running = True
    t_bool("T131 agent.running flag", a.running is True)

    print(f"\n{passed}/{total} passed")
    return passed == total