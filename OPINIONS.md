
---

OPINIONS.md — один блок для копирования

```markdown
# Opinions about the stack create + true + !true + simple

Literary stylization. Each author speaks through the lens of his own work: what he did first, what he thinks about the product (functionality, philosophy, parts, whole, axis), and advice to the author as a human being (not about fixing the product, but about life and bringing the idea to life).

**4 groups**: language creators (10), book authors (6), thinkers (17), product creators (6) — 39 opinions in total.

---

## Group 1 — Language creators (10)

### Konrad Zuse — Plankalkül

**Who**: Konrad Zuse, creator of Plankalkül.

**What he did first**:
- Plankalkül (1942–1945) — the first universal programming language.
- The first language treating code and data in one notation.
- The first formal plan (program as a plan).

**What he thinks about the product**:
- **Functionality**: true treats code and data in one notation (cycle/tape of lines); !true treats computation in one notation (pure functions on a stack); Simple shows both in one window.
- **Philosophy**: "true is what can be used" — an engineering philosophy: if it works, it is truth. "Programming must be open, visual, easy and beautiful" — the philosophy of a plan made visible.
- **Parts**: true is the notation for code and data, !true is the pure computation layer, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: one notation for everything, visible to the user.
- **Axis**: one notation for everything, visible to the user.

**Advice to the author**:
> "I built Plankalkül on paper because there was no machine. You build on a machine that already works. That is a great gift — don't waste it on perfection. A plan that runs is better than a plan that is only on paper."

*Did you know? In true, each line is like a qubit: a black box for the agent until it is read — just like a qubit collapses when measured.*

### Grace Hopper — COBOL

**Who**: Grace Hopper, creator of COBOL.

**What she did first**:
- COBOL (1959) — the first compiler turning English-like statements into machine code.
- The first language designed for business readability.
- The first to make programs portable across machines.

**What she thinks about the product**:
- **Functionality**: true compiles lines into actions; !true compiles pure functions into values; Simple makes both portable.
- **Philosophy**: "true is what can be used" — the philosophy of readability: truth is in what a person can read. "Programming must be open, visual, easy and beautiful" — the philosophy of COBOL: readable, portable, for people.
- **Parts**: true is the readable language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: readable text that machines and people understand, portable.
- **Axis**: readable text that machines and people understand, portable.

**Advice to the author**:
> "I had to fight to make computers read English. You don't have to fight — your language already reads like a person wrote it. Keep it that way. And remember: a program that a manager can read is worth ten programs that only a programmer can read."

*Did you know? In true, the agent line is fixed at the top in the UI; the tape moves step by step; the executing line is highlighted — so the agent's parameters are always visible.*

### Ken Thompson — B

**Who**: Ken Thompson, creator of B.

**What he did first**:
- B (1969) — the first language small enough to fit on one page but complete.
- The first language where everything is an expression.
- The first step to C.

**What he thinks about the product**:
- **Functionality**: true has seven line types, five operators, four jump forms — the whole language on one page; !true has pure functions only; Simple has one window.
- **Philosophy**: "true is what can be used" — the philosophy of smallness: truth is in what fits on one page. "Programming must be open, visual, easy and beautiful" — the philosophy of B: small, minimal, complete.
- **Parts**: true is the small language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: small, minimal, complete — on one page.
- **Axis**: small, minimal, complete — on one page.

**Advice to the author**:
> "B was small because we had no memory. You have memory, but you still keep it small. That is rare. Don't let anyone talk you into adding features just because there is space."

*Did you know? In true, `=>|` and `->|` are different operations: `=>|` inserts a copy into an axis (source kept), `->|` inserts and moves (source removed).*

### Niklaus Wirth — Pascal

**Who**: Niklaus Wirth, creator of Pascal.

**What he did first**:
- Pascal (1970) — the first language designed for teaching with clear structure.
- The first language where the compiler teaches the programmer.
- The first with structured programming as core.

**What he thinks about the product**:
- **Functionality**: true teaches by showing the agent reading lines; !true teaches by showing values flowing on a stack; Simple teaches by showing type, aim, step.
- **Philosophy**: "true is what can be used" — the philosophy of teaching: truth is in what a student can see. "Programming must be open, visual, easy and beautiful" — the philosophy of Pascal: clear structure, visible to the user.
- **Parts**: true is the teaching language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: learn by seeing — the system teaches the user.
- **Axis**: learn by seeing — the system teaches the user.

**Advice to the author**:
> "I made Pascal so that a student could see the whole language at once. Your product has the same quality — a student can see the whole cycle/tape at once. Protect this quality. A language that is easy to learn is easy to love."

*Did you know? In true, `::gen` copies a template (by name or path), substitutes `$name`/`_name`, and adds the new file to the list — generation is just copying and substituting.*

### Dennis Ritchie — C

**Who**: Dennis Ritchie, creator of C.

**What he did first**:
- C (1972) — the first language close to the machine but portable.
- The first language where the programmer has full trust.
- The first language that became the base of an operating system.

**What he thinks about the product**:
- **Functionality**: true trusts the agent to read and change lines; !true trusts the pure function to compute; Simple shows what happens — no hidden state.
- **Philosophy**: "true is what can be used" — the philosophy of trust: truth is in what a programmer can trust. "Programming must be open, visual, easy and beautiful" — the philosophy of C: trust with clear rules, portable.
- **Parts**: true is the trusted language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: trust with clear rules, portable.
- **Axis**: trust with clear rules, portable.

**Advice to the author**:
> "C was small because we needed it to run on a PDP-11. You have a modern machine, but you keep the core small. That is the right instinct. The machine will change; the core should not."

*Did you know? In true, `?=>` evaluates the source expression before copying — so `a + b ?=> c` writes the sum into `c`, not the expression text.*

### Alan Kay — Smalltalk

**Who**: Alan Kay, creator of Smalltalk.

**What he did first**:
- Smalltalk (1972) — the first language where objects exchange messages.
- The first language with a live environment.
- The first language where everything is an object.

**What he thinks about the product**:
- **Functionality**: true has lines exchanging meaning through the agent (=> is send, -> is move, <-> is swap); !true has pure functions exchanging values through the stack; Simple shows both live.
- **Philosophy**: "true is what can be used" — the philosophy of liveness: truth is in what is alive. "Programming must be open, visual, easy and beautiful" — the philosophy of Smalltalk: message-passing, live, visible.
- **Parts**: true is the message-passing language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: message-passing, live — but with lines and pure functions instead of objects.
- **Axis**: message-passing, live — but with lines and pure functions instead of objects.

**Advice to the author**:
> "Smalltalk was not built to be a language — it was built to be a way of thinking. Your product has the same quality: it is not just a language, it is a way of thinking about a program as a tape of lines. Protect this way of thinking."

*Did you know? In true, the agent line is fixed at the top, and the tape moves step by step; the executing line is highlighted — the observer is fixed, the observed moves by steps.*

### Bjarne Stroustrup — C++

**Who**: Bjarne Stroustrup, creator of C++.

**What he did first**:
- C++ (1983) — the first language with abstraction without loss.
- The first language where abstractions compile to the same machine code.
- The first with zero-cost abstractions.

**What he thinks about the product**:
- **Functionality**: true has explicit operators (=>| vs ->| differ, y is \n, Aim and step: N visible); !true has explicit pure functions (one value per call, blank line resets); Simple shows type, aim, step.
- **Philosophy**: "true is what can be used" — the philosophy of abstraction without loss: truth is in what compiles to the same code. "Programming must be open, visual, easy and beautiful" — the philosophy of C++: abstraction, zero-cost, explicit.
- **Parts**: true is the explicit language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: abstraction without loss — every operator, every function, every line is explicit.
- **Axis**: abstraction without loss — every operator, every function, every line is explicit.

**Advice to the author**:
> "C++ grew because every feature had to pay for itself. Your product has the same discipline: seven line types, five operators, four jump forms — every feature pays for itself. Keep this discipline."

*Did you know? In true, a jump can be `^ N`, `^ name`, `^ :cycle:N`, or `^ :cycle:name` — the agent can jump to a line number or to a named line, in the current file or across files.*

### Larry Wall — Perl

**Who**: Larry Wall, creator of Perl.

**What he did first**:
- Perl (1987) — the first language with "there's more than one way to do it".
- The first language where everything is text.
- The first with regular expressions built in.

**What he thinks about the product**:
- **Functionality**: true is "everything is a line"; !true is "everything is a pure function"; extensions (::math, ::gen, ::check, ::agent:*, ::creator:*) are added on top.
- **Philosophy**: "true is what can be used" — the philosophy of text: truth is in what is text. "Programming must be open, visual, easy and beautiful" — the philosophy of Perl: text-first, extension-friendly.
- **Parts**: true is the text language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: text-first, extension-friendly — but with one way (line) and pure functions.
- **Axis**: text-first, extension-friendly — but with one way (line) and pure functions.

**Advice to the author**:
> "I made Perl so that a programmer could do anything quickly. You made true so that a programmer can do one thing well. Both are needed. But yours is harder — and more valuable. Keep it."

*Did you know? In true, the `::` prefix is for extensions (math, nothing, gen, check, agent, creator), and the `:` prefix is for calling a !true function by name from the open files list.*

### Guido van Rossum — Python

**Who**: Guido van Rossum, creator of Python.

**What he did first**:
- Python (1991) — the first language with readability as the first principle.
- The first with significant indentation.
- The first with a REPL as core experience.

**What he thinks about the product**:
- **Functionality**: Data as <type> is live feedback (like a REPL); AgentBar shows type, aim, step, and the `●` indicator; !true pure functions return one value; names cannot contain operators (validator).
- **Philosophy**: "true is what can be used" — the philosophy of readability: truth is in what a person can read. "Programming must be open, visual, easy and beautiful" — the philosophy of Python: readable, predictable, visible.
- **Parts**: true is the readable language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: readable, predictable, visible — live feedback.
- **Axis**: readable, predictable, visible — live feedback.

**Advice to the author**:
> "I designed Python for myself first. You designed true for yourself first. That is the right order. A language designed for a committee is a language designed for no one."

*Did you know? In true, the agent line is fixed at the top in the UI, and the executing line is highlighted — so you always see what the agent is reading right now.*

### Yukihiro Matsumoto — Ruby

**Who**: Yukihiro Matsumoto, creator of Ruby.

**What he did first**:
- Ruby (1995) — the first language with programmer joy as the first principle.
- The first language designed for happiness.
- The first with "least surprise" as core.

**What he thinks about the product**:
- **Functionality**: observer joy — the agent reads the cycle/tape, changes it, updates the type, shows step: N; the `●` indicator shows when the agent is running (colored by agent's color); !true computes purely and returns one value; Simple renders both.
- **Philosophy**: "true is what can be used" — the philosophy of joy: truth is in what brings joy. "Programming must be open, visual, easy and beautiful" — the philosophy of Ruby: joy, least surprise, visible.
- **Parts**: true is the joyful language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: joy from watching the system work — observer joy (instead of programmer joy).
- **Axis**: joy from watching the system work — observer joy (instead of programmer joy).

**Advice to the author**:
> "I designed Ruby to make programmers happy. You designed true to make the observer happy — the one who watches the agent read the tape. That is a new kind of joy. Don't lose it."

*Did you know? In true, `::agent:finish` stops the agent and updates the UI — you can end a program from within the program.*

---

## Group 2 — Book authors (6)

### Andrew Hunt, David Thomas — The Pragmatic Programmer

**Who**: Andrew Hunt and David Thomas, authors of The Pragmatic Programmer.

**What he did first**:
- The Pragmatic Programmer (1999) — the first book to make pragmatism (DRY, tracer bullets, "fix the problem, not the blame") the core of programming practice.
- The first to make "your knowledge portfolio" a concept.
- The first to make "good enough software" a principle.

**What he thinks about the product**:
- **Functionality**: true avoids duplication (one line type per line); !true avoids side effects (pure functions); Simple shows the tracer (type, aim, step, `●`).
- **Philosophy**: "true is what can be used" — the philosophy of pragmatism: truth is in what works. "Programming must be open, visual, easy and beautiful" — the philosophy of the Pragmatic Programmer.
- **Parts**: true is the pragmatic language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: pragmatism for the user — fix the program, not the blame.
- **Axis**: pragmatism for the user — fix the program, not the blame.

**Advice to the author**:
> "We wrote 'good enough software' because perfection kills projects. Your product is good enough. Ship it. Listen to the users. Improve it. That is the pragmatic way."

*Did you know? In true, a cycle wraps to line 0, and a tape stops at the last line — the same agent logic, two execution modes.*

### David Glickstein — Facts and Fallacies of Software Engineering

**Who**: David Glickstein (with Andrew Hunt, David Thomas), author of Facts and Fallacies of Software Engineering.

**What he did first**:
- Facts and Fallacies of Software Engineering (2002) — the first book to collect facts and fallacies of software engineering in one place.
- The first to separate facts from fallacies systematically.
- The first to make "the gap between theory and practice" a topic.

**What he thinks about the product**:
- **Functionality**: true separates facts (line types) from fallacies (what a line is not); !true separates pure functions from side effects; Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of facts: truth is in what is a fact. "Programming must be open, visual, easy and beautiful" — the philosophy of Facts and Fallacies.
- **Parts**: true is the factual language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: facts made visible — the user sees what is, not what is guessed.
- **Axis**: facts made visible — the user sees what is, not what is guessed.

**Advice to the author**:
> "There are more facts than fallacies in software engineering, but the fallacies are louder. Your product is a fact — it runs, it works, it can be tested. Let the facts speak."

*Did you know? In true, `::check` validates an object by checking that all `;`-separated substrings are present in the file — a simple fact-check.*

### Robert C. Martin — Clean Code

**Who**: Robert C. Martin, author of Clean Code.

**What he did first**:
- Clean Code (2008) — the first book to make "clean code" — readable, simple, testable — the core of a programmer's book.
- The first to make naming a discipline.
- The first to make "code smells" a catalog.

**What he thinks about the product**:
- **Functionality**: true has clear line types (named, action, condition); !true has clear pure functions (one value per call); Simple shows type, aim, step.
- **Philosophy**: "true is what can be used" — the philosophy of clean code: truth is in what is clean. "Programming must be open, visual, easy and beautiful" — the philosophy of Clean Code.
- **Parts**: true is the clean language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: clean code for the user — readable, predictable, visible.
- **Axis**: clean code for the user — readable, predictable, visible.

**Advice to the author**:
> "I wrote Clean Code because I was tired of reading bad code. Your product is already clean — one line type per line, one value per function, one window. Keep it clean. Cleanliness is a discipline, not a one-time effort."

*Did you know? In true, names cannot contain operator characters or separators — the validator enforces this, so a name can always be parsed back.*

### Aditya Bhargava — Grokking Algorithms

**Who**: Aditya Bhargava, author of Grokking Algorithms.

**What he did first**:
- Grokking Algorithms (2016) — the first book to make algorithms visual — pictures and simple language — the core of an algorithms book.
- The first to make "grokking" a method.
- The first to make algorithms accessible to beginners.

**What he thinks about the product**:
- **Functionality**: true shows the agent, the cycle/tape, Data as <type> — a user sees the algorithm in action; !true shows the stack and the chain — a user sees values flow; Simple renders both, with `●` indicator showing when the agent is running.
- **Philosophy**: "true is what can be used" — the philosophy of visual algorithms: truth is in what you can see. "Programming must be open, visual, easy and beautiful" — the philosophy of Grokking Algorithms.
- **Parts**: true is the visual language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: algorithms made visual — a user sees the algorithm in action.
- **Axis**: algorithms made visual — a user sees the algorithm in action.

**Advice to the author**:
> "I drew pictures because words alone were not enough. You drew the tape — the agent, the lines, the type. That is the same idea. Keep drawing."

*Did you know? In true, `?=>` evaluates the source expression before copying — so `a + b ?=> c` writes the sum into `c`, not the expression text.*

### Bruce Eckel — Thinking in Java

**Who**: Bruce Eckel, author of Thinking in Java.

**What he did first**:
- Thinking in Java (1998) — the first book to make "thinking in a language" — the mental model before the syntax — the core of a language book.
- The first to make "the mental model" explicit.
- The first to make a language book a course.

**What he thinks about the product**:
- **Functionality**: true teaches the mental model (agent, cycle/tape, Data as <type>); !true teaches the mental model (pure functions, stack, caller stores); Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of the mental model: truth is in what you think. "Programming must be open, visual, easy and beautiful" — the philosophy of Thinking in Java.
- **Parts**: true is the thinking language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: thinking made visible — a user thinks in lines and pure functions before writing.
- **Axis**: thinking made visible — a user thinks in lines and pure functions before writing.

**Advice to the author**:
> "I wrote Thinking in Java because syntax is easy, thinking is hard. Your product has a mental model: the agent, the cycle/tape, the type. Teach this model first, syntax second."

*Did you know? In true, the mental model is: the agent reads the tape step by step, the agent line is fixed at the top, the executing line is highlighted — the model is visible in the UI.*

### Donald Knuth — The Art of Computer Programming

**Who**: Donald Knuth, author of The Art of Computer Programming.

**What he did first**:
- The Art of Computer Programming (1968–) — the first to make "the art of computer programming" — algorithms as art, analysis as science — the core of a multi-volume work.
- The first to make analysis of algorithms a discipline.
- The first to make "literate programming" a concept.

**What he thinks about the product**:
- **Functionality**: true separates art (the agent reading lines) from science (the formal parser, the invariants); !true separates art (the pure function) from science (the stack, the guard); Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of art and science: truth is in what is both. "Programming must be open, visual, easy and beautiful" — the philosophy of The Art of Computer Programming.
- **Parts**: true is the art-and-science language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: art and science together — a user sees both at once.
- **Axis**: art and science together — a user sees both at once.

**Advice to the author**:
> "I spent years on literate programming because code is written for humans first, machines second. Your product writes for humans first — the agent, the tape, the type. Keep this order."

*Did you know? In true, `::gen` copies a template (by name or path), substitutes `$name`/`_name`, and adds the new file to the list — generation is just copying and substituting.*

---

## Group 3 — Thinkers (17)

### Richard Feynman — "Explain it simply"

**Who**: Richard Feynman, physicist, teacher.

**What he did first**:
- Feynman diagrams (1949) — the first visual tool for quantum electrodynamics.
- The first to make "if you can't explain it simply, you don't understand it" the first principle of teaching.
- The first to teach physics through simple pictures.

**What he thinks about the product**:
- **Functionality**: the agent walks the cycle/tape, reads a line, executes it, changes memory, changes places with the next line; !true computes pure functions on a stack; Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of explanation: truth is in what you can explain. "Programming must be open, visual, easy and beautiful" — the philosophy of Feynman.
- **Parts**: true is the explained language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: explainable tools — a user can explain this in one minute.
- **Axis**: explainable tools — a user can explain this in one minute.

**Advice to the author**:
> "I drew diagrams because equations were not enough. You drew the tape because code was not enough. That is the same instinct. Trust it."

*Did you know? In true, a condition is true if its value is not empty, not `"0"`, not `"False"`, and not undefined — truth is what can be used.*

### Niels Bohr — Complementarity

**Who**: Niels Bohr, physicist.

**What he did first**:
- Complementarity (1927) — the first to make complementarity — two descriptions of the same system, each true in its own frame — the core of physics.
- The first to make the observer part of the system.
- The first to make measurement a concept.

**What he thinks about the product**:
- **Functionality**: in true a line has meaning only at the moment of reading (Data as <type>); in !true a value has meaning only on the stack; Simple shows both views at once.
- **Philosophy**: "true is what can be used" — the philosophy of complementarity: truth is in what is both. "Programming must be open, visual, easy and beautiful" — the philosophy of Bohr.
- **Parts**: true is the complementarity language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: complementarity in programming — two views, both true.
- **Axis**: complementarity in programming — two views, both true.

**Advice to the author**:
> "I spent my life on complementarity because two views are better than one. You have two views: true and !true. Do not try to merge them into one. The tension is the value."

*Did you know? In true, `::agent:finish` stops the agent, but `::agent:name` just reads the agent's name — the same `::agent:*` family does both control and read.*

### Eliyahu Goldratt — Theory of Constraints

**Who**: Eliyahu Goldratt, management consultant.

**What he did first**:
- Theory of Constraints (1984) — the first to make "a system is limited by its constraint" the core of management.
- The first to make the constraint the lever for improvement.
- The first to make "the goal" explicit.

**What he thinks about the product**:
- **Functionality**: the constraint of true is its contract (seven line types, five operators, four jump forms); the constraint of !true is its purity (one value per function, blank line resets); the constraint of Simple is its window.
- **Philosophy**: "true is what can be used" — the philosophy of constraints: truth is in what is the constraint. "Programming must be open, visual, easy and beautiful" — the philosophy of Goldratt.
- **Parts**: true is the constrained language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: constraint as contract — the user relies on it.
- **Axis**: constraint as contract — the user relies on it.

**Advice to the author**:
> "I made a career of finding the one constraint that limits everything. Your constraint is the core: seven line types, five operators, four jump forms. Protect it. Everything else is an extension."

*Did you know? In true, the extension `::agent:*` is the only way the language talks to the agent — the agent itself is part of Creator.*

### Genrich Altshuller — TRIZ

**Who**: Genrich Altshuller, inventor, engineer.

**What he did first**:
- TRIZ (1946) — the first to make contradiction resolution (separation, inversion, mediation) the core of invention.
- The first to make TRIZ a method.
- The first to make invention teachable.

**What he thinks about the product**:
- **Functionality**: separation in time: true separates reading and execution; !true separates computation (stack) from storage (caller). Separation in space: true separates cycle/tape (lines) from memory (containers); !true separates pure functions from side effects (which live in true). Inversion: in true the agent is both executor and observer; in !true the function is pure and the caller stores. Mediation: ::gen generates objects from templates, ::check validates them, Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of contradiction resolution: truth is in what resolves a contradiction. "Programming must be open, visual, easy and beautiful" — the philosophy of TRIZ.
- **Parts**: true is the separation-in-time language, !true is the separation-in-space computation, **Creator is the heart**, Simple is the mediation, modules is the shared part.
- **Whole**: TRIZ principles applied to a product — separation, inversion, mediation.
- **Axis**: TRIZ principles applied to a product — separation, inversion, mediation.

**Advice to the author**:
> "I learned TRIZ in a prison cell because I had nothing else to do. You have a machine, a language, a product. You have no excuse. Resolve contradictions — that is the only real work."

*Did you know? In true, `::gen` generates a new file from a template, and `::check` validates it — generation and validation are separated, like TRIZ's separation in time.*

### Nassim Taleb — Antifragility

**Who**: Nassim Taleb, risk analyst, essayist.

**What he did first**:
- Antifragility (2012) — the first to make antifragility — a system that gains from stress — the core of risk analysis.
- The first to make "black swan" a concept.
- The first to make robustness a spectrum (fragile, robust, antifragile).

**What he thinks about the product**:
- **Functionality**: true has a formal parser (EBNF) and unambiguous escape (placeholder); !true has one value per function and a guard against deep recursion; Simple shows type, aim, step and highlights the executing line.
- **Philosophy**: "true is what can be used" — the philosophy of antifragility: truth is in what survives stress. "Programming must be open, visual, easy and beautiful" — the philosophy of Taleb.
- **Parts**: true is the antifragile language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: antifragility for the user — works the same way every time.
- **Axis**: antifragility for the user — works the same way every time.

**Advice to the author**:
> "I spent my life on what survives black swans. Your product survives because it is small, formal, and predictable. Do not add complexity to look smart. Complexity is what kills in a black swan."

*Did you know? In true, the escape `\` before an operator makes it literal — the parser has an unambiguous escape, so a line never changes meaning by accident.*

### Lao Tzu — Simplicity

**Who**: Lao Tzu, philosopher.

**What he did first**:
- Tao Te Ching (6th century BC) — the first to make wu-wei — action through non-action — the core of philosophy.
- The first to make simplicity a principle.
- The first to make "the Tao that can be expressed is not the eternal Tao" a concept.

**What he thinks about the product**:
- **Functionality**: everything in true is a line, everything in !true is a pure function; a user writes lines and formulas, and the stack does the rest.
- **Philosophy**: "true is what can be used" — the philosophy of wu-wei: truth is in what acts without forcing. "Programming must be open, visual, easy and beautiful" — the philosophy of Lao Tzu.
- **Parts**: true is the way, !true is the non-action, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: wu-wei — action through simplicity.
- **Axis**: wu-wei — action through simplicity.

**Advice to the author**:
> "The Tao that can be expressed is not the eternal Tao. The program that can be written is not the eternal program. Do not try to write the eternal program. Write the one that works today."

*Did you know? In true, a program is a cycle or a tape of lines — nothing more. The simplicity is the point.*

### Alan Turing — Computability

**Who**: Alan Turing, mathematician, logician.

**What he did first**:
- Turing machine (1936) — the first formal model of computation.
- The first to make computability a formal concept.
- The first to make the halting problem a concept.

**What he thinks about the product**:
- **Functionality**: true emulates MT (mem["tape"], mem["head"], mem["state"], Aim as halt); !true computes pure functions and calls true cycles; Simple shows both.
- **Philosophy**: "true is what can be used" — the philosophy of computability: truth is in what can be computed. "Programming must be open, visual, easy and beautiful" — the philosophy of Turing.
- **Parts**: true is the computable language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: computability made visible.
- **Axis**: computability made visible.

**Advice to the author**:
> "I built a machine on paper because I wanted to know what a machine can do. You built a machine that runs. Now ask: what can it do that no other machine can do? That is the real question."

*Did you know? True is Turing-complete: it emulates a Turing machine via `mem["tape"]`, `mem["head"]`, `mem["state"]`, and `Aim` as the halt condition.*

### Semyon Korsakov — Ontologies and AI

**Who**: Semyon Korsakov, physician, pioneer of knowledge representation.

**What he did first**:
- Knowledge graphs (1832) — the first to make ontologies (knowledge graphs) the core of knowledge representation.
- The first to make semantic networks a concept.
- The first to make machine reasoning a goal.

**What he thinks about the product**:
- **Functionality**: true has entities (lines, containers) and relations (cycle: qualifier); !true has pure transformations; Simple shows the ontology as a live cycle/tape; ::gen generates objects, ::check validates them.
- **Philosophy**: "true is what can be used" — the philosophy of ontology: truth is in what is related. "Programming must be open, visual, easy and beautiful" — the philosophy of Korsakov.
- **Parts**: true is the ontology language, !true is the pure computation, **Creator is the heart**, Simple is the window, modules is the shared part.
- **Whole**: ontology in action.
- **Axis**: ontology in action.

**Advice to the author**:
> "I built knowledge graphs with cards because I wanted a machine to reason. You built a machine that reasons over lines. Do not lose the graph — the relations are what matters."

*Did you know? In true, `cycle:name` gives file identity, `name` inside a file gives container identity, and `cycle:name:sub` gives qualified identity (file + container).*

### Alexander Bogdanov — Tektology

**Who**: Alexander Bogdanov, physician, philosopher, pioneer of systems theory.

**What he did first**:
- Tektology (1912–1917) — the first to make tektology — a universal organizational science — before cybernetics and systems theory.
- The first to show that organization is a property of any system (natural, technical, social).
- The first to introduce "complex" (a whole of elements) and "link" (a relation between elements) as universal concepts.

**What he thinks about the product**:
- **Functionality**: true is a complex of lines linked by the agent (line = element, agent = link); !true is a complex of pure functions linked by the stack (function = element, stack = link); Simple is a complex of widgets linked by App (widget = element, App = link); ::gen and ::check are organizational operations.
- **Philosophy**: "true is what can be used" — the philosophy of organization: truth is in what is organized. "Programming must be open, visual, easy and beautiful" — the philosophy of Bogdanov.
- **Parts**: true is the complex of lines, !true is the complex of functions, **Creator is the heart**, Simple is the complex of widgets, modules is the shared part.
- **Whole**: organization of elements and links — complex as a whole.
- **Axis**: organization of elements and links — complex as a whole.

**Advice to the author**:
> "I wrote Tektology in exile because I wanted to understand how things are organized. You built a product that is organized: line, agent, link. Do not lose the organization — it is the whole point."

*Did you know? In true, the agent is the link between lines: it reads a line, determines its type, executes the instruction, and moves on — the organization is the agent.*

### Paramahansa Yogananda — Yoga and meditation

**Who**: Paramahansa Yogananda, yogi, author of Autobiography of a Yogi.

**What he did first**:
- Autobiography of a Yogi (1946) — the first book to bring yoga and meditation to the Western reader.
- The first to make Kriya Yoga accessible to the general public.
- The first to show that spiritual practice and ordinary life are not opposites.

**What he thinks about the product**:
- **Functionality**: the agent reads the cycle/tape, changes places with the next line, updates its type. This is a practice — step by step, with attention.
- **Philosophy**: "true is what can be used" — the philosophy of practice: truth is in what you practice. "Programming must be open, visual, easy and beautiful" — the philosophy of Yogananda: work as practice, practice as work.
- **Parts**: true is the practice of attention (the agent reads one line at a time), !true is the practice of detachment (pure functions, no side effects), **Creator is the heart**, Simple is the window (the practice of observation), modules is the shared part.
- **Whole**: work as practice — the agent reads, the user watches, the practice deepens.
- **Axis**: work as practice — the agent reads, the user watches, the practice deepens.

**Advice to the author**:
> "I taught that meditation is not an escape from life but a way to live more fully. Your product is the same: it is not an escape from programming but a way to program more fully. Do not rush. The agent reads one line at a time. You read one line at a time. That is enough."

*Did you know? In true, the agent reads one line at a time — the whole system is built on the discipline of one step at a time.*

### Marcus Aurelius — Stoicism

**Who**: Marcus Aurelius, Roman emperor, Stoic philosopher.

**What he did first**:
- Meditations (c. 170–180 AD) — the first personal journal of Stoic practice by a world leader.
- The first to make Stoicism a daily practice (not just a theory).
- The first to show that power and humility can coexist.

**What he thinks about the product**:
- **Functionality**: the agent reads the cycle/tape, one line at a time. It does not rush. It does not skip. It does not complain. This is Stoic discipline.
- **Philosophy**: "true is what can be used" — the philosophy of Stoicism: truth is in what you can act on. "Programming must be open, visual, easy and beautiful" — the philosophy of Marcus Aurelius: do what is in front of you, do it well, let go of the rest.
- **Parts**: true is the discipline of the agent (one line at a time), !true is the discipline of the pure function (one value, no side effects), **Creator is the heart**, Simple is the discipline of the observer (watch, do not interfere), modules is the shared part.
- **Whole**: discipline as practice — the agent reads, the user watches, the work is done.
- **Axis**: discipline as practice — the agent reads, the user watches, the work is done.

**Advice to the author**:
> "You have power over your product — not over the opinions of others, not over the market, not over the future. Do what is in front of you: one line, one function, one step. The rest is not yours to control."

*Did you know? In true, the agent does not rush: it reads one line, executes it, moves to the next — the discipline is built into the execution model.*

### William of Ockham — Nominalism, parsimony

**Who**: William of Ockham, Franciscan friar, logician, nominalist.

**What he did first**:
- Ockham's razor (c. 1320) — the first to make "entities are not to be multiplied beyond necessity" a principle of reasoning.
- The first to make nominalism a systematic position (universals are not real, only particulars are).
- The first to separate logic from metaphysics in a systematic way.

**What he thinks about the product**:
- **Functionality**: true has seven line types, five operators, four jump forms. !true has pure functions only. Simple has one window. Entities are not multiplied.
- **Philosophy**: "true is what can be used" — the philosophy of parsimony: truth is in what is necessary. "Programming must be open, visual, easy and beautiful" — the philosophy of Ockham: do not multiply entities beyond necessity.
- **Parts**: true is the necessary language, !true is the necessary computation, **Creator is the heart**, Simple is the necessary window, modules is the shared part.
- **Whole**: do not multiply entities beyond necessity.
- **Axis**: do not multiply entities beyond necessity.

**Advice to the author**:
> "I cut away universals because they were not necessary. You cut away complexity because it was not necessary. Keep cutting. The razor is not a one-time tool — it is a daily practice."

*Did you know? In true, there are only seven line types and five operators — entities are not multiplied.*

### Alexei Alexeevich Ukhtomsky — Dominant, physiology

**Who**: Alexei Alexeevich Ukhtomsky, physiologist, creator of the dominant theory.

**What he did first**:
- The dominant (1923) — the first theory of the dominant focus of excitation in the nervous system.
- The first to show that behavior is organized around a dominant focus.
- The first to make the concept of "functional organ" a physiological reality.

**What he thinks about the product**:
- **Functionality**: the agent is a dominant focus — it reads the cycle/tape, and everything else is organized around this reading. The type (Data as <type>) is the dominant; the line is the stimulus; the memory is the functional organ.
- **Philosophy**: "true is what can be used" — the philosophy of the dominant: truth is in what organizes behavior. "Programming must be open, visual, easy and beautiful" — the philosophy of Ukhtomsky: the dominant organizes the whole.
- **Parts**: true is the dominant (the agent reads), !true is the functional organ (the stack organizes values), **Creator is the heart**, Simple is the observer (the window), modules is the shared part.
- **Whole**: the dominant organizes the whole — the agent reads, the system organizes around it.
- **Axis**: the dominant organizes the whole — the agent reads, the system organizes around it.

**Advice to the author**:
> "I discovered the dominant by watching a frog's reflex. You discovered your product by watching an agent read a line. The principle is the same: one focus organizes everything. Protect your focus. Do not let it be distracted."

*Did you know? In true, the agent is the dominant focus: everything in the system is organized around its reading of lines.*

### Nikola Tesla — Flow, resonance

**Who**: Nikola Tesla, inventor, engineer.

**What he did first**:
- AC motor (1888) — the first practical alternating current motor.
- Tesla coil (1891) — the first resonant transformer.
- Radio (1893) — the first demonstration of wireless communication (before Marconi).
- Wardenclyffe Tower (1901) — the first attempt at wireless power transmission.

**What he thinks about the product**:
- **Functionality**: the agent reads the cycle/tape, executes, changes places — this is a flow, like alternating current. !true computes pure functions on a stack — this is a resonance, like a Tesla coil. Simple shows both — this is the transmission.
- **Philosophy**: "true is what can be used" — the philosophy of flow: truth is in what flows. "Programming must be open, visual, easy and beautiful" — the philosophy of Tesla: flow, resonance, transmission.
- **Parts**: true is the flow (the agent reads), !true is the resonance (the pure function), **Creator is the heart**, Simple is the transmission (the window), modules is the shared part.
- **Whole**: flow, resonance, transmission — the system as a whole.
- **Axis**: flow, resonance, transmission — the system as a whole.

**Advice to the author**:
> "I died alone in a hotel room with a notebook full of ideas. Do not die with a notebook full of ideas. Release them. Even the ones that are not finished. The world will finish them — or forget them. But at least they will exist."

*Did you know? In true, the tape moves step by step and the agent line is fixed at the top — the flow is visible, not hidden.*

---

## Group 4 — Product creators (6)

### Steve Wozniak (1976 — Apple I)

**Who**: Steve Wozniak, co-founder of Apple, engineer.

**What he did first**:
- Apple I (1976) — the first personal computer assembled in a garage and sold as a finished product.
- Apple II (1977) — the first mass-market personal computer with color graphics and an open architecture.
- Disk II (1978) — the first low-cost floppy disk drive for a personal computer.
- Wizardry (1980) — port of the first commercial RPG to Apple II.

**What he thinks about the product**:
- **Functionality**: Simple as IDE + Creator as heart + two languages (true and !true) is like the Apple II: an open architecture for the user (editor, AgentBar, buttons) and an engineering heart under the hood.
- **Philosophy**: "true is what can be used" — an engineering philosophy: if it works, it is truth. "Programming must be open, visual, easy and beautiful" — the philosophy of the Apple II.
- **Parts**: Simple is the face (like the Apple II case), **Creator is the heart** (like the motherboard), true/!true are the languages (like BASIC and assembler), modules is the shared part (like the chipset).
- **Whole**: the product is whole: the user sees Simple, and under the hood is Creator + true + !true.
- **Axis**: open architecture, engineering heart.

**Advice to the author**:
> "I built Apple I in a garage because I wanted a computer of my own. You built true because you wanted a language of your own. That is the same motivation — and the same joy. Do not lose the joy."

*Did you know? In true, the extension `::creator:*` controls the UI (play/pause/step/stepBack/restart/new/open/save/close/exit) — the same prefix works for control and read.*

### Steve Jobs (1976 — Apple I)

**Who**: Steve Jobs, co-founder of Apple, visionary.

**What he did first**:
- Apple I (1976) — the first personal computer sold as a finished product (with Wozniak).
- Apple II (1977) — the first mass-market personal computer designed for people.
- Macintosh (1984) — the first mass-market computer with a graphical interface and a mouse.
- iPod (2001) — the first mass-market MP3 player with a simple interface.
- iPhone (2007) — the first mass-market smartphone with a multi-touch interface.

**What he thinks about the product**:
- **Functionality**: Simple is the face of the product. Like the Macintosh: the user does not see the internals, he sees the editor, AgentBar, buttons.
- **Philosophy**: "true is what can be used" — the philosophy of simplicity: truth is not in complexity, but in use. "Programming must be open, visual, easy and beautiful" — the Apple philosophy.
- **Parts**: Simple is the face (like the Macintosh), **Creator is the heart** (like the Motorola 68000), true/!true are the languages (like QuickDraw and System), modules is the shared part (like ROM).
- **Whole**: the product is whole, but the face is more important than the internals.
- **Axis**: the face is the product.

**Advice to the author**:
> "I fired people who did not believe in the Macintosh. Do not fire anyone — but do not let anyone talk you out of the face. The face is what the user sees. The face is the product."

*Did you know? In true, the agent line is fixed at the top in the UI, and the executing line is highlighted — the face of the product shows the agent's work.*

### Linus Torvalds (1991 — Linux)

**Who**: Linus Torvalds, creator of Linux.

**What he did first**:
- Linux (1991) — the first mass-market open operating system with a kernel written from scratch by one person.
- Git (2005) — the first distributed version control system, created in two weeks.
- "Just for fun" (2001) — the first hacker autobiography told in simple language.
- "Talk is cheap. Show me the code" — a principle that became a catchphrase.

**What he thinks about the product**:
- **Functionality**: Talk is cheap. Show me the code. The code is there: simple.py (UI), creator.py (heart), true.py / not_true.py (languages), modules.py (shared).
- **Philosophy**: "true is what can be used" — the Linux philosophy: if it works, it is truth. "Programming must be open, visual, easy and beautiful" — the open-source philosophy.
- **Parts**: Simple is the face (DE), **Creator is the heart** (kernel), true/!true are the languages (shell and C), modules is the shared part (libc).
- **Whole**: the product is whole, but the core is more important than the face.
- **Axis**: the core is more important than the face.

**Advice to the author**:
> "I released Linux 0.01 with a note that it was not ready. It was not. But people started using it. Release your 0.01. It does not need to be ready. It needs to be out."

*Did you know? In true, `true` does not see `!true`, and `!true` does not see `true` — all interaction goes through Creator, just like the kernel isolates subsystems.*

### Sid Meier (1991 — Civilization)

**Who**: Sid Meier, creator of Civilization, game designer.

**What he did first**:
- Civilization (1991) — the first turn-based strategy with an open simulation of civilization development.
- Railroad Tycoon (1990) — the first economic simulation of railways.
- Pirates! (1987) — the first open sandbox with pirates.
- "A game is a series of interesting decisions" — a principle that became a catchphrase.

**What he thinks about the product**:
- **Functionality**: A game is a series of interesting decisions. Your product is the same: the agent decides which line to read; the user decides what to write; ::gen decides which template to take; ::check decides whether the description is correct.
- **Philosophy**: "true is what can be used" — the Civilization philosophy: truth is in what works in the game. "Programming must be open, visual, easy and beautiful" — the game design philosophy.
- **Parts**: Simple is the face (game UI), **Creator is the heart** (simulation), true/!true are the languages (rules and formulas), modules is the shared part (engine).
- **Whole**: the product is whole, but interesting decisions are more important than features.
- **Axis**: a series of interesting decisions.

**Advice to the author**:
> "I designed Civilization so that a player would want to play one more turn. Design your product so that a user would want to write one more line. One more line. That is the whole secret."

*Did you know? In true, each step is an interesting decision: the agent reads the next line, determines its type, and executes it — one step at a time.*

### Leonardo da Vinci (1490 — aerial screw, Vitruvian Man)

**Who**: Leonardo da Vinci, artist, inventor, polymath.

**What he did first**:
- Aerial screw (1490) — the first design of a helicopter-like flying machine.
- Vitruvian Man (1490) — the first systematic study of human proportions.
- Anatomical drawings (1510) — the first systematic anatomical drawings.
- Codex Atlanticus (1478–1519) — the first large collection of notebooks covering art, science, and engineering together.

**What he thinks about the product**:
- **Functionality**: the agent reads the cycle/tape, executes, changes places — this is a study of a living system, like the Vitruvian Man. !true computes pure functions on a stack — this is a study of a pure form. Simple shows both — this is the notebook.
- **Philosophy**: "true is what can be used" — the philosophy of study: truth is in what you study. "Programming must be open, visual, easy and beautiful" — the philosophy of Leonardo: art and science are one.
- **Parts**: true is the study of the living system (the agent), !true is the study of the pure form (the function), **Creator is the heart**, Simple is the notebook (the window), modules is the shared part.
- **Whole**: art and science together — a user sees both at once.
- **Axis**: art and science together — a user sees both at once.

**Advice to the author**:
> "I left thousands of pages of notes because I could not stop studying. You built a product that is a study: the agent, the tape, the type. Do not stop studying. The product is not finished — it is a study that continues."

*Did you know? In true, the agent reads one line at a time — the study is in the detail, not in the whole at once.*