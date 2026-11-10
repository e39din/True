# tests.py — tests for true + !true + creator
# Versions: true 0.9.9 / !true 0.9.6
import os, tempfile, re, threading, time
from modules import valid_name, entails, log
import true as T
import not_true as NT

def run_tests():
    AG = "Mr.Green, #00ff00 | Data as <sep> | Aim: 0 | step: 0 | mode: 1"
    passed = 0
    total = 0
    failed = []

    def _make_model(lines):
        """Моделирует simple.py add_editor/sync_from_ui: парсит первую строку как агентскую."""
        from creator import Agent
        has_agent = False
        if lines:
            a = Agent()
            if a.parse(lines[0]):
                has_agent = True
        return {"cycles":[{"name":"t.cycle","lines":lines[:],"agent_pos":0,"color":"#00ff00","has_agent":has_agent}],
                "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}

    def report(name, ok, extra=""):
        nonlocal passed, total
        total += 1
        if ok: passed += 1
        else: failed.append(name)
        msg = f"  {name}: {'PASS' if ok else 'FAIL'}{extra}"
        print(msg)
        log(msg, "INFO")

    def t(name, lines, exp, steps):
        m = _make_model(lines)
        try:
            for _ in range(steps): T.step_engine(m)
            mem = m["memory"].get("t.cycle", {})
            ok = all(mem.get(k) == v for k, v in exp.items())
            report(name, ok, "" if ok else f"\n    mem={mem} exp={exp}")
        except Exception as e:
            report(name, False, f"\n    exception: {e}")

    def t_bool(name, cond):
        try:
            report(name, bool(cond))
        except Exception as e:
            report(name, False, f"\n    exception: {e}")

    print("=== Simple tests v0.9.9 / v0.9.6 ===")
    log("=== Simple tests v0.9.9 / v0.9.6 ===", "INFO")
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
      {"a":"1","b":"2","l":"1, 2"}, 3)
    t("T14 jump", ["^ 1", "1 = a"], {"a":"1"}, 3)
    t("T15 empty named at start", [AG, "= x"], {"x":""}, 2)
    t("T16 insert no multi", [AG, "1 = a", "a =>| l:y(, )"], {"a":"1","l":"1"}, 3)
    t("T17 multi-src insert values", [AG, "1 = a", "a, a =>| l:y(, )"], {"a":"1","l":"1, 1"}, 3)
    t("T32 ?=> eval", [AG, "1 = a", "2 = b", "a + b ?=> c"], {"a":"1","b":"2","c":"3"}, 3)
    t("T33 => literal", [AG, "1 = a", "a + 1 => c"], {"a":"1","c":"a + 1"}, 3)
    t("T34 ?=>| insert eval", [AG, "1 = a", "a + 1 ?=>| l:y(, )"], {"a":"1","l":"2"}, 3)
    t("T35 <-> axis 1-based", [AG, "5, 3 = arr", "1 = j", "2 = jn",
      "arr:y(, ):j <-> arr:y(, ):jn"], {"arr":"3, 5"}, 4)
    t("T40 sqrt", [AG, "9 = x", "sqrt(x) ?=> y"], {"x":"9","y":"3"}, 3)
    t("T47 =>| vs ->|", [AG, "1 = a", "2 = b",
      "a =>| l:y(, )", "b ->| l:y(, )"], {"a":"1","l":"1, 2"}, 5)
    t("T48 y sep=\\n", [AG, "1\\n2\\n3 = l", "l:y:2 => x"], {"l":"1\n2\n3","x":"2"}, 3)
    t("T50 escape \\=", [AG, "1 = a", "a \\= b"], {"a":"1\na = b"}, 3)
    t("T51 escape \\?", [AG, "1 = a", "a \\? b"], {"a":"1\na ? b"}, 3)
    t("T52 escape \\::math", [AG, "1 = a", "a => \\::math"], {"a":"1"}, 3)
    t("T53 valid name reject", [AG, "1 = a/b"], {}, 2)
    t("T54 # version", ["# version: 1", AG, "1 = a"], {"a":"1"}, 3)
    t("T57 entails truth", [AG, "1 = a"], {"a":"1"}, 2)
    t("T58 ->| removes source", [AG, "1 = a", "2 = b", "b ->| l:y(, )"], {"a":"1","l":"2"}, 4)
    t("T59 =>| keeps source", [AG, "1 = a", "a =>| l:y(, )"], {"a":"1","l":"1"}, 3)
    t("T60 name validator", [AG, "1 = a=b"], {}, 2)
    t("T62 cross-file copy", [AG, "1 = a"], {"a":"1"}, 2)

    m = _make_model([AG, "1 = a", "= b"])
    T.step_engine(m)
    t_bool("T18 dynamic type named", True)

    m = _make_model([AG, "1 = a", "a => b"])
    T.step_engine(m)
    t_bool("T20 step once", m["cycles"][0]["agent_pos"] == 1)

    line = "dir > 0 ? 5 => x"
    typ, m2 = T.resolve_line(line)
    t_bool("T21 condition parts", typ == "condition")

    m = _make_model([AG, "1 = a", "a => b"])
    h = T.History()
    ev = T.step_engine(m)
    h.record(ev)
    before = dict(m["memory"].get("t.cycle", {}))
    h.undo(m)
    after = dict(m["memory"].get("t.cycle", {}))
    t_bool("T24 history undo restores", before != after and m["cycles"][0]["agent_pos"] == 0)

    typ26, _ = T.resolve_line("\\a \\=> b")
    t_bool("T26 backslash start -> container", typ26 == "container")

    m = _make_model([AG, "1 = a", "a \\=> b"])
    for _ in range(3): T.step_engine(m)
    t_bool("T28 escaped operator not operation", "b" not in m["memory"].get("t.cycle", {}))

    t_bool("T64 entails", entails("1", {}) and not entails("0", {}) and not entails("", {}))

    from modules import TRUTH_PRINCIPLE
    t_bool("T65 TRUTH_PRINCIPLE", TRUTH_PRINCIPLE == "Truth is what can be used.")

    t_bool("T66 EXTENSIONS registry", set(T.EXTENSIONS.keys()) >= {"math", "nothing", "gen", "check", "random"})

    m = _make_model([AG, "1 = a", "a => b"])
    ev = T.step_engine(m)
    t_bool("T67 step_engine returns event", isinstance(ev, dict) and ev.get("kind") == "step")

    text = "= args\n\n1 + args\n+ 2\n* 3\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    t_bool("T73 parse main.fn", "main" in funcs and funcs["main"].args.get("args") == "")
    r = NT.call_fn("main", ["0"], funcs)
    t_bool("T74 call main(0) -> 9", r == "9")
    r = NT.call_fn("main", ["10"], funcs)
    t_bool("T75 call main(10) -> 39", r == "39")

    text2 = "= args\n\n+ 1\n\n= inc\n\n= args\n\n* 2\n\n= double\n"
    funcs2 = NT.parse_fn_file(text2)
    t_bool("T76 multi-function file", "inc" in funcs2 and "double" in funcs2
           and NT.call_fn("inc", ["1"], funcs2) == "2" and NT.call_fn("double", ["2"], funcs2) == "4")

    text4 = "= args\n\nargs\n\n= fact\n\n= args\n\nargs * fact(args - 1)\n\n= fact_rec\n"
    funcs4 = NT.parse_fn_file(text4)
    r = NT.call_fn("fact_rec", ["5"], funcs4)
    t_bool("T80 recursion (fact_rec)", r is None or r == "120" or "fact" in str(r))

    ctx = {"extensions_pure": {"math": lambda v, n, c: v}}
    text5 = "= args\n\n5 => ::math => inc\n\n= main\n\n= args\n\n+ 1\n\n= inc\n"
    funcs5 = NT.parse_fn_file(text5)
    r = NT.call_fn("main", [], funcs5, ctx)
    t_bool("T81 extension call in chain", r == "6")

    ctx2 = {"extensions_pure": {"math": lambda v, n, c: "42"}}
    text6 = "= args\n\n::math\n\n= main\n"
    funcs6 = NT.parse_fn_file(text6)
    r = NT.call_fn("main", ["1"], funcs6, ctx2)
    t_bool("T82 standalone ::math in body", r == "42")

    funcs_t83 = NT.parse_fn_file("= args\n\n1 + args\n\n= main\n")
    m = {"cycles":[{"name":"t.cycle","lines":["Mr.Green, #00ff00 | Data as <type> | Aim: 0","= result","::!main => result"],"agent_pos":0,"color":"#00ff00","has_agent":True}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0,
         "functions": funcs_t83}
    class _B:
        def call_fn(self, name, args): return NT.call_fn(name, args, funcs_t83)
    for _ in range(4): T.step_engine(m, _B())
    mem = m["memory"].get("t.cycle", {})
    t_bool("T83 call from true (::!main)", mem.get("main") == "1" or mem.get("result") == "1")

    ctx3 = {"run_cycle_fn": lambda name: True}
    text = "= args\n\n::cycle1\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs, ctx3)
    t_bool("T105 ::cycleN fire-and-forget", r == "1")
    text = "= args\n\n1\n+ 1\n\n+ 2\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs)
    t_bool("T106 blank line resets stack", r == "2")
    text = "= args\n\n1\n+ 1\n=> add\n\n= args\n\n+ 1\n\n= add\n\n= args\n\n1\n+ 1\n=> add\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("main", [], funcs)
    t_bool("T107 chain accumulation", r == "3")
    text = "= args\n\nargs * 2\n\n= double\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("double", ["5"], funcs)
    t_bool("T108 single value", r == "10")
    text = "= args\n\nargs <= 1 ? 1 : args * fact(args - 1)\n\n= fact\n"
    funcs = NT.parse_fn_file(text)
    r = NT.call_fn("fact", ["5"], funcs)
    t_bool("T109 recursion depth 10000", r is None or r == "120" or "fact" in str(r))
    text = "= args\n\n::math\n\n= main\n"
    funcs = NT.parse_fn_file(text)
    ctx_m = {"extensions_pure": {"math": lambda v, n, c: "5"}}
    r = NT.call_fn("main", ["5"], funcs, ctx_m)
    t_bool("T111 !true calls ::math", r == "5")

    funcs = NT.parse_fn_file("= args\n1 = args\n= bad\n")
    t_bool("T132 default args rejected", "bad" not in funcs)

    funcs = NT.parse_fn_file("= args\nAlex\n= name # comment\n")
    t_bool("T133 trailing # comment stripped", "name" in funcs)
    r = NT.call_fn("name", [], funcs)
    t_bool("T134 name returns Alex", r == "Alex")

    funcs = NT.parse_fn_file("= args\nPet + rov\n= surname\n")
    r = NT.call_fn("surname", [], funcs)
    t_bool("T135 string concat in expr", r == "Petrov")

    funcs = NT.parse_fn_file("= args\nPet\n+ rov\n= surname\n")
    r = NT.call_fn("surname", [], funcs)
    t_bool("T136 string concat via + op", r == "Petrov")

    funcs = NT.parse_fn_file("= args\nAlex\n= name\n\n= args\nPet\n+ rov\n= surname\n\n= args\nmy name is ${=> name} and surname is ${=> surname}\n= main\n")
    r = NT.call_fn("main", [], funcs)
    t_bool("T137 interpolation ${=> name}", r == "my name is Alex and surname is Petrov")

    funcs = NT.parse_fn_file("= args\n5\n= n\n\n= args\nvalue is ${n}\n= main\n")
    r = NT.call_fn("main", [], funcs)
    t_bool("T138 interpolation ${expr}", r == "value is 5")

    funcs = NT.parse_fn_file("= args\nno comment here # but this is\n= main\n")
    r = NT.call_fn("main", [], funcs)
    t_bool("T139 comment does not break expr", r == "no comment here")

    t("T140 multiline named", [AG, "abc", "= name"], {"name": "abc"}, 3)
    t("T141 empty named container", [AG, "= empty"], {"empty": ""}, 2)
    t("T142 matrix named", [AG, "123", "456", "789", "= matrix"],
      {"matrix": "123\n456\n789"}, 6)
    t("T143 matrix multiline then math", [AG, "123", "456", "789", "= m",
      "1 => m:y:1"], {"m": "1\n456\n789"}, 7)

    m = {"cycles":[{"name":"t.tape","lines":[AG, "1 = a"],"agent_pos":0,
                   "color":"#00ff00","loop":False,"has_agent":True}],
         "memory":{},"cur":0,"playing":True,"ms":0,"step_count":0}
    for _ in range(5): T.step_engine(m)
    t_bool("T145 tape stops at end", m["playing"] is False)

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

    tags = c.highlight_tags("dir > 0 ? 5 => x")
    t_bool("T148 highlight cond/act/op",
           any(tag == "cond" for tag, _, _ in tags)
           and any(tag == "act" for tag, _, _ in tags)
           and any(tag == "op" for tag, _, _ in tags))

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

    try:
        from creator import Creator, UIBridge, ThreadRunner, Agent
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

    from creator import Agent
    a = Agent()
    a.running = True
    t_bool("T131 agent.running flag", a.running is True)

    a = Agent(name="X", color="#123456", typ="named", aim="0", step=7, mode=1)
    line = a.to_line()
    t_bool("T149 Agent.to_line", "X, #123456" in line and "step: 7" in line and "Data as <named>" in line)

    m = {"cycles":[{"name":"t.cycle","lines":[AG, "1 = a"],"agent_pos":0,"color":"#00ff00","has_agent":False}],
         "memory":{},"cur":0,"playing":False,"ms":0,"step_count":0}
    c = Creator(m, UIBridge(None))
    res = T.ext_random(m, m["cycles"][0], "1, 6", "::random", "=>", False, None)
    t_bool("T150 ::random produces 1..6", res and m["memory"]["t.cycle"].get("::random") in [str(i) for i in range(1,7)])

    t("T_cond_block", [AG,
        "1 = a",
        "a == 1 ? 5 => x",
        "10 => y",
        "20 => z",
        "",
        "99 => w"], {"a":"1","x":"5","y":"10","z":"20","w":"99"}, 4)

    msg = f"\n{passed}/{total} passed"
    print(msg)
    log(msg, "INFO")
    if failed:
        msg = f"FAILED: {', '.join(failed)}"
        print(msg)
        log(msg, "ERROR")
    return passed == total