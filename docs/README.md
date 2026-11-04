# Simple — True language interpreter (full documentation)

**True** is a programming language where a program is a **tape of qubits** (strings),
and an **agent**-observer "measures" qubits step by step, swapping them.

**Simple** is a cross-platform interpreter in Python 3 + Tkinter.
One file, no dependencies.

> **Status**: MVP. True is a full-fledged language with its own concept —
> it can evolve as an independent language.

| Language | Docs | Article |
|---|---|---|
| **English** | this file | [article.md](article.md) |
| **Русский** | [ru/README.md](ru/README.md) | [ru/article.md](ru/article.md) |

Back to root: [../README.md](../README.md)

---

## Quick start

```bash
python3 simple.py           # launch UI
python3 simple.py --test    # tests
```

Requires **Python 3.8+** (Tkinter is in the standard library).

---

## Usage

| Action | Result |
|---|---|
| ▶ / ⏸ | play / pause |
| ⏭ | **one step** |
| ⏮ | reset |
| `+` | add cycle |
| `ms` field | step delay (default 390) |
| click in editor | **auto-pause**, edit |
| RMB in editor | Copy / Paste / Cut / Select All |
| `Space` | play / pause |

---

## Default program (main.cycle)

```
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
Поднимайся на лифте Mr.Green :)

6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor == max ? -1 => dir
floor == 1 ? 1 => dir

floor + dir => ::math => floor
```

---

## Concept

| Term | Meaning |
|---|---|
| **Cycle** | program = list of lines |
| **Qubit** | a line; value depends on the observer |
| **Agent** | observer; line `Name, #hex \| Data as <type> \| Aim: cond` |
| **`<type>`** | type the agent **recognized** on the current line (updated each step) |
| **Chain of qubits** | agent marks all lines up to `separator` as one block |
| **`::name`** | extension (`::math`, `::nothing`) |

### Line types

| Type | Syntax | Action |
|---|---|---|
| `agent` | `Name, #hex \| Data as <t> \| Aim:` | marker |
| `separator` | `""` / `---` | block boundary |
| `named` | `val = name(, name2)` | `mem[name] = val` (`= x` → `x=""`) |
| `container` | `text` | literal |
| `action` | `src op dst` (chain) | `=>` `->` `<->` `=>\|` `->\|` |
| `condition` | `cond ? act` | if `cond ≠ 0` → `act` |
| `jump` | `^ name` / `^ N` / `^ :cycle:N` | jump |

### Operators

| Operator | Semantics |
|---|---|
| `=>` | copy |
| `->` | move |
| `=>\|` | insert-copy into axis (with `sep`) |
| `->\|` | insert-move into axis |
| `<->` | swap |
| `::nothing` | `->` deletes, `=>` is no-op |
| `::math` | `mem["::math"] = eval(src)` |

### Axes

| Syntax | default sep |
|---|---|
| `name:x(sep):idx` | `""` (characters) |
| `name:y(sep):idx` | `","` |

`idx` = `1`-based, `first`, `last`, `all`.

### Jumps

| Syntax | Target |
|---|---|
| `^ name` | `named` line with name |
| `^ N` | line `N` (1-based) |
| `^ :cycle:N` | cycle `cycle`, line `N` |

#### Jump example (two cycles) — F106

`main.cycle`:

```
Mr.Green, #5fb85f | Data as <jump> | Aim: 1
1 = x

^ :helper.cycle:1
```

`helper.cycle`:

```
Mr.Blue, #5b9bd5 | Data as <named> | Aim: 1
42 = y

^ :main.cycle:2
```

The agent jumps from `main.cycle` to `helper.cycle` (line 1), then back to `main.cycle` (line 2).

---

## EBNF

```ebnf
cycle        = { line "\n" } ;
line         = agent | separator | jump | condition | action | named | container ;
agent        = name "," color "| Data as <" type "> | Aim:" text ;
separator    = "" | "---" ;
jump         = "^" ( ":" cycle_name ":" num | num | name ) ;
condition    = expr "?" { action } ;
action       = src { "," src } op { "," dst } [ op ... ] ;
named        = [ value ] "=" name { "," name } ;
container    = text ;
op           = "=>" | "->" | "<->" | "=>|" | "->|" ;
src          = name | expr | axis_ref | line_ref ;
dst          = name | axis_ref | "::" ext | "::nothing" ;
expr         = term { ("+" | "-" | "*" | "/" | "%" | "^") term } ;
axis_ref     = name ":" ("x" | "y") [ "(" sep ")" ] [ ":" ( num | "first" | "last" ) ] ;
line_ref     = ":" [ cycle_name ] ":line:" num ;
ext          = "math" | "nothing" | name ;
```

**Priorities** (top wins):
`agent > separator > jump > condition > action > named > container`

---

## Syntax highlighting

| Type | Color | Background |
|---|---|---|
| agent | `#5fb85f` (soft green) | `#1e2a1e` |
| named | `#5b9bd5` (blue) | — |
| action | `#7fb069` (green) | — |
| act (inside condition) | `#7fb069` (green) | — |
| cond | `#e8c547` (yellow) | — |
| op (`=>`, `->`, `=>\|`, `<->`) | `#a8d888` (light green) | `#2a2a3a` |
| jump | `#b07fd5` (purple) | — |
| container | `#888888` (gray) | — |
| separator | `#444444` (dark) | — |

---

## Features

| Feature | Yes / No |
|---|---|
| Multiple cycles (`+`) | ✅ |
| Cross-cycle jumps `^ :cycle:N` | ✅ |
| Axes `x`/`y` with `sep` | ✅ |
| Chains `a => b => c` | ✅ |
| `::math` (arithmetic, booleans) | ✅ |
| `::nothing` (name / axis / line) | ✅ |
| Syntax highlighting | ✅ |
| Step (one step) | ✅ |
| Logs to `simple.log` / `simple_test.log` | ✅ |
| Escape `\=>` | ✅ |
| Comments `#` | ❌ |
| User `::functions` | ❌ (only `math`, `nothing`) |
| Save `.cycle` to disk | ❌ |
| Load `.cycle` | ❌ |

---

## Tests

```bash
python3 simple.py --test
```

**Expected output** (`simple_test.log`):

```
=== Simple tests v0.16.2 ===
  T1 named: PASS
  ...
  T22 default program: PASS

24/24 passed
```

---

## Logs

| File | Content |
|---|---|
| `simple.log` | UI session log (`[step]`, `[type]`, `[exec]`, `[flush]`, `[swap]`) |
| `simple_test.log` | test log |

Logs are **overwritten** on each run.

---

## Limitations (honest)

| # | Limitation |
|---|---|
| 1 | One file `simple.py` — demo, not production |
| 2 | Regex parsing — fragile with non-standard syntax |
| 3 | No save/load `.cycle` |
| 4 | No comments in language |
| 5 | `::` — only `math` and `nothing` |
| 6 | `flush` writes to `lines` (not `Text` directly) |
| 7 | No scopes (all per-cycle) |
| 8 | No `mem` history (current only) |
| 9 | **No `.cycle` version marker (`# version: N`) — planned** — F107 |

---

## Philosophy

- **Qubit = line** — visual
- **Observer = agent** — original
- **Program reads and changes itself** — differs from imperative languages
- **Chains of qubits** — grouping without brackets
- **Axes** — lists in one qubit
- **`Data as <type>`** — live feedback
- **One file** — easy to copy

---

## See also

- [Article (EN)](article.md)
- [Полная документация (RU)](ru/README.md)
- [Статья (RU)](ru/article.md)
- [Back to root](../README.md)

---

## License

MIT | 2026 | Author — Александр Кундрюков (a.kundryukov@gmail.com)