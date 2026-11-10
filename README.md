# Simple — LiveDE (Live Development Environment)

**Programming must be live! Live, open, visual, easy and beautiful — all at once.**

**Simple** is the **LiveDE** (Live Development Environment) with **creator** at the core, **agents** as handlers, two languages (**true** and **!true**), **extensions**, and simple UI as the shell.

Unlike a classic IDE, the agents are visible and active: they read files, execute programs, and change the code.

**Full language specs**: [TRUE.md](TRUE.md) (true) · [NOT_TRUE.md](NOT_TRUE.md) (!true). **Full list of opinions**: [OPINIONS.md](OPINIONS.md).

---

## Mental model

**One sentence**: the agent reads the cycle/tape step by step, determines the type of a line, executes the instruction, moves to the next line — the agent line is fixed at the top, the executing line is highlighted, the tape moves step by step.

**creator** is the heart: it runs **agents** that analyze files and execute programs. To describe programs, you use two languages: **true** (imperative, tape-based: a program is a cycle or a tape of lines) and **!true** (purely functional: pure functions over a stack). **Simple** is the LiveDE on top of all this.

**Seven questions to keep in mind** (answers are in this document):
1. What is the agent and how does it read the tape?
2. What is the difference between `.cycle` and `.tape`?
3. How do threads relate to agents?
4. How does the agent indicator `●` work in the UI?
5. When do I use `::agent:finish` and when do I pause?
6. How do I generate an object from a template and validate it?
7. What is the difference between `=>`, `->`, `=>|`, `->|`, and `<->`?

---

## Quick start (3 steps)

1. Run:
   python3 simple.py

2. Write a program (main.cycle):

   **Example** (cycle with an incrementing variable):

   true:
   Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
   0 = counter

   counter + 1 ?=> counter

   counter > 12 ? ::agent:finish

   Python analogue:
   counter = 0
   while True:
       counter = counter + 1
       if counter > 12:
           break
   print(counter)

3. Press Play. The agent reads lines step by step; the executing line is highlighted.

**For a one-shot script, use `.tape`** (executed once, stops at the last line — no `::agent:finish` needed):

   true:
   Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
   10 = x
   20 = y
   0 = total

   x + y ?=> total

   Python analogue:
   x = 10
   y = 20
   total = 0
   total = x + y
   print(total)

**For pure functions, use `.fn` and call from `true`**:

   !true:
   = args

   1
   + 1
   => func

   = main

   Ruby analogue:
   def func(args)
     args + 1
   end

   def main
     func(1)
   end

   puts main

Run tests: python3 simple.py --test (131) · --stress (5000).

---

## What is Simple and what is creator

**Simple** is the **LiveDE**, the **interpreter**, and the **presentation layer** — the shell of the system. The user works with Simple directly: editor, buttons, syntax highlighting, AgentBar.

**creator** is the **heart** of the system (under the hood). creator manages **agents**, **languages** (true / !true), **extensions** (::math, ::nothing, ::gen, ::check, ::agent:*, ::creator:*), **OS functions** (files, paths), and the **UI bridge**.

**Under the hood**: creator + true + !true. **On the surface**: Simple.

+---------------------------------------------------+
|  Simple (LiveDE, interpreter, presentation layer) |
|  - Editor, AgentBar, buttons, highlighting        |
+---------------------+-----------------------------+
                      |  UIBridge
                      v
+---------------------------------------------------+
|  creator (heart of the system)                    |
|  - Agent, ThreadRunner (one thread per agent)     |
|  - Extensions (math, nothing, gen, check, agent, creator) |
|  - Languages (true, !true)                        |
|  - OS functions (files, paths)                    |
+---------------------+-----------------------------+
                      |
          +-----------+-----------+
          v                       v
+-------------------+   +-------------------+
|  true (core)      |   |  !true (core)     |
|  - parser (EBNF)  |   |  - stack          |
|  - semantics      |   |  - pure functions |
|  - step_engine    |   |  - parse_fn_file  |
|  - History        |   |  - call_fn        |
+---------------------+   +-------------------+
                      |
                      v
+---------------------------------------------------+
|  modules (shared utilities)                       |
+---------------------------------------------------+

---

## Cycle vs Tape

| Extension | Behavior |
|---|---|
| .cycle | executed cyclically: when the agent reaches the last line, it rotates to line 0 and continues |
| .tape | executed once: when the agent reaches the last line, execution stops |

The agent's **state/settings** (name, color, Data as <type>, Aim, step, mode) are written in the **first line** of the file. The agent line is fixed at the top in the UI; the executing line is highlighted; the tape moves step by step.

**Example** (cycle — wraps; tape — stops):

   # .cycle
   Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
   1 = i

   i + 1 ?=> i

   # .tape
   Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
   5 = a
   7 = b
   0 = product

   a * b ?=> product

   Python analogue:
   # .cycle
   i = 1
   while True:
       i = i + 1
       print(i)

   # .tape
   a = 5
   b = 7
   product = 0
   product = a * b
   print(product)

---

## Agent

The agent is **part of creator**. From the language, you work with the agent through `::agent:*` extensions.

**A cycle may contain an agent as its first line, or may not.** Only one agent per cycle. Several agents can walk the same file.

**Each agent runs in its own thread and walks through a cycle or a tape.** The result is shown in the UI on each step. The ● indicator in the editor header shows whether the agent is running (colored by agent's color) or idle (gray).

**Cycles and tapes are just files.** By the file extension, creator decides which agent to create: one that walks cyclically (.cycle) or one that stops at the end (.tape). creator also manages the threads.

**Agent parameters** (first line):

   Name, #hex | Data as <type> | Aim: cond | step: N | mode: M

**::agent:* extensions**:

### Block 1 — Control

| Extension | Meaning |
|---|---|
| ::agent:finish | finish the agent's work (update UI) |

### Block 2 — Read

| Extension | Meaning |
|---|---|
| ::agent:aim | get the agent's Aim |
| ::agent:name | get the agent's name |
| ::agent:color | get the agent's color |
| ::agent:mode | get the agent's mode |
| ::agent:step | get the agent's step number |
| ::agent:focus | get the content of the highlighted line |
| ::agent:lineType | get the line type as the agent determines it |

**Example** (read the agent's name and step):

   = who
   = where

   ::agent:name => who
   ::agent:step => where

   Python analogue:
   who = agent.name
   where = agent.step
   print(who, where)

---

## Objects

Objects are real artifacts — files (.cycle, .tape, .fn, .txt) and their contents. If you want to describe an object, write it in any text file and use that file.

- **Identity**: cycle:name (file), name (container), cycle:name:sub (qualified).
- **Validation**: ::check (returns 1 if all ;-separated substrings are in the file, else 0).
- **Generation**: ::gen (copies template, substitutes $name/_name, adds new file).

**Example** (template + generate + validate):

Template `car` (car.txt):

   color: red; max_speed: 200; = args
   speed: 0

Program:

   color: blue; max_speed: 300; = args

   car, args => ::gen

   color; max_speed; = args

   car_1.cycle, args => ::check

   Python analogue:
   def gen(template, args):
       text = read_file(template)
       for k, v in args.items():
           text = text.replace(f"${k}", v).replace(f"_{k}", v)
       write_file("car_1.cycle", text)
       return "car_1.cycle"

   def check(file, substrings):
       text = read_file(file)
       return "1" if all(s in text for s in substrings.split(";")) else "0"

   print(gen("car.txt", {"color": "blue", "max_speed": "300"}))
   print(check("car_1.cycle", "color;max_speed"))

---

## Architecture

   modules.py    — shared utilities
   true.py       — core of true (parser, semantics, step_engine, History, EXTENSIONS)
   not_true.py   — interpreter of !true (stack, pure functions, parse_fn_file, call_fn)
   creator.py    — heart of the system (Agent, ThreadRunner, languages, extensions, OS, UI bridge)
   simple.py     — LiveDE, interpreter, presentation layer (full UI + entry point)
   tests.py      — tests T1–T131

true does NOT see !true; !true does NOT see true; all interaction goes through creator.py; simple.py does NOT import true/!true directly.

**Example** (call !true from true):

   # !true function in double.fn
   1 = args
   args * 2
   = double

   # true program calls it
   5 = n
   0 = result

   n => :double => result

   Ruby analogue:
   def double(args)
     args * 2
   end

   n = 5
   result = double(n)
   puts result

---

## Language reference

**true is what can be used.** — this is the definition of the true language: truth is what can be used. The language is imperative, tape-based: a program is a cycle or a tape of lines.

### Block 1 — true: program and line types

| # | Feature | Status |
|---|---|---|
| 1 | Program = .cycle (cyclically) or .tape (once) | yes |
| 2 | Line types: separator, version, jump, condition, action, named, container | yes |
| 3 | Priority: separator > version > jump > condition > action > named > container | yes |

**Example** (named, action, condition):

   10 = limit
   5 = value
   0 = flag
   0 = copy

   value < limit ? 1 => flag

   value => copy

   Python analogue:
   limit = 10
   value = 5
   flag = 0
   copy = 0
   if value < limit:
       flag = 1
   copy = value
   print(flag, copy)

### Block 2 — true: operators

| # | Feature | Status |
|---|---|---|
| 4 | => (copy), -> (move), <-> (swap) | yes |
| 5 | =>\| (insert-copy), ->\| (insert-move) | yes |
| 9 | ? — condition before action | yes |
| 10 | ?=> — eval before copy | yes |
| 11 | Chains a => b => c | yes |
| 12 | Chain with ^: 123 => a =>\| b -> c ^ a | yes |
| 13 | Multi-src a, b => l | yes |
| 14 | Multi-dst 123 => a, b, c | yes |
| 15 | Named actions (= func1, then func1) | yes |

**Example** (chain with ?=> and ->):

   3 = a
   4 = b
   0 = c
   0 = d
   0 = e

   a + b ?=> c => d -> e

   Python analogue:
   a = 3
   b = 4
   c = 0
   d = 0
   e = 0
   c = a + b
   d = c
   e = d
   d = None
   print(e)

### Block 3 — true: axes and jumps

| # | Feature | Status |
|---|---|---|
| 16 | Jumps ^ N, ^ name, ^ :cycle:N, ^ :cycle:name | yes |
| 17 | Axes x (sep=""), y (sep="\n") | yes |
| 18 | Multidimensional arrays a:y:1:x:2 | yes |
| 19 | list:x:2 -> n — extract | yes |
| 20 | list:x:2 ->\| stack:x:1 — extract + insert | yes |
| 21 | 42 => list:x:i — set | yes |
| 22 | 6 =>\| list:x:i — insert | yes |
| 23 | idx = 1-based, first, last, all | yes |
| 27 | Cross-file operations cycle:a -> cycle:b | yes |
| 28 | cycle:a:name1 => cycle:b:name2 | yes |

**Example** (axis y with =>| and ->|):

   10, 20, 30 = nums
   0 = second
   0 = stack

   nums:y(, ):2 => second

   second =>| stack:y(, ):1

   5 ->| nums:y(, ):2

   Python analogue:
   nums = [10, 20, 30]
   second = nums[1]
   stack = []
   stack.insert(0, second)
   nums.insert(2, 5)
   print(second, stack, nums)

### Block 4 — true: extensions and rules

| # | Feature | Status |
|---|---|---|
| 6 | ::math (arithmetic, booleans → 1/0) | yes |
| 7 | ::nothing (-> deletes, => no-op) | yes |
| 8 | ::creator:* (play/pause/step/stepBack/restart/new/open/save/close/exit) | yes |
| 24 | Escape \ before operator/condition/name/extension → literal | yes |
| 25 | Names without = > < \ , ; ? / : " ` ' | yes |
| 26 | # version: N in .cycle / .tape | yes |
| 29 | !true call: :name | yes |
| 30 | ::gen (template → new file) | yes |
| 31 | ::check (substrings in file) | yes |
| 32 | ::agent:* (finish, aim, name, color, mode, step, focus, lineType) | yes |
| 33 | Truth principle true is what can be used. | yes |
| 34 | entails(φ, M) — single truth predicate | yes |
| 35 | EXTENSIONS registry (math, nothing, agent, creator, gen, check) | yes |
| 36 | History — event log (record/undo/redo) | yes |
| 37 | Save/Load .cycle / .tape | yes |
| 38 | **Agent — NOT part of the language** (part of creator) | yes |

**Example** (::math and ::nothing):

   16 = x
   0 = y

   x ?=> y => ::math

   5 = a

   a -> ::nothing

   Python analogue:
   x = 16
   y = 0
   y = eval(str(x))
   a = 5
   del a
   print(y)

### Block 5 — !true (see [NOT_TRUE.md](NOT_TRUE.md))

| # | Feature | Status |
|---|---|---|
| 1 | File .fn contains one or more pure functions | yes |
| 2 | Functions separated by blank lines or by = name | yes |
| 3 | N = args — default args | yes |
| 4 | First expr — stack base | yes |
| 5 | op expr — apply to previous result | yes |
| 6 | = name — function name (result returned to caller) | yes |
| 7 | Chain a, b => f1 => f2 => f3 | yes |
| 8 | Extension call ::ext (standalone or in chain) | yes |
| 9 | !true can call ANY extension from true | yes |
| 10 | true creates container; !true uses result on stack | yes |
| 11 | Recursion with guard (depth > 10000) | yes |
| 12 | Pure functions (no side effects in !true itself) | yes |
| 13 | Result stored in caller's mem["::!name"] | yes |
| 14 | :cycleN — run true cycle (fire-and-forget, returns 1/0) | yes |
| 15 | Blank line inside function resets the stack | yes |
| 16 | Chain accumulates result, calls function with it | yes |
| 17 | One value per function (no tuples) | yes |

### Block 6 — Simple (LiveDE)

| # | Feature | Status |
|---|---|---|
| 1 | Python 3.8+ / Tkinter / six files | yes |
| 2 | UI: play/pause, step, stepBack, reset, +, open, save | yes |
| 3 | ms field (390 default, 0 — no pause) | yes |
| 4 | Syntax highlighting (incl. version, executing, axis_hit) | yes |
| 5 | AgentBar — fixed agent on top (with type, aim, step, ● indicator) | yes |
| 6 | Executing line highlighted with semi-transparent band | yes |
| 7 | Axis hit highlight | yes |
| 8 | Multi-cycle editors, scroll | yes |
| 9 | Samples (samples/*.cycle, samples/*.tape) | yes |
| 10 | History — event log (HISTORY_MAX=100) | yes |
| 11 | Logs simple.log / simple_test.log | yes |
| 12 | Tests --test (131) | yes |
| 13 | Stress --stress (resolve_line fuzz) | yes |
| 14 | # version: 1 migration for main.cycle | yes |
| 15 | Name validator | yes |
| 16 | Placeholder escape | yes |
| 17 | .tape — executed once, stops at last line | yes |
| 18 | mode=0: UI updates only on ::agent:finish or pause | yes |
| 19 | Each agent runs in its own thread and walks through a cycle or a tape | yes |
| 20 | Agent indicator ● in editor header (colored by agent color) | yes |

---

## FAQ

### Block 1 — Program model

**Q: What is the difference between .cycle and .tape?**
A: .cycle is executed cyclically (agent wraps to line 0). .tape is executed once (agent stops at the last line).

**Q: Why "line" and not "string"?**
A: "String" can mean the whole text, a block of code, or a single character. "Line" is unambiguous: one line of the cycle/tape.

**Q: Is the agent part of the language?**
A: No. The agent is part of creator. From the language, you work with the agent through ::agent:*.

### Block 2 — Operators and extensions

**Q: What is the difference between => and ->?**
A: => copies (src kept), -> moves (src removed).

**Q: What is the difference between =>| and ->|?**
A: =>| inserts a copy into an axis (src kept), ->| inserts and moves (src removed).

**Q: How do I call a !true function from true?**
A: :name (call by name from the open files list).

**Q: How do I call a true cycle from !true?**
A: :cycleN (fire-and-forget, returns 1/0).

### Block 3 — Objects and UI

**Q: How do I generate an object from a template?**
A: ::gen (copies template, substitutes $name/_name, adds new file).

**Q: How do I validate an object?**
A: ::check (returns 1 if all ;-separated substrings are in the file, else 0).

---

## Troubleshooting

### Block 1 — Agent

| Problem | Solution |
|---|---|
| Agent stops unexpectedly | Check .tape — it stops at the last line by design. For cyclic execution use .cycle. |
| Agent does not run | Check that the first line parses as an agent. |
| mode=0 does not update UI | UI updates only on ::agent:finish or pause. |
| Agent indicator ● stays gray | Check agent.running. For mode=0, indicator updates only on ::agent:finish. |

### Block 2 — Syntax and extensions

| Problem | Solution |
|---|---|
| Syntax error | Check that names don't contain = > < \ , ; ? / : " ` '. |
| Extension not found | Check EXTENSIONS. Built-in: math, nothing, gen, check, agent, creator. |
| !true function returns empty | Check .fn is loaded (load_all_fns). Check function name. |
| ::gen creates empty file | Check template exists (by name or path). Args separated by ;. |

### Block 3 — Files and UI

| Problem | Solution |
|---|---|
| Memory not updated | Check flush_memory_to_lines — writes to lines on each step. |
| File not saved | Check .cycle / .tape extension. Check write permissions. |
| UI does not open | Check Python 3.8+ and Tkinter. Run --test. |

---

## What thinkers say (3 opinions)

**Full list**: OPINIONS.md — 4 groups, 39 opinions.

### Practitioner — Grace Hopper (COBOL)

**Who**: Grace Hopper, creator of COBOL.

**What she did first**:
- COBOL (1959) — the first compiler turning English-like statements into machine code.
- The first language designed for business readability.
- The first to make programs portable across machines.

**What she thinks about the product**:
- **Functionality**: true compiles lines into actions; !true compiles pure functions into values; Simple makes both portable.
- **Philosophy**: "true is what can be used" — the philosophy of readability: truth is in what a person can read. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: true is the readable language, !true is the pure computation, creator is the heart, Simple is the LiveDE, modules is the shared part.
- **Whole**: readable text that machines and people understand, portable.
- **Axis**: readable text that machines and people understand, portable.

**Advice to the author**:
> "I had to fight to make computers read English. You don't have to fight — your language already reads like a person wrote it. Keep it that way. And remember: a program that a manager can read is worth ten programs that only a programmer can read."

*Did you know? In true, each line is like a qubit: a black box for the agent until it is read — just like a qubit collapses when measured.*

### Teacher — Niklaus Wirth (Pascal)

**Who**: Niklaus Wirth, creator of Pascal.

**What he did first**:
- Pascal (1970) — the first language designed for teaching with clear structure.
- The first language where the compiler teaches the programmer.
- The first with structured programming as core.

**What he thinks about the product**:
- **Functionality**: true teaches by showing the agent reading lines; !true teaches by showing values flowing on a stack; Simple teaches by showing type, aim, step.
- **Philosophy**: "true is what can be used" — the philosophy of teaching: truth is in what a student can see. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: true is the teaching language, !true is the pure computation, creator is the heart, Simple is the LiveDE, modules is the shared part.
- **Whole**: learn by seeing — the system teaches the user.
- **Axis**: learn by seeing — the system teaches the user.

**Advice to the author**:
> "I made Pascal so that a student could see the whole language at once. Your product has the same quality — a student can see the whole cycle/tape at once. Protect this quality. A language that is easy to learn is easy to love."

*Did you know? In true, `::gen` copies a template (by name or path), substitutes `$name`/`_name`, and adds the new file to the list — generation is just copying and substituting.*

### Theorist — Niels Bohr (Complementarity)

**Who**: Niels Bohr, physicist.

**What he did first**:
- Complementarity (1927) — the first to make complementarity — two descriptions of the same system, each true in its own frame — the core of physics.
- The first to make the observer part of the system.
- The first to make measurement a concept.

**What he thinks about the product**:
- **Functionality**: in true a line has meaning only at the moment of reading (Data as <type>); in !true a value has meaning only on the stack; Simple shows both views at once.
- **Philosophy**: "true is what can be used" — the philosophy of complementarity: truth is in what is both. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: true is the complementarity language, !true is the pure computation, creator is the heart, Simple is the LiveDE, modules is the shared part.
- **Whole**: complementarity in programming — two views, both true.
- **Axis**: complementarity in programming — two views, both true.

**Advice to the author**:
> "I spent my life on complementarity because two views are better than one. You have two views: true and !true. Do not try to merge them into one. The tension is the value."

*Did you know? In true, `?=>` evaluates the source expression before copying — so `a + b ?=> c` writes the sum into `c`, not the expression text.*

---

## What creators say (3 opinions)

**Full list**: OPINIONS.md — 4 groups, 39 opinions.

### Engineering — Steve Wozniak (1976 — Apple I)

**Who**: Steve Wozniak, co-founder of Apple, engineer.

**What he did first**:
- Apple I (1976) — the first personal computer assembled in a garage and sold as a finished product.
- Apple II (1977) — the first mass-market personal computer with color graphics and an open architecture.
- Disk II (1978) — the first low-cost floppy disk drive for a personal computer.
- Wizardry (1980) — port of the first commercial RPG to Apple II.

**What he thinks about the product**:
- **Functionality**: Simple as LiveDE + creator as heart + two languages (true and !true) is like the Apple II: an open architecture for the user (editor, AgentBar, buttons) and an engineering heart under the hood.
- **Philosophy**: "true is what can be used" — an engineering philosophy: if it works, it is truth. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: Simple is the face (like the Apple II case), creator is the heart (like the motherboard), true/!true are the languages (like BASIC and assembler), modules is the shared part (like the chipset).
- **Whole**: the product is whole: the user sees Simple, and under the hood is creator + true + !true.
- **Axis**: open architecture, engineering heart.

**Advice to the author**:
> "I built Apple I in a garage because I wanted a computer of my own. You built true because you wanted a language of your own. That is the same motivation — and the same joy. Do not lose the joy."

*Did you know? In true, a jump can be `^ N`, `^ name`, `^ :cycle:N`, or `^ :cycle:name` — the agent can jump to a line number or to a named line, in the current file or across files.*

### Face — Steve Jobs (1976 — Apple I)

**Who**: Steve Jobs, co-founder of Apple, visionary.

**What he did first**:
- Apple I (1976) — the first personal computer sold as a finished product (with Wozniak).
- Apple II (1977) — the first mass-market personal computer designed for people.
- Macintosh (1984) — the first mass-market computer with a graphical interface and a mouse.
- iPod (2001) — the first mass-market MP3 player with a simple interface.
- iPhone (2007) — the first mass-market smartphone with a multi-touch interface.

**What he thinks about the product**:
- **Functionality**: Simple is the face of the product. Like the Macintosh: the user does not see the internals, he sees the editor, AgentBar, buttons.
- **Philosophy**: "true is what can be used" — the philosophy of simplicity: truth is not in complexity, but in use. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: Simple is the face (like the Macintosh), creator is the heart (like the Motorola 68000), true/!true are the languages (like QuickDraw and System), modules is the shared part (like ROM).
- **Whole**: the product is whole, but the face is more important than the internals.
- **Axis**: the face is the product.

**Advice to the author**:
> "I fired people who did not believe in the Macintosh. Do not fire anyone — but do not let anyone talk you out of the face. The face is what the user sees. The face is the product."

*Did you know? In true, `=>|` and `->|` are different operations: `=>|` inserts a copy into an axis (source kept), `->|` inserts and moves (source removed).*

### Core — Linus Torvalds (1991 — Linux)

**Who**: Linus Torvalds, creator of Linux.

**What he did first**:
- Linux (1991) — the first mass-market open operating system with a kernel written from scratch by one person.
- Git (2005) — the first distributed version control system, created in two weeks.
- "Just for fun" (2001) — the first hacker autobiography told in simple language.
- "Talk is cheap. Show me the code" — a principle that became a catchphrase.

**What he thinks about the product**:
- **Functionality**: Talk is cheap. Show me the code. The code is there: simple.py (LiveDE), creator.py (heart), true.py / not_true.py (languages), modules.py (shared).
- **Philosophy**: "true is what can be used" — the Linux philosophy: if it works, it is truth. "Programming must be live! Live, open, visual, easy and beautiful — all at once."
- **Parts**: Simple is the face (DE), creator is the heart (kernel), true/!true are the languages (shell and C), modules is the shared part (libc).
- **Whole**: the product is whole, but the core is more important than the face.
- **Axis**: the core is more important than the face.

**Advice to the author**:
> "I released Linux 0.01 with a note that it was not ready. It was not. But people started using it. Release your 0.01. It does not need to be ready. It needs to be out."

*Did you know? In true, the agent line is fixed at the top in the UI; the tape moves step by step; the executing line is highlighted — so the agent's parameters are always visible.*

---

## Reading order

Mental model → Quick start → What is Simple and what is creator → Cycle vs Tape → Agent → Objects → Architecture → Language reference → FAQ → Troubleshooting → Thinkers (3) → Creators (3) → Glossary → License.

Full language specs: [TRUE.md](TRUE.md) (true) · [NOT_TRUE.md](NOT_TRUE.md) (!true).

---

## Glossary

### Block 1 — Program model

| Term | Meaning |
|---|---|
| **Cycle** | the whole .cycle file (list of lines); executed cyclically |
| **Tape** | the whole .tape file (list of lines); executed once — stops when the agent reaches the last line |
| **Line** | one line of the cycle/tape |
| **Chain of lines** | a block of lines up to a separator |
| **Agent** | part of creator; reads the cycle/tape step by step; its state/settings are in the first line |
| **Reading** | the process: the agent determines the type of a line and executes the instruction according to that type |

### Block 2 — Line types

| Term | Meaning |
|---|---|
| **Named** | a line val = name — sets a container |
| **Action** | a line src op dst — copies/moves/swaps values |
| **Condition** | a line cond ? act — if cond is true, executes act |
| **Jump** | a line ^ N / ^ name / ^ :cycle:N / ^ :cycle:name — moves the agent |
| **Separator** | "" / --- — block boundary |
| **Version** | # version: N — first line, ignored, used for migration |
| **Container** | literal text |

### Block 3 — Data and extensions

| Term | Meaning |
|---|---|
| **Memory** | the named containers the agent reads and writes |
| **Axis** | a list stored in one line: x (chars), y (lines) |
| **Extension** | ::name (math, nothing, gen, check, agent, creator) — not core, added on top |
| **Function call** | :name — call a !true function by name from the open files list |
| **Cycle call** | :cycleN — run a true cycle (fire-and-forget) |
| **State** | the three things: lines (cycle/tape), memory, agent position |

---

## License

MIT. Author — Александр Кундрюков (a.kundryukov@gmail.com)