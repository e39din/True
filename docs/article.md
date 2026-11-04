# True — a language where the program thinks in lines

*First demonstration. 5 minutes read.*

**True** is a programming language where a program is a **tape of qubits** (strings),
and an **agent**-observer "measures" qubits step by step, swapping them.

> **Status**: MVP. True is a full-fledged language with its own concept —
> it can evolve as an independent language.

| Language | Article | Docs |
|---|---|---|
| **English** | this file | [README.md](README.md) |
| **Русский** | [ru/article.md](ru/article.md) | [ru/README.md](ru/README.md) |

Back to root: [../README.md](../README.md)

---

## Idea

**True** is a language where **the program reads and changes itself**.

A program is a **tape of lines**. The **agent-observer is part of the program** (the first line of `.cycle`).
It moves down the tape, on each step **swaps a line with the one below** and **executes** what it reads.

**The program is both the data source and the instructions.**
There is no separate "code" and "data" — there are **qubits** the agent reads and **swaps**.

**The agent is not an external interpreter but part of the `.cycle` file.**
It is **executor** and **data** at the same time: `Mr.Green, ...` is just a line of the program,
but it is the one that **reads** the rest.

---

## The same logic in four languages

**True** (main.cycle):

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

<details>
<summary><b>Lisp (Scheme)</b> — click to expand</summary>

```lisp
(define max-floor 6)
(define floor 1)
(define dir 1)
(define lift '())

(define (step)
  (when (> dir 0) (set! lift (append lift (list floor))))
  (when (and (< dir 0) (not (null? lift))) (set! lift (reverse (cdr (reverse lift)))))
  (when (= floor max-floor) (set! dir -1))
  (when (= floor 1) (set! dir 1))
  (set! floor (+ floor dir))
  (display (list floor dir lift)) (newline))

(let loop () (step) (loop))
```

</details>

<details>
<summary><b>Rust</b> — click to expand</summary>

```rust
fn main() {
    let max_floor = 6;
    let mut floor = 1;
    let mut dir: i32 = 1;
    let mut lift: Vec<i32> = Vec::new();

    loop {
        if dir > 0 { lift.push(floor); }
        if dir < 0 { lift.pop(); }
        if floor == max_floor { dir = -1; }
        if floor == 1 { dir = 1; }
        floor += dir;
        println!("floor={} dir={} lift={:?}", floor, dir, lift);
    }
}
```

</details>

**Honest**: Python, Lisp and Rust implement **the same logic**, but **do not** read and **do not** change
their source code. **True** does this **on every step** — the program **self-modifies**:
the agent **changes lines**, `memory` **reflects** in the text, `<type>` **updates**.
This is **the difference** of True from imperative languages: **program = data + instructions** in one.

---

## Key ideas

### 1. Qubit = line

A line is a **qubit**. Its value depends on the **observer** (agent).

On each step the agent:

- **reads** the `target` line (type, value),
- **executes** an action (if `action` / `condition`),
- **changes** `lines` (`flush` of memory),
- **changes** the agent line (`Data as <type>`).

**The program reads and changes itself.** This is **the difference** from imperative languages.

### 2. Observer = agent = part of the program

**The agent is the first line of `.cycle`:**

```
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
```

- `Mr.Green` — name,
- `#5fb85f` — color,
- `Data as <...>` — type the agent **recognized** (updated each step),
- `Aim: 1` — goal.

**The agent is not a separate process but a line of the program.** It is **executor** and **data**
at the same time: `Mr.Green, ...` is just a `.cycle` line like all others,
but it is the one that **reads** the rest and **changes** them.

### 3. Chains of qubits

Empty line (`""` or `---`) — **block boundary**.
When the agent determines the type of the **first** qubit in a chain, **the whole chain up to `separator`**
fires **together** as one block of that type.

Fragment of the real program (`main.cycle`):

```
Mr.Green, #5fb85f | Data as <condition> | Aim: 1
dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor + dir => ::math => floor
```

- `dir > 0 ? ...` and `dir < 0 ? ...` — **one block** `condition` (empty line is the boundary).
- `floor + dir => ...` — **separate block** `action` (after `separator`).

This allows **grouping** logic without brackets.

### 4. Axes

A container can be an **axis** — a list:

| Syntax | default sep | What |
|---|---|---|
| `name:x(sep):idx` | `""` (characters) | horizontal |
| `name:y(sep):idx` | `","` | vertical |

`idx` = `1`-based, `first`, `last`, `all`.

Example:

```
1, 2, 3 = lift
lift:y(, ):last -> ::nothing
```

→ `lift = "1, 2"` (last element removed).

**Axes** are a way to **store lists** in one qubit and **insert/remove** elements.

### 5. Extensions `::name`

- `::math` — arithmetic (`+ - * / % ^ == != && ||`),
- `::nothing` — deletion (`->` deletes, `=>` — no-op).

---

## Philosophy

- **Qubit = line** — visual.
- **Observer = agent = part of the program** — executor and data at the same time.
- **Program reads and changes itself** — differs from imperative languages.
- **Chains of qubits** — grouping without brackets.
- **Axes** — lists in one qubit.
- **`::name`** — extensions.
- **`Data as <type>`** — live feedback.
- **One file** — easy to copy.

---

## See also

- [Full documentation (EN)](README.md)
- [Полная документация (RU)](ru/README.md)
- [Статья (RU)](ru/article.md)
- [Back to root](../README.md)

---

*Simple v0.16.2. Python 3.8+. Tkinter. No dependencies.*