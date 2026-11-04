# Simple — интерпретатор языка True (полная документация)

**True** — язык программирования, где программа = лента **кубитов** (строк),
а **агент**-наблюдатель шаг за шагом «измеряет» кубиты, меняя их местами.

**Simple** — кроссплатформенный интерпретатор на Python 3 + Tkinter.
Один файл, без зависимостей.

> **Статус**: MVP. True — полноценный язык с собственной концепцией:
> он может развиваться как самостоятельный язык.

| Язык | Документация | Статья |
|---|---|---|
| **English** | [../README.md](../README.md) | [../article.md](../article.md) |
| **Русский** | этот файл | [article.md](article.md) |

Назад в корень: [../../README.md](../../README.md)

---

## Быстрый старт

```bash
python3 simple.py           # запуск UI
python3 simple.py --test    # тесты
```

Требования: **Python 3.8+** (Tkinter входит в стандартную поставку).

---

## Как пользоваться

| Действие | Результат |
|---|---|
| ▶ / ⏸ | play / pause |
| ⏭ | **один шаг** |
| ⏮ | reset (agent=0, memory={}) |
| `+` | добавить цикл |
| поле `ms` | пауза между шагами (по умолчанию 390) |
| клик в редактор | **авто-пауза**, можно править |
| ПКМ в редакторе | Copy / Paste / Cut / Select All |
| `Space` | play / pause |

После правки — ▶ Play, агент идёт по **новому** коду.

---

## Программа по умолчанию (main.cycle)

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

## Концепция

| Понятие | Что это |
|---|---|
| **Цикл** (cycle) | программа = список строк |
| **Кубит** | строка; значение зависит от наблюдателя |
| **Агент** (agent) | наблюдатель; строка `Name, #hex \| Data as <type> \| Aim: cond` |
| **`<type>`** | тип, который агент **распознал** на текущей строке (обновляется каждый шаг) |
| **Цепочки кубитов** | агент маркирует все строки до `separator` как один блок |
| **`::name`** | расширение (`::math`, `::nothing`) |

### Типы строк

| Тип | Синтаксис | Что делает |
|---|---|---|
| `agent` | `Name, #hex \| Data as <t> \| Aim:` | маркер |
| `separator` | `""` / `---` | граница блока |
| `named` | `val = name(, name2)` | `mem[name] = val` (`= x` → `x=""`) |
| `container` | `text` | литерал |
| `action` | `src op dst` (цепочка) | `=>` `->` `<->` `=>\|` `->\|` |
| `condition` | `cond ? act` | если `cond ≠ 0` → `act` |
| `jump` | `^ name` / `^ N` / `^ :cycle:N` | прыжок |

### Операторы

| Оператор | Семантика |
|---|---|
| `=>` | copy |
| `->` | move |
| `=>\|` | insert-copy в ось (с `sep`) |
| `->\|` | insert-move в ось |
| `<->` | swap |
| `::nothing` | `->` удаляет, `=>` no-op |
| `::math` | `mem["::math"] = eval(src)` |

### Оси

| Синтаксис | sep по умолчанию |
|---|---|
| `name:x(sep):idx` | `""` (символы) |
| `name:y(sep):idx` | `","` |

`idx` = `1`-based, `first`, `last`, `all`.

### Прыжки

| Синтаксис | Куда |
|---|---|
| `^ name` | к `named`-строке с именем `name` |
| `^ N` | на строку `N` (1-based) |
| `^ :cycle:N` | в цикл `cycle` на строку `N` |

#### Пример прыжка (два цикла) — F106

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

Агент прыгает из `main.cycle` в `helper.cycle` (строка 1), затем обратно в `main.cycle` (строка 2).

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

**Приоритеты** (сверху — выше):
`agent > separator > jump > condition > action > named > container`

---

## Подсветка синтаксиса

| Тип | Цвет | Фон |
|---|---|---|
| agent | `#5fb85f` (мягкий зелёный) | `#1e2a1e` |
| named | `#5b9bd5` (синий) | — |
| action | `#7fb069` (зелёный) | — |
| act (внутри condition) | `#7fb069` (зелёный) | — |
| cond | `#e8c547` (жёлтый) | — |
| op (`=>`, `->`, `=>\|`, `<->`) | `#a8d888` (светло-зелёный) | `#2a2a3a` |
| jump | `#b07fd5` (фиолетовый) | — |
| container | `#888888` (серый) | — |
| separator | `#444444` (тёмный) | — |

---

## Возможности

| Что | Да / Нет |
|---|---|
| Несколько циклов (`+`) | ✅ |
| Кросс-цикловые прыжки `^ :cycle:N` | ✅ |
| Оси `x`/`y` с `sep` | ✅ |
| Цепочки `a => b => c` | ✅ |
| `::math` (арифметика, булевы) | ✅ |
| `::nothing` (имя / ось / строка) | ✅ |
| Подсветка синтаксиса | ✅ |
| Step (один шаг) | ✅ |
| Логи в `simple.log` / `simple_test.log` | ✅ |
| Escape `\=>` | ✅ |
| Комментарии `#` | ❌ |
| Пользовательские `::functions` | ❌ (только `math`, `nothing`) |
| Сохранение `.cycle` на диск | ❌ |
| Загрузка `.cycle` | ❌ |

---

## Тесты

```bash
python3 simple.py --test
```

**Ожидаемый вывод** (`simple_test.log`):

```
=== Simple tests v0.16.2 ===
  T1 named: PASS
  ...
  T22 default program: PASS

24/24 passed
```

---

## Логи

| Файл | Что |
|---|---|
| `simple.log` | лог UI-сессии (`[step]`, `[type]`, `[exec]`, `[flush]`, `[swap]`) |
| `simple_test.log` | лог тестов |

Логи **перезаписываются** при каждом запуске.

---

## Ограничения (честно)

| # | Ограничение |
|---|---|
| 1 | Один файл `simple.py` — для демо, не для продакшена |
| 2 | Regex-парсинг — хрупок при нестандартном синтаксисе |
| 3 | Нет сохранения/загрузки `.cycle` |
| 4 | Нет комментариев в языке |
| 5 | `::` — только `math` и `nothing` |
| 6 | `flush` пишет в `lines` (не в `Text` напрямую) |
| 7 | Нет области видимости (всё `per-cycle`) |
| 8 | Нет истории `mem` (только текущее) |
| 9 | **Нет маркера версии `.cycle` (`# version: N`) — планируется** — F107 |

---

## Философия

- **Кубит = строка** — наглядно
- **Наблюдатель = агент** — оригинально
- **Программа читает и меняет саму себя** — отличие от императивных языков
- **Цепочки кубитов** — группировка без скобок
- **Оси данных** — списки в одном кубите
- **`Data as <type>`** — живая обратная связь
- **Один файл** — простота копирования

---

## См. также

- [Статья (RU)](article.md)
- [Full documentation (EN)](../README.md)
- [Article (EN)](../article.md)
- [Назад в корень](../../README.md)

---

## Лицензия

MIT | 2026 | Автор — Александр Кундрюков (a.kundryukov@gmail.com)