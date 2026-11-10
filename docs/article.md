# True — a language where the agent reads the tape

*First demonstration. 5 minutes read.*

**True** is a programming language where a program is a **cycle or a tape of lines**,
and an **agent**-observer reads the lines step by step, determines the type of each line,
and executes the instruction.

> **Status**: MVP. True is a full-fledged language with its own concept —
> it can evolve as an independent language.

| Language | Article | Docs |
|---|---|---|
| **English** | this file | [README.md](README.md) |

Back to root: [../README.md](../README.md)

---

## Idea

**True** is a language where the program is a **cycle or a tape of lines**,
and the **agent** reads, determines the type, and executes.

A program is a **tape of lines**. The **agent-observer is part of the program** (the first line of `.cycle`).
It moves down the tape; on each step it **reads a line**, **determines its type**, and **executes the instruction**.

**The program is both the data source and the instructions.**
There is no separate "code" and "data" — there are **lines** the agent reads and executes.

**The agent is not an external interpreter but part of the `.cycle` file.**
It is **executor** and **data** at the same time: `Mr.Green, ...` is just a line of the program,
but it is the one that **reads** the rest.

**The agent line is fixed at the top** in the UI; the executing line is highlighted;
the tape moves step by step. See [README.md](README.md) — AgentBar.

---

## The same logic in two languages

**True** (main.cycle):

```true
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
Поднимайся на лифте Mr.Green :)

6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last -> ::nothing

floor == max ? -1 => dir
floor == 1 ? 1 => dir

floor + dir => ::math => floor
```

**Python** (imperative logic):

```python
max_floor = 6
floor = 1
dir = 1
lift = []

while True:
    if dir > 0:
        lift.append(floor)
    if dir < 0 and lift:
        lift.pop()
    if floor == max_floor:
        dir = -1
    if floor == 1:
        dir = 1
    floor = floor + dir
    print(f"floor={floor} dir={dir} lift={lift}")
```

**Honest**: Python implements **the same logic**, but **does not** read and **does not** change
its source code. **True** does this **on every step** — the program **self-modifies**:
the agent **reads lines**, `memory` **reflects** in the text (via `flush`), `<type>` **updates**.
This is **the difference** of True from imperative languages: **program = data + instructions** in one.

See [TRUE.md](TRUE.md) — «Program = cycle or tape of lines», «Line types», «Truth predicate».

---

## Key ideas

### 1. Observer = agent = part of the program

**The agent is the first line of `.cycle`:**

```true
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
```

- `Mr.Green` — name,
- `#5fb85f` — color,
- `Data as <...>` — type the agent **recognized** (updated each step),
- `Aim: 1` — goal.

**The agent is not a separate process but a line of the program.** It is **executor** and **data**
at the same time: `Mr.Green, ...` is just a `.cycle` line like all others,
but it is the one that **reads** the rest.

**The agent line is fixed at the top in the UI.** See [README.md](README.md) — AgentBar.

### 2. Chains of lines

Empty line (`""` or `---`) — **block boundary**.
When the agent determines the type of the **first** line in a chain, **the whole chain up to `separator`**
fires **together** as one block of that type.

Fragment of the real program (`main.cycle`):

```true
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last -> ::nothing

floor + dir => ::math => floor
```

- `dir > 0 ? ...` and `dir < 0 ? ...` — **one block** `condition` (empty line is the boundary).
- `floor + dir => ...` — **separate block** `action` (after `separator`).

This allows **grouping** logic without brackets.

### 3. Axes

A container can be an **axis** — a list:

| Syntax | default sep | What |
|---|---|---|
| `name:x(sep):idx` | `""` (characters) | horizontal |
| `name:y(sep):idx` | `","` | vertical |

`idx` = `1`-based, `first`, `last`, `all`.

Example:

```true
1, 2, 3 = lift
lift:y(, ):last -> ::nothing
```

→ `lift = "1, 2"` (last element removed).

**Axes** are a way to **store lists** in one line and **insert/remove** elements.

### 4. Extensions `::name`

- `::math` — arithmetic (`+ - * / % ^ == != && ||`),
- `::nothing` — deletion (`->` deletes, `=>` — no-op).

See [TRUE.md](TRUE.md) — «Extensions».

---

## Philosophy

- **Truth is what can be used.**
- **Programming must be open, visual, easy and beautiful — all at once.**

---

## See also

- [Full documentation (EN)](README.md)
- [true — Language Specification](TRUE.md)
- [!true — Language Specification](NOT_TRUE.md)
- [Opinions](OPINIONS.md)
- [Back to root](../README.md)

---

*Simple v0.16.2. Python 3.8+. Tkinter. No dependencies.*