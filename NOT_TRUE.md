# !true — Language Specification

**Purely functional. Pure functions over a stack.**

**Version**: !true 0.9.6.

**Why "!true"?** Because it is not visual — it does not participate in the step-by-step mode, it runs behind the scenes. And because I made it first, and thought it was not good enough on its own for my goals — but in combination with `true` and `creator` it is pretty good :)

**Note**: `!true` is a pure functional layer. It is called from `true` (or from `creator`). It has no access to the tape; it computes over a stack.

---

## Mental model

**One sentence**: a `.fn` file contains pure functions; each function takes arguments, computes on a stack, and returns one value to the caller.

**Three things**:
1. **Function** — a named block of pure computation (`= args` ... `= name`).
2. **Stack** — the place where values accumulate; `op expr` applies an operation to the previous result.
3. **Caller** — `true` (or `creator`) calls the function and receives one value (`mem["::!name"]`).

**Mandatory lines**: every function has `= args` (the arguments line) and `= funcName` (the function name line). Both are mandatory.

**Format**:

```
= args
<body>
= name
```

---

## What is !true

`.fn` files contain one or more pure functions, separated by blank lines or by `= name`.

Every function starts with `= args` (arguments) and ends with `= name` (name). Both lines are mandatory; no blank lines between `= args`, the body, and `= name`.

**There are no default arguments.** If a function is called without an argument, `args = ""` (empty string). If called with an argument, `args` = the passed value. `arg1`, `arg2`, ... are also available as positional arguments.

Pure functions: result is NOT stored in the function; it is returned to the caller (`mem["::!name"]`).

Blank line inside function resets the stack. Chain accumulates result and calls function with it.

One value per function (no tuples; use true cycle/tape for multiple values).

Extensions: `!true` can call ANY extension from `true`.
- `true`: extension creates container `mem["::name"]`, can be used later.
- `!true`: extension result is used on stack within the call, not persisted.

Recursion: allowed with guard (`depth > 10000`).

Call from true: `:name` (call by name from the open files list).

---

## Comments

`#` starts a comment until the end of the line. A `#` inside `${...}` is not a comment (it belongs to the interpolation expression).

```
= args
Alex
= name # this is a comment
```

`name` returns `Alex`; the comment is ignored.

---

## Quick start (!true)

```
# version: 1
= args
args
+ 1
= func

= args
1
=> func
= main
```

`main` returns `2` (1 + 1); the result is stored in memory (`main = 2`).

Clojure analogue:

```
(defn func [args]
  (+ args 1))

(defn main []
  (func 1))

(main = 2)
```

---

## Function syntax

| Syntax | Meaning |
|---|---|
| `= args` | arguments line (mandatory) |
| `= funcName` | function name line (mandatory; result returned to caller) |
| `expr` | first expression — stack base |
| `op expr` | apply op to previous result |
| `a, b => f1 => f2 => f3` | chain: accumulate, call functions in order |
| `::ext` | extension call (standalone or in chain) |
| `:cycleN` | run a true cycle (fire-and-forget, returns 1/0) |
| `${expr}` / `${=> name}` | interpolation inside an expression |

**Arguments**: `= args` is mandatory. If the function is called without an argument, `args = ""`. If called with an argument, `args` = the passed value. Positional arguments are available as `arg1`, `arg2`, ...

**No default arguments**: `N = args` is not supported. Use `args = ""` and check `args` in the body if you need a default.

**Example** (no arguments):

```
= args
123
= func1
```

`func1` returns `123` regardless of `args` (body does not use `args`).

---

## String concatenation

`+` concatenates strings when at least one operand is not a number:

```
= args
Pet
+ rov
= surname
```

`surname` returns `Petrov`.

```
= args
Pet + rov
= surname
```

`surname` returns `Petrov` (fallback in `FN_EXPR`: `A + B` is concatenated when not numeric).

---

## Interpolation

Inside an expression, `${...}` is replaced by the computed value:

- `${expr}` — evaluate `expr` (like `eval_expr(expr, mem)`).
- `${=> name}` — call function `name` with no arguments, substitute its result.

```
= args
Alex
= name

= args
Pet
+ rov
= surname

= args
my name is ${=> name} and surname is ${=> surname}
= main
```

`main` returns `my name is Alex and surname is Petrov`.

---

## Stack

- First expression — stack base.
- `op expr` — apply op to previous result.
- Blank line inside function resets the stack.
- Chain accumulates result and calls the function with it.
- One value per function (no tuples).

**Result returns to the tape**: when you call a function with `=> func`, the result comes back to the tape (stack), and the tape continues computing. Example:

```
= args
args
+ 1
= func1

= args
args
+ 1
= func2

= args
1
+ 1
=> func1
+ 1
=> func2
= main
```

`func1` returns `2`; the tape continues with `+ 1` (now `3`); `func2` returns `3`; `main = 3`.

Clojure analogue:

```
(defn func1 [args]
  (+ args 1))

(defn func2 [args]
  (+ args 1))

(defn main []
  (func2 (+ (func1 1) 1)))

(main = 3)
```

---

## Extensions

`!true` can call ANY extension from `true`:

- `::math` — arithmetic.
- `::nothing` — no-op (or delete).
- `::gen` — generate a new file from a template.
- `::check` — validate a file.
- `::agent:*` — read the agent.
- `::creator:*` — UI control.
- `:cycleN` — run a true cycle (fire-and-forget, returns 1/0).

---

## Call from true

| Syntax | Meaning |
|---|---|
| `:name` | call `!true` function `name` (from the open files list) |
| `:cycleN` | run `true` cycle N (fire-and-forget, returns 1/0) |

---

## EBNF

```
program      = function { "\n" function } ;
function     = "= args" { expr_line | op_line | chain_line | ext_line | cycle_line | interp_line } "= name" ;
expr_line    = expr ;
op_line      = op expr ;
chain_line   = expr { "," expr } "=>" name { "=>" name } ;
ext_line     = "::" ext_name ;
cycle_line   = ":" "cycle" num ;
interp_line  = { text | "${" ( expr | "=>" name ) "}" } ;
op           = "+" | "-" | "*" | "/" | "%" | "^" ;
name         = { letter | digit | "_" | "." } - reserved ;
ext_name     = "math" | "nothing" | "gen" | "check" | "agent:" name | "creator:" name | "!" name ;
```

**Both `= args` and `= name` are mandatory, no blank lines between them. Default args (`N = args`) are NOT supported.**

---

## Examples

### Example 1: Simple function

```
= args
args * 2
= double
```

Call from true:

```
5 = n
0 = result
n => :double => result
```

`double` returns `10` (5 * 2); the result is stored in `result` (`result = 10`).

### Example 2: Two functions, one uses the other

```
= args
args * args
= square

= args
args => square => :square => sum
= sum_of_squares
```

`sum_of_squares` returns `16` (square(2) = 4; square(4) = 16); the result is stored in `sum_of_squares = 16`.

### Example 3: Chain with extension

```
= args
args => ::math => inc
= main

= args
args
+ 1
= inc
```

`main` returns `6` (5 * 1 + 1); the result is stored in `main = 6`.

### Example 4: Run a true cycle from !true

```
= args
:cycle1
= main
```

`main` returns `1` (cycle1 runs, returns 1/0); the result is stored in `main = 1`.

### Example 5: String concatenation and interpolation

```
= args
Alex
= name

= args
Pet
+ rov
= surname

= args
my name is ${=> name} and surname is ${=> surname}
= main
```

`main` returns `my name is Alex and surname is Petrov`.

---

## Principles (3)

1. **Everything is a pure function.** (a `.fn` file contains pure functions)
2. **Everything is a stack.** (values accumulate; `op expr` applies to the previous result)
3. **One value per function.** (no tuples; use true cycle/tape for multiple values)

---

## Architecture

- `not_true.py` — interpreter of !true (stack, pure functions, parse_fn_file, call_fn).
- `true.py` — core of true (parser, semantics, step_engine, History, EXTENSIONS).
- `creator.py` — heart of the system (Agent, ThreadRunner, languages, extensions, OS, UI bridge).
- `simple.py` — LiveDE, interpreter, presentation layer.
- `modules.py` — shared utilities.

`true` does NOT see `!true`; `!true` does NOT see `true`; all interaction goes through `creator.py`.

---

## FAQ

**Q: Are `= args` and `= funcName` mandatory?**
A: Yes. Every function has `= args` (arguments) and `= funcName` (name). Both lines are mandatory; no blank lines between them.

**Q: Are default arguments supported?**
A: No. `N = args` is not supported. If a function is called without an argument, `args = ""`. If you need a default, check `args` in the body.

**Q: What is a pure function?**
A: A function whose result depends only on its arguments; no side effects. In `!true`, the result is returned to the caller (`mem["::!name"]`), not stored in the function.

**Q: How do I call a !true function from true?**
A: `:name` (call by name from the open files list).

**Q: How do I call a true cycle from !true?**
A: `:cycleN` (fire-and-forget, returns 1/0).

**Q: What happens on a blank line inside a function?**
A: The stack resets.

**Q: What happens on a chain?**
A: The chain accumulates the result and calls the function with it.

**Q: Does the result return to the tape?**
A: Yes. When you call `=> func`, the result comes back to the tape (stack), and the tape continues computing.

**Q: Can a function return multiple values?**
A: No. One value per function (no tuples; use true cycle/tape for multiple values).

**Q: Is recursion allowed?**
A: Yes, with a guard (`depth > 10000`).

**Q: How do comments work?**
A: `#` starts a comment until the end of the line. A `#` inside `${...}` is not a comment.

**Q: How does `+` work on strings?**
A: If at least one operand is not a number, `+` concatenates strings. `Pet + rov` -> `Petrov`; `1 + 2` -> `3`.

**Q: How does interpolation work?**
A: `${expr}` evaluates `expr`; `${=> name}` calls function `name` with no arguments. Both are substituted into the surrounding expression.

---

## Glossary

| Term | Meaning |
|---|---|
| **Function** | a named block of pure computation (`= args` ... `= name`) |
| **`= args`** | arguments line (mandatory); if no argument is passed, `args = ""` |
| **`= funcName`** | function name line (mandatory; result returned to caller) |
| **Stack** | the place where values accumulate; `op expr` applies to the previous result |
| **Caller** | `true` (or `creator`) calls the function and receives one value (`mem["::!name"]`) |
| **Pure function** | a function whose result depends only on its arguments; no side effects |
| **Chain** | `a, b => f1 => f2 => f3` — accumulate, call functions in order |
| **Extension** | `::name` (math, nothing, gen, check, agent:*, creator:*) — not core, added on top |
| **Cycle call** | `:cycleN` — run a `true` cycle (fire-and-forget) |
| **Comment** | `#` until end of line (not inside `${...}`) |
| **Concatenation** | `+` on strings when at least one operand is not a number |
| **Interpolation** | `${expr}` or `${=> name}` inside an expression |