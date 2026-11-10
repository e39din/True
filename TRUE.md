# true — Language Specification

**true is what can be used.**

**Programming must be live! Live, open, visual, easy and beautiful — all at once.**

**Version**: true 0.9.9.

---

## Mental model

**One sentence**: the agent reads the cycle/tape step by step, determines the type of a line, executes the instruction, moves to the next line — the agent line is fixed at the top, the executing line is highlighted, the tape moves step by step.

**creator** is the heart: it runs **agents** that analyze files and execute programs. To describe programs, you use two languages: **true** (imperative, tape-based: a program is a cycle or a tape of lines) and **!true** (purely functional: pure functions over a stack). **Simple** is the LiveDE on top of all this.

**Seven questions to keep in mind** (answers are in this document):
1. How does a line become an instruction? (see Line types)
2. What is the priority of line types? (see Line types)
3. What does `=>` do, and when do I use `->`, `=>|`, `->|`, `<->`? (see Operators)
4. What is the difference between `x` and `y` axes? (see Axes)
5. When do I use a jump (`^ N`, `^ name`, `^ :cycle:N`)? (see Jumps)
6. How does the truth predicate work? (see Truth predicate)
7. What is the difference between `.cycle` and `.tape`? (see Program = cycle or tape)

---

## Quick start (syntax)

Cycle (executed cyclically; agent is part of creator, not of the language):
# version: 1
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

Tape (executed once, stops at last line):
# version: 1
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

---

## Roles in the system

| Layer | Role | What the user sees |
|---|---|---|
| **Simple** | LiveDE, interpreter, presentation layer | Editor, AgentBar, buttons, highlighting, samples, `●` indicator |
| **creator** | Heart of the system | (under the hood) agents, languages, extensions, OS |
| **true** | Core language (cycle or tape of lines; **no agent**) | `.cycle` / `.tape` files, lines, axes |
| **!true** | Pure functions (stack) | `.fn` files, functions, stack, chains |
| **modules** | Shared utilities | (under the hood) eval, escape, ref parsing |

**Simple** is the LiveDE. **creator** is the heart. **Under the hood**: creator + true + !true. **On the surface**: Simple.

---

## Program = cycle or tape of lines

A program is a `.cycle` or `.tape` file: a list of lines, split by `\n`.

- `.cycle` — executed cyclically: when the agent reaches the last line, it rotates to line 0 and continues.
- `.tape` — executed once: when the agent reaches the last line, execution stops.

The **agent** is the one who **reads the cycle/tape**, **determines its content**, **executes instructions**. Its **state/settings** (name, color, `Data as <type>`, `Aim`, `step`, `mode`) are written in the **first line** of the file. The agent is both **executor** and **observer**.

The first line of the file may or may not be an agent. **`has_agent`** — internal flag: if `True`, the first line is an agent line and is skipped by `true.step_engine`.

Analogy with quantum mechanics: each line is like a qubit — a black box for the agent until he reads it and determines its type (`Data as <type>`). After reading, the line acquires certainty — just like a qubit collapses when measured.

## Line types (priority: top wins)

`separator > version > jump > condition > action > named > container`

| Type | Syntax | Action |
|---|---|---|
| `separator` | `""` / `---` | block boundary |
| `version` | `# version: N` | ignored, used for migration |
| `jump` | `^ N` / `^ name` / `^ :cycle:N` / `^ :cycle:name` | jump |
| `condition` | `cond ? act` | if `true(cond)` → `act` |
| `action` | `src op dst` (chain) | `=>` `->` `=>\|` `->\|` `<->` |
| `named` | `val = name(, name2)` | `mem[name] = val` (`= x` → `x=""`) |
| `container` | `text` | literal |

The agent line is not a line type of the language. It is parsed by creator, not by true. From the language, the agent is accessed through `::agent:*`.

## Operators

| Operator | Semantics |
|---|---|
| `=>` | copy (`dst = src`, src kept) |
| `->` | move (`dst = src`, src removed) |
| `=>\|` | insert-copy into axis (src kept) |
| `->\|` | insert-move into axis (src removed) |
| `<->` | swap |
| `?=>` | eval src, then copy |
| `::nothing` | `->` / `->\|` deletes, `=>` / `=>\|` no-op |
| `::math` | `mem["::math"] = eval(src)` |

## Axes

| Syntax | default sep |
|---|---|
| `name:x(sep):idx` | `""` (characters) |
| `name:y(sep):idx` | `"\n"` (lines) |

`idx` = `1`-based, `first`, `last`, `all`.

- `42 => list:x:i` — set
- `6 =>| list:x:i` — insert
- `list:x:2 -> n` — extract
- `list:x:2 ->| stack:x:1` — extract + insert
- `a:y:1:x:2` — multidimensional

## Cross-file operations

All open files in the list are already linked. Use `cycle:` qualifier.

## Names

Names cannot contain operator characters or separators: `= > < \ , ; ? / : " \` '`.

## Escape

`\` before operator, condition, name, or extension makes it a literal.

## Jumps

`^ N`, `^ name`, `^ :cycle:N`, `^ :cycle:name`.

## Extensions

| Extension | Semantics |
|---|---|
| `::math` | `mem["::math"] = eval(src)` |
| `::nothing` | `->` deletes, `=>` no-op |
| `::gen` | copy template (by name or path), substitute args, add to list |
| `::check` | return 1 if all substrings (split by `;`) are in file, else 0 |
| `::agent:finish` | finish the agent's work (update UI) |
| `::agent:aim` | get the agent's Aim |
| `::agent:name` | get the agent's name |
| `::agent:color` | get the agent's color |
| `::agent:mode` | get the agent's mode |
| `::agent:step` | get the agent's step number |
| `::agent:focus` | get the content of the highlighted line |
| `::agent:lineType` | get the line type as the agent determines it |
| `::creator:*` | UI control (play/pause/step/stepBack/restart/new/open/save/close/exit) |
| `:name` | call `!true` function `name` (from the open files list) |
| `:cycleN` | run `true` cycle N (fire-and-forget, returns 1/0) |

**`has_agent`** — internal flag: if `True`, the first line is an agent line and is skipped by `true.step_engine`.

## !true — pure functions (v0.9.6)

See [NOT_TRUE.md](NOT_TRUE.md).

**Why "!true"?** Because it is not visual — it does not participate in the step-by-step mode, it runs behind the scenes. And because I made it first, and thought it was not good enough on its own for my goals — but in combination with `true` and `creator` it is pretty good :)

`.fn` files contain one or more pure functions, separated by blank lines or by `= name`.

Pure functions: result is NOT stored in the function; it is returned to the caller (`mem["::!name"]`).

Blank line inside function resets the stack. Chain accumulates result and calls function with it.

One value per function (no tuples; use true cycle/tape for multiple values).

Extensions: `!true` can call ANY extension from `true`.
- `true`: extension creates container `mem["::name"]`, can be used later.
- `!true`: extension result is used on stack within the call, not persisted.

Recursion: allowed with guard (`depth > 10000`).

Call from true: `:name` (call by name from the open files list).

## Objects

Objects are real, actual (true) artifacts — files (`.cycle`, `.tape`, `.fn`, `.txt`) and their contents. No rigid class form.

Identity: `cycle:name` (file), `name` (container), `cycle:name:sub` (qualified).

Description: text, symbols, names, your own rules.

Validation: `::check` (returns 1 if all `;`-separated substrings are in the file, else 0). Works with names or file paths.

Generation: `::gen` (copies template by name or path, substitutes `$name`/`_name`, adds new file to the list).

## How the system works (formal semantics in plain words)

### State

The **state** of the system is three things:
- the **cycle** (or **tape**) — the list of lines the agent works with,
- the **memory** — the named containers the agent reads and writes,
- the **agent position** — which line the agent is currently at.

Formally: `state = (lines, memory, agent_position)`, where the agent position is always inside the lines.

### Truth predicate

**true is what can be used.**
A condition is **true** if its value is not empty, not `"0"`, not `"False"`, and not undefined.
A condition is **false** otherwise.

In code: `entails(condition, memory)` returns `True` or `False`.
Formally: `true(φ) ⟺ value(φ, memory) ∉ {undefined, "0", "", "False"}`.

### Invariants

Invariants are rules that must always hold. If any of them is broken, the program is in an invalid state.
Each invariant is written formally (for the parser and tests) and in plain words (for the reader).

| # | Formally | In plain words |
|---|---|---|
| I1 | `0 ≤ agent_position ≤ len(lines)` | The agent is always inside the cycle/tape; `== len(lines)` is the moment of rotate (`.cycle`) or end (`.tape`) |
| I2 | all names in `memory` are valid | Every name in memory can be parsed back (no operator characters, no separators) |
| I3 | all axes in `memory` are consistent with sep | Every axis in memory uses the same separator it was written with |
| I4 | agent is not lost on rotate | When the agent wraps to line 0, it is still on a valid line |
| I5 | memory keys are removed only via `remove_ref` | A key disappears from memory only through explicit `remove_ref` (or `::nothing` with `->`), never silently |

**In one sentence**: the agent is always somewhere real, every name and every axis can be read back, the agent never gets lost, and memory changes only through explicit operations.

## Turing completeness

- **true**: Turing-complete (emulates MT via `mem["tape"]`, `mem["head"]`, `mem["state"]`, `Aim`).
- **!true**: pure functional layer; Turing-complete in combination with `true`.
- **System**: `simple + true + !true` is Turing-complete.

## EBNF

program      = cycle | tape ;
cycle        = [ version_line ] { line "\n" } ;
tape         = [ version_line ] { line "\n" } ;
version_line = "# version:" num ;
line         = separator | jump | condition | action | named | container ;
separator    = "" | "---" ;
jump         = "^" ( ":" cycle_name ":" ( num | name ) | num | name ) ;
condition    = expr "?" { action } ;
action       = src { "," src } op { "," dst } [ op ... ] ;
named        = [ value ] "=" name { "," name } ;
container    = text ;
op           = "=>" | "->" | "<->" | "=>|" | "->|" ;
src          = ref | expr ;
dst          = ref | "::" ext | "::nothing" | ":" name ;
ref          = [ cycle ":" ] ( name | axis_ref | num | "line:" num ) ;
axis_ref     = name ":" ("x" | "y") [ "(" sep ")" ] [ ":" ( num | "first" | "last" | "all" ) ] ;
ext          = "math" | "nothing" | "gen" | "check" | "agent:" name | "creator:" name ;
name         = { letter | digit | "_" | "." } - reserved ;

**Note**: `agent` is not a line type in the language. The agent line is parsed by creator, not by true.

## Examples

### Example 1: Elevator (cycle)

# version: 1
Mr.Green, #5fb85f | Data as <condition> | Aim: 0 | step: 0 | mode: 1
6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor == max ? -1 => dir
floor == 1 ? 1 => dir

floor + dir => ::math => floor

Python analogue:
max_val = 6
floor = 1
direction = 1
lift = []

while True:
    if direction > 0:
        lift.insert(floor, str(floor))
    if direction < 0:
        lift.pop()
    if floor == max_val:
        direction = -1
    if floor == 1:
        direction = 1
    floor = floor + direction
print(floor, lift)

### Example 2: Script (tape, mode=0)

# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
1 = a
2 = b
0 = result

a + b ?=> result

Python analogue:
a = 1
b = 2
result = 0
result = a + b
print(result)

### Example 3: Generate and validate (classes, objects)

Template `car` (car.txt):

color: red; max_speed: 200; = args
speed: 0

Program:

# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
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

### Example 4: Matrix (axes)

# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
123 = array2d
456
789

array2d:y:2 => row
row:x:1 => cell

Python analogue:
array2d = "123\n456\n789"
row = array2d.split("\n")[1]
cell = row[0]
print(cell)

## Principles (10 principles, 3 levels)

### Level 1 — Core principle (1)

> **Programming must be open, visual, easy and beautiful — all at once.**

### Level 2 — Philosophy (7) — "everything is X"

1. **Everything is a string.** (a line of the cycle/tape)
2. **Everything is an instruction.**
3. **Everything is a list/array.**
4. **Everything is a container.**
5. **Everything is an expression.**
6. **Everything is a condition.**
7. **Everything is a geometric figure with axes.**

### Level 3 — Paradigm (3) — how the language is built

8. **Program = data + instructions.**
9. **A program can be a function, a switch, a set of instructions, a set of data.**
10. **The agent can change the reality.** (the agent is part of creator, not part of the language)

**Total**: 10 principles in 3 levels.

## Architecture

1. **Simple is the LiveDE, interpreter, presentation layer.** (what the user sees)
2. **creator is the heart.** (agents, languages, extensions, OS)
3. **Under the hood: creator + true + !true; on the surface: Simple.**
4. **true does not see !true; !true does not see true; all interaction via creator.**
5. **Extensions are not core.** (`::math`, `::nothing`, `::gen`, `::check`, `::agent:*`, `::creator:*` — extensions; core — operators and line types)
6. **The agent is part of creator, not part of the language.** The language does not know about the agent. From the language, the agent is accessed through `::agent:*`. **`has_agent`** — internal flag: if `True`, the first line is an agent line and is skipped by `true.step_engine`.

## Syntax & semantics

1. **Names cannot contain operator characters or separators.** (`= > < \ , ; ? / : " \` '`)
2. **Escape `\` before operator/condition/name/extension → literal.**
3. **`# version: N` is the first line of a `.cycle` / `.tape` file.**
4. **Axes: x (chars), y (lines).**
5. **`idx` = 1-based, `first`, `last`, `all`.**
6. **`=>` copy, `->` move, `=>|` insert-copy, `->|` insert-move, `<->` swap.**
7. **`?` — condition; `Aim` — halt (agent's Aim, part of creator).**
8. **Jumps: `^ N`, `^ name`, `^ :cycle:N`, `^ :cycle:name`.**
9. **Cross-file operations via `cycle:` qualifier.**
10. **Parsing uses EBNF and parser, not regex.**

## Consequences

1. **Objects are real artifacts** (files `.cycle`, `.tape`, `.fn`, `.txt`); describe in any text file, validate with `::check`, generate with `::gen`.
2. **Classes are templates**; use `::gen` and `::check`.
3. **Each line is like a qubit**: a black box until read; after reading it acquires certainty. (analogy with quantum mechanics)
4. **If it can be done simply — do it simply.**
5. **Work with what exists (do not multiply entities).**

## Meta

1. **If something exists — it is truth (true).**
2. **The hidden forces guessing and breeds errors.**
3. **Visibility gives understanding of truth (true).**

## FAQ

**Q: What is the difference between .cycle and .tape?**
A: .cycle is executed cyclically (agent wraps to line 0). .tape is executed once (agent stops at the last line).

**Q: What is the difference between => and ->?**
A: => copies (src kept), -> moves (src removed).

**Q: What is the difference between =>| and ->|?**
A: =>| inserts a copy into an axis (src kept), ->| inserts and moves (src removed).

**Q: How do I call a !true function from true?**
A: :name (call by name from the open files list).

**Q: How do I call a true cycle from !true?**
A: :cycleN (fire-and-forget, returns 1/0).

**Q: How do I generate an object from a template?**
A: ::gen (copies template, substitutes $name/_name, adds new file).

**Q: How do I validate an object?**
A: ::check (returns 1 if all ;-separated substrings are in the file, else 0).

**Q: Is the agent part of the language?**
A: No. The agent is part of creator. From the language, you work with the agent through ::agent:*. **`has_agent`** — internal flag: if `True`, the first line is an agent line and is skipped by `true.step_engine`.

**Q: Why "line" and not "string"?**
A: "String" can mean the whole text, a block of code, or a single character. "Line" is unambiguous: one line of the cycle/tape.

**Q: Why "!true"?**
A: Because it is not visual — it does not participate in the step-by-step mode, it runs behind the scenes. And because I made it first, and thought it was not good enough on its own for my goals — but in combination with true and creator it is pretty good :)

## Troubleshooting

| Problem | Solution |
|---|---|
| Agent stops unexpectedly | Check .tape — it stops at the last line by design. For cyclic execution use .cycle. |
| Syntax error | Check that names don't contain = > < \ , ; ? / : " ` '. |
| Extension not found | Check EXTENSIONS. Built-in: math, nothing, gen, check, agent, creator. |
| !true function returns empty | Check .fn is loaded (load_all_fns). Check function name. |
| ::gen creates empty file | Check template exists (by name or path). Args separated by ;. |
| Memory not updated | Check flush_memory_to_lines — writes to lines on each step. |
| File not saved | Check .cycle / .tape extension. Check write permissions. |
| Agent does not run | Check that the first line of the cycle is an agent: `Name, #hex \| Data as <type> \| Aim: cond \| step: N \| mode: M`. Check `has_agent` flag. |
| mode=0 does not update UI | UI updates only on `::agent:finish` or `pause`. Add `::agent:finish` at the end of the tape. |

## Adding your own extension

An extension is a function `fn(model, cyc, src, dst, op, eval_flag, bridge)` that returns `True` on success.

Example (an extension that reverses a string):

import true as T

def ext_reverse(model, cyc, src, dst, op, eval_flag, bridge):
    mem = model["memory"].setdefault(cyc["name"], {})
    value = mem.get(src, src)
    mem["::reverse"] = value[::-1]
    return True

T.register_extension("reverse", ext_reverse)

Usage:

hello => ::reverse

Result: `mem["::reverse"] = "olleh"`.

**Note**: `!true` can also call any extension (it uses the result on the stack, not in a container). See [NOT_TRUE.md](NOT_TRUE.md).

## Glossary

| Term | Meaning |
|---|---|
| **Cycle** | the whole `.cycle` file (list of lines); executed cyclically |
| **Tape** | the whole `.tape` file (list of lines); executed once — stops when the agent reaches the last line |
| **Line** | one line of the cycle/tape |
| **Chain of lines** | a block of lines up to a separator |
| **Agent** | part of creator, not part of the language; reads the cycle/tape, determines its content, executes instructions; its state/settings are in the first line |
| **Reading** | the process: the agent determines the type of a line and executes the instruction according to that type |
| **Extension** | `::name` (math, nothing, gen, check, agent:*, creator:*) — not core, added on top |
| **Function call** | `:name` — call a `!true` function by name from the open files list |
| **Cycle call** | `:cycleN` — run a `true` cycle (fire-and-forget) |
| **Axis** | a list stored in one line: `x` (chars), `y` (lines) |
| **Container** | a named value in memory (`mem[name]`) |
| **Named** | a line `val = name` — sets `mem[name] = val` |
| **Action** | a line `src op dst` — copies/moves/swaps values |
| **Condition** | a line `cond ? act` — if `cond` is true, executes `act` |
| **Jump** | a line `^ N` / `^ name` / `^ :cycle:N` / `^ :cycle:name` — moves the agent |
| **Separator** | `""` / `---` — block boundary |
| **Version** | `# version: N` — first line, ignored, used for migration |
| **Memory** | the named containers the agent reads and writes |
| **State** | the three things: lines (cycle/tape), memory, agent position |
| **Invariant** | a rule that must always hold (I1–I5) |
| **Truth** | what can be used: not empty, not `"0"`, not `"False"`, not undefined |