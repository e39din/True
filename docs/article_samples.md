# True — templates in action

*Examples from `samples/`. Each example: GIF, program, short note, a fact about the language in a callout, Python analogue.*

**True** — a language where a program is a **cycle or a tape of lines**,
and an **agent** reads the lines step by step, determines the type of each line,
and executes the instruction. See [README.md](README.md), [TRUE.md](TRUE.md), [NOT_TRUE.md](NOT_TRUE.md).

Each example below is a real file from `samples/` (created by `ensure_samples()` in `simple.py`).
The GIF placeholder shows the execution — paste the actual GIF in place of the link.

---

## true

### 1. Counter (`.cycle`)

![counter](gifs/counter.gif)

**Program** (`samples/counter.cycle`):

```true
# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 1
0 = counter
counter + 1 ?=> counter
```

**What happens**: the agent reads `counter + 1 ?=> counter` on every step; `?=>` evaluates the source expression before copying, so `counter` increments. A `.cycle` wraps to line 0 and continues.

> [!NOTE]
> **Fact** — `?=>` evaluates the source expression before copying: `a + b ?=> c` writes the sum into `c`, not the expression text. (TRUE.md, «Operators»)

**Python analogue**:

```python
counter = 0
while True:
    counter = counter + 1
    print(counter)
```

---

### 2. Elevator (`.cycle`)

![elevator](gifs/elevator.gif)

**Program** (`samples/elevator.cycle`):

```true
# version: 1
Mr.Green, #5fb85f | Data as <condition> | Aim: 0 | step: 0 | mode: 1
6 = max
1 = floor
1 = dir

= lift

dir > 0 ? floor =>| lift:y(, ):floor
dir < 0 ? lift:y(, ):last  -> ::nothing

floor >= max ? -1 => dir
floor <= 1 ? 1 => dir

floor + dir => ::math => floor
```

**What happens**: `=>|` inserts a copy into the axis `lift:y(, )` (source kept); `->` with `::nothing` deletes the last element; `::math` computes `floor + dir`. The agent reads a block of `condition` lines (separated by an empty line) as one block.

> [!NOTE]
> **Fact** — an empty line is the block boundary: the agent reads the first line of the chain, determines its type, and applies it to the whole chain up to `separator`. (TRUE.md, «Chains of lines»)

**Python analogue**:

```python
max_floor = 6
floor = 1
direction = 1
lift = []

while True:
    if direction > 0:
        lift.append(str(floor))
    if direction < 0 and lift:
        lift.pop()
    if floor >= max_floor:
        direction = -1
    if floor <= 1:
        direction = 1
    floor = floor + direction
    print(f"floor={floor} dir={direction} lift={lift}")
```

---

### 3. Script (`.tape`)

![script](gifs/script.gif)

**Program** (`samples/script.tape`):

```true
# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
1 = a
2 = b
0 = result
a + b => ::math => result
::agent:finish
```

**What happens**: `.tape` is executed once; `::agent:finish` stops the agent. `::math` computes `a + b` and writes the result to `::math`; the chain then copies it to `result`.

> [!NOTE]
> **Fact** — `::math` stores the result in `mem["::math"]`, not in the destination; the chain then copies it on. (TRUE.md, «Extensions»)

**Python analogue**:

```python
a = 1
b = 2
result = 0
result = a + b
print(result)
```

---

### 4. Matrix (`.tape`)

![matrix](gifs/matrix.gif)

**Program** (`samples/matrix.tape`):

```true
# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0

123
456
789
= array2d

1 = i
1 = j

array2d:y:i:x:j % 2 == 0 ? X => array2d:y:i:x:j
array2d:y:i:x:j % 2 == 1 ? O => array2d:y:i:x:j

j + 1 ?=> j
j > 3 ? 1 => j
j == 1 ? i + 1 ?=> i
i > 3 ? ::agent:finish
```

**What happens**: `array2d:y:i:x:j` — a chain of axes (y → x); `%` in the condition; `X`/`O` are literals (not declared in `mem`, so `read_ref` returns the name itself); `j + 1 ?=> j`, `j > 3 ? 1 => j`, `j == 1 ? i + 1 ?=> i` walk the 3×3 matrix; `i > 3 ? ::agent:finish` exits. The matrix becomes `OXO / XOX / OXO` (odd → `O`, even → `X`).

> [!NOTE]
> **Fact** — `idx` in an axis can be `1`-based, `first`, `last`, `all`. (TRUE.md, «Axes»)

**Python analogue**:

```python
array2d = [list("123"), list("456"), list("789")]
i = 1
j = 1
while True:
    cell = array2d[i-1][j-1]
    if int(cell) % 2 == 0:
        array2d[i-1][j-1] = "X"
    if int(cell) % 2 == 1:
        array2d[i-1][j-1] = "O"
    j += 1
    if j > 3:
        j = 1
        i += 1
    if i > 3:
        break
print("\n".join("".join(row) for row in array2d))
```

---

### 5. Classes: generate and validate (`.tape`)

![classes](gifs/classes.gif)

**Program** (`samples/classes.tape`):

```true
# version: 1
Mr.Green, #5fb85f | Data as <type> | Aim: 0 | step: 0 | mode: 0
color: red; max_speed: 200; = args
car, args => ::gen
color; max_speed; = args
car_1.cycle, args => ::check
::agent:finish
```

**Template** (`car.txt`):

```text
color: red; max_speed: 200; = args
speed: 0
```

**What happens**: `::gen` copies the template `car.txt`, substitutes `$name`/`_name`, and adds the new file to the list. `::check` returns `1` if all `;`-separated substrings are present in the file.

> [!NOTE]
> **Fact** — jumps: `^ N`, `^ name`, `^ :cycle:N`, `^ :cycle:name`. (TRUE.md, «Jumps»)

**Python analogue**:

```python
def gen(template, args):
    text = read_file(template)
    for k, v in args.items():
        text = text.replace(f"${k}", v).replace(f"_{k}", v)
    write_file("car_1.cycle", text)
    return "car_1.cycle"

def check(file, substrings):
    text = read_file(file)
    return "1" if all(s in text for s in substrings.split(";")) else "0"

print(gen("car.txt", {"color": "red", "max_speed": "200"}))
print(check("car_1.cycle", "color;max_speed"))
```

---

### 6. Race (`.cycle`) — two agents write to one `data.txt`

![race](gifs/race.gif)

**Program A** (`samples/race_a.cycle`):

```true
# version: 1
Mr.Red, #d04040 | Data as <type> | Aim: 0 | step: 0 | mode: 1

:data.txt:line:1 => a
a + "-" => a
a => :data.txt:line:1
```

**Program B** (`samples/race_b.cycle`):

```true
# version: 1
Mr.Blue, #4080d0 | Data as <type> | Aim: 0 | step: 0 | mode: 1

:data.txt:line:2 => b
b + "-" => b
b => :data.txt:line:2
```

**Data** (`samples/data.txt`, opened in the list):

```text
A: 
B: 
```

**What happens**: two agents (`Mr.Red`, `Mr.Blue`) in two `.cycle` files; each reads its own line of `data.txt`, appends `-` (`+` concatenates when at least one operand is not a number), and writes it back. A writes line 1 (`A: ---`), B writes line 2 (`B: -----`). Each agent runs in its own thread (`ThreadRunner`), so the order of updates between A and B is not guaranteed; the race is visible in `data.txt`.

> [!NOTE]
> **Fact** — cross-file operations use the `cycle:` qualifier: all open files in the list are already linked. (TRUE.md, «Cross-file operations»)

**Python analogue**:

```python
import random
data = ["A: ", "B: "]  # data.txt, two lines
while True:
    data[0] = data[0] + "-"
    data[1] = data[1] + "-"
    print("\n".join(data))
# In true, each agent runs in its own thread; the order between A and B is not guaranteed.
```

---

## !true

### 7. Double (`.fn`)

![double](gifs/double.gif)

**Program** (`samples/double.fn`):

```true
= args
args * 2
= double
```

**What happens**: a pure function `double` — `args * 2`. Called from `true` as `:double`; the result is returned to the caller and stored in `mem["::!double"]`.

> [!NOTE]
> **Fact** — in a `!true` function both `= args` and `= name` are mandatory; no blank lines between them. (NOT_TRUE.md, «Function syntax»)

**Python analogue**:

```python
def double(args):
    return args * 2
```

---

### 8. Concat (`.fn`)

![concat](gifs/concat.gif)

**Program** (`samples/concat.fn`):

```true
= args
Pet
+ rov
= surname

= args
my name is ${=> surname}
= main
```

**What happens**: `+` concatenates strings when at least one operand is not a number; `${=> surname}` calls `surname` and substitutes its result.

> [!NOTE]
> **Fact** — a blank line inside a `!true` function resets the stack. (NOT_TRUE.md, «Stack»)

**Python analogue**:

```python
def surname(args):
    return "Pet" + "rov"

def main():
    return f"my name is {surname('')}"
```

---

### 9. Counter (`.fn`)

![counter_fn](gifs/counter_fn.gif)

**Program** (`samples/counter.fn`):

```true
= args
1
+ 1
= inc
```

**What happens**: first expression `1` is the stack base; `+ 1` applies to the previous result; the function returns `2` to the caller.

> [!NOTE]
> **Fact** — one value per function (no tuples); recursion is allowed with a guard (`depth > 10000`). (NOT_TRUE.md, «Principles (3)», «Recursion»)

**Python analogue**:

```python
def inc(args):
    return 1 + 1
```

---

## See also

- [Full documentation (EN)](README.md)
- [true — Language Specification](TRUE.md)
- [!true — Language Specification](NOT_TRUE.md)
- [Article](article.md)
- [Back to root](../README.md)

---

*Simple v0.28.5. Python 3.8+. Tkinter. No dependencies.*