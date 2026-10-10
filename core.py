"""CodeLens core: AST-based explanation, complexity estimate, bug hints, docstrings.
Everything here uses only Python's built-in `ast` module (no ML, no internet)."""
import ast
import builtins
from typing import Optional

LIBS = {"os": "files/paths/OS access", "sys": "interpreter and system access",
        "math": "math functions", "random": "random numbers", "json": "reading/writing JSON",
        "re": "regular expressions", "time": "time functions", "datetime": "dates and times",
        "numpy": "fast numeric arrays", "pandas": "data tables", "matplotlib": "plotting charts",
        "collections": "extra container types", "itertools": "iteration helpers"}

CONCEPTS = {
    "loop": "A loop repeats a block of code many times.",
    "condition": "An if-statement runs code only when a condition is true.",
    "function": "A function is a reusable block of code that takes inputs and may return a result.",
    "recursion": "Recursion means a function calls itself to solve a smaller version of the problem.",
    "class": "A class is a blueprint for creating objects with data and methods.",
    "comprehension": "A comprehension builds a list/dict/set in one compact line.",
    "error handling": "try/except catches errors so the program doesn't crash.",
}


def _s(node) -> str:
    """Convert an AST node back to source text (safe)."""
    try:
        return ast.unparse(node)
    except Exception:
        return "?"


def parse(code: str):
    """Return (tree, error). error is a friendly message if the code is invalid."""
    try:
        return ast.parse(code), None
    except SyntaxError as e:
        return None, f"Syntax error on line {e.lineno}: {e.msg}"


def arg_names(fn) -> list:
    """List the parameter names of a function node."""
    a = fn.args
    names = [x.arg for x in a.posonlyargs + a.args]
    if a.vararg:
        names.append("*" + a.vararg.arg)
    names += [x.arg for x in a.kwonlyargs]
    if a.kwarg:
        names.append("**" + a.kwarg.arg)
    return names


def describe(node) -> str:
    """Plain-English sentence for ONE statement node."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return f"Defines function `{node.name}` taking ({', '.join(arg_names(node)) or 'no inputs'})."
    if isinstance(node, ast.ClassDef):
        b = ", ".join(_s(x) for x in node.bases)
        return f"Defines class `{node.name}`" + (f" inheriting from {b}." if b else ".")
    if isinstance(node, ast.Return):
        return f"Returns `{_s(node.value)}` to the caller." if node.value else "Returns nothing (None)."
    if isinstance(node, ast.Assign):
        return f"Stores `{_s(node.value)}` in `{', '.join(_s(t) for t in node.targets)}`."
    if isinstance(node, ast.AugAssign):
        return f"Updates the variable: `{_s(node)}`."
    if isinstance(node, ast.For):
        return f"Loops: repeats the block for each `{_s(node.target)}` in `{_s(node.iter)}`."
    if isinstance(node, ast.While):
        return f"Loops: repeats the block while `{_s(node.test)}` is true."
    if isinstance(node, ast.If):
        return f"Checks `{_s(node.test)}`; the block runs only if it is true."
    if isinstance(node, ast.Import):
        return "Imports " + ", ".join(
            f"`{a.name}`" + (f" ({LIBS[a.name]})" if a.name in LIBS else "") for a in node.names) + "."
    if isinstance(node, ast.ImportFrom):
        return f"Imports {', '.join(a.name for a in node.names)} from `{node.module}`."
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
        if _s(node.value.func) == "print":
            return f"Prints `{', '.join(_s(a) for a in node.value.args)}` to the screen."
        return f"Calls `{_s(node.value)}`."
    if isinstance(node, ast.Try):
        return "Starts error handling: tries the block and catches exceptions."
    if isinstance(node, ast.ExceptHandler):
        return f"If a `{_s(node.type) if node.type else 'any'}` error happens, runs this block."
    if isinstance(node, ast.With):
        return f"Opens `{', '.join(_s(i.context_expr) for i in node.items)}` and closes it automatically."
    if isinstance(node, ast.Break):
        return "Exits the loop immediately."
    if isinstance(node, ast.Continue):
        return "Skips to the next loop iteration."
    if isinstance(node, ast.Raise):
        return "Raises an error on purpose."
    if isinstance(node, ast.Assert):
        return f"Checks that `{_s(node.test)}` is true, otherwise stops with an error."
    if isinstance(node, ast.Pass):
        return "Does nothing (placeholder)."
    return ""


def line_by_line(code: str, tree) -> list:
    """Return [(line_no, source_line, explanation)] for every non-blank line."""
    notes = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.stmt, ast.ExceptHandler)):
            notes.setdefault(n.lineno, describe(n))
    return [(i, l, notes.get(i, "")) for i, l in enumerate(code.splitlines(), 1) if l.strip()]


def _calls_self(fn) -> int:
    """Count how many times a function calls itself (recursion)."""
    return sum(1 for n in ast.walk(fn) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Name) and n.func.id == fn.name)


def functions(tree) -> list:
    """Summary dict for each function in the code."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append({"name": n.name, "args": arg_names(n), "line": n.lineno, "node": n,
                        "returns": [_s(r.value) for r in ast.walk(n) if isinstance(r, ast.Return) and r.value],
                        "recursive": _calls_self(n) > 0, "doc": ast.get_docstring(n)})
    return out


def overview(tree) -> dict:
    """Count the main constructs used in the code."""
    walk = list(ast.walk(tree))
    count = lambda *t: sum(isinstance(n, t) for n in walk)
    return {"functions": count(ast.FunctionDef, ast.AsyncFunctionDef), "classes": count(ast.ClassDef),
            "loops": count(ast.For, ast.While), "conditions": count(ast.If),
            "comprehensions": count(ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp),
            "try_blocks": count(ast.Try), "imports": count(ast.Import, ast.ImportFrom)}


def key_concepts(tree) -> list:
    """Names of concepts used, to show beginner-friendly definitions."""
    o, used = overview(tree), []
    if o["loops"]: used.append("loop")
    if o["conditions"]: used.append("condition")
    if o["functions"]: used.append("function")
    if any(f["recursive"] for f in functions(tree)): used.append("recursion")
    if o["classes"]: used.append("class")
    if o["comprehensions"]: used.append("comprehension")
    if o["try_blocks"]: used.append("error handling")
    return used


def _loop_depth(node, d=0) -> int:
    """Maximum nesting depth of loops/comprehensions."""
    best = d
    for c in ast.iter_child_nodes(node):
        nd = d + 1 if isinstance(c, (ast.For, ast.While, ast.AsyncFor)) else d
        if isinstance(c, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            nd = d + len(c.generators)
        best = max(best, _loop_depth(c, nd))
    return best


def _halving(node) -> bool:
    """True if a value is repeatedly divided by 2 (binary search style)."""
    for n in ast.walk(node):
        if isinstance(n, (ast.BinOp, ast.AugAssign)) and isinstance(n.op, (ast.FloorDiv, ast.Div, ast.RShift)):
            r = n.right if isinstance(n, ast.BinOp) else n.value
            if isinstance(r, ast.Constant) and isinstance(r.value, (int, float)) and r.value >= 2:
                return True
    return False


def complexity(fn) -> str:
    """Heuristic time-complexity ESTIMATE for a function node."""
    sorts = any(isinstance(n, ast.Call) and _s(n.func).split(".")[-1] in ("sorted", "sort") for n in ast.walk(fn))
    selfcalls = _calls_self(fn)
    depth = _loop_depth(fn)
    if selfcalls >= 2:
        return "O(2^n) - branching recursion"
    if selfcalls == 1:
        return "O(log n) - recursion that halves the input" if _halving(fn) else "O(n) - single recursion"
    if sorts:
        return "O(n log n) - uses sorting"
    if depth == 0:
        return "O(1) - no loops"
    if depth == 1:
        return "O(log n) - loop halves the input" if _halving(fn) else "O(n) - one loop"
    return f"O(n^{depth}) - {depth} nested loops"


def bug_hints(tree) -> list:
    """Static checks. Returns [(line, message)]."""
    hints = []
    imported, loaded = {}, set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: imported[(a.asname or a.name).split(".")[0]] = n.lineno
        elif isinstance(n, ast.ImportFrom):
            for a in n.names: imported[a.asname or a.name] = n.lineno
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            loaded.add(n.id)
        elif isinstance(n, ast.ExceptHandler) and n.type is None:
            hints.append((n.lineno, "Bare `except:` hides real errors. Use `except Exception:` or a specific error."))
        elif isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops) \
                and any(isinstance(c, ast.Constant) and c.value is None for c in n.comparators):
            hints.append((n.lineno, "Use `is None` / `is not None` instead of `== None`."))
        elif isinstance(n, ast.While) and isinstance(n.test, ast.Constant) and n.test.value is True \
                and not any(isinstance(x, (ast.Break, ast.Return)) for x in ast.walk(n)):
            hints.append((n.lineno, "`while True` with no `break`/`return` may loop forever."))
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id in dir(builtins):
            hints.append((n.lineno, f"`{n.id}` shadows a Python built-in. Rename the variable."))
    for name, line in imported.items():
        if name not in loaded:
            hints.append((line, f"Import `{name}` is never used."))
    for f in functions(tree):
        fn = f["node"]
        for d in fn.args.defaults + [d for d in fn.args.kw_defaults if d]:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                hints.append((fn.lineno, f"`{fn.name}` has a mutable default argument. Use `None` and create it inside."))
        stores = {n.id: n.lineno for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
        used = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        for v, ln in stores.items():
            if v not in used and v != "_":
                hints.append((ln, f"Variable `{v}` is assigned but never used."))
        last = fn.body[-1]
        if f["returns"] and not isinstance(last, (ast.Return, ast.Raise)) and not (isinstance(last, ast.If) and last.orelse):
            hints.append((fn.lineno, f"`{fn.name}` returns a value on some paths but may end without returning (gives None)."))
    return sorted(set(hints))


def make_docstring(fn, summary: Optional[str] = None) -> str:
    """Google-style docstring template for a function node."""
    args = [a for a in arg_names(fn) if a not in ("self", "cls")]
    lines = [f'"""{(summary or "Describe what " + fn.name + " does").rstrip(".")}.', ""]
    if args:
        lines += ["Args:"] + [f"    {a.lstrip('*')}: Description of {a.lstrip('*')}." for a in args] + [""]
    if any(isinstance(n, ast.Return) and n.value for n in ast.walk(fn)):
        lines += ["Returns:", "    Description of the returned value."]
    return "\n".join(lines).rstrip() + '\n"""'
