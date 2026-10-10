"""CodeLens - Streamlit UI. Run: streamlit run app.py"""
import streamlit as st
import core

SAMPLES = {
    "Factorial (recursion)": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nprint(factorial(5))",
    "Bubble sort": "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n - i - 1):\n            if arr[j] > arr[j + 1]:\n                arr[j], arr[j + 1] = arr[j + 1], arr[j]\n    return arr",
    "Binary search": "def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
    "Buggy example": "import os\n\ndef add_item(item, items=[]):\n    unused = 5\n    list = [1, 2]\n    try:\n        items.append(item)\n    except:\n        pass\n    if item == None:\n        return items\n",
}

st.set_page_config(page_title="CodeLens", layout="wide")
st.title("CodeLens: Offline Python Code Explainer")
st.caption("Paste Python code and get an explanation, complexity estimate, bug hints and docstrings. Runs fully offline.")

with st.sidebar:
    sample = st.selectbox("Sample code", list(SAMPLES))
    use_ai = st.toggle("Use AI summary (CodeT5)")
    level = st.radio("Detail level", ["Beginner", "Intermediate"])

up = st.file_uploader("Or upload a .py file", type="py")
code = st.text_area("Python code", up.read().decode("utf-8") if up else SAMPLES[sample], height=280)

if st.button("Explain", type="primary"):
    if not code.strip():
        st.warning("Please enter some code.")
        st.stop()
    if len(code.splitlines()) > 300:
        st.warning("Code is over 300 lines. Only the first 300 are analysed.")
        code = "\n".join(code.splitlines()[:300])
    tree, err = core.parse(code)
    if err:
        st.error(err)
        st.stop()

    funcs = core.functions(tree)
    summaries = {}
    if use_ai:
        try:
            with st.spinner("Running CodeT5 (first run loads the model)..."):
                from summarizer import summarize_functions
                summaries = summarize_functions(code, tree)
        except Exception as e:
            st.warning(f"AI summary unavailable, showing rule-based explanation only. ({e})")

    t1, t2, t3, t4, t5 = st.tabs(["Explanation", "Line-by-Line", "Complexity", "Bug Hints", "Docstrings"])
    report = ["CODELENS REPORT", "=" * 40]

    with t1:
        o = core.overview(tree)
        st.subheader("Overview")
        cols = st.columns(len(o))
        for c, (k, v) in zip(cols, o.items()):
            c.metric(k.replace("_", " ").title(), v)
        st.subheader("Functions")
        for f in funcs:
            line = f"`{f['name']}({', '.join(f['args'])})` (line {f['line']}): returns {', '.join('`'+r+'`' for r in f['returns']) or 'nothing'}."
            if f["recursive"]:
                line += " It is **recursive** (calls itself)."
            st.markdown("- " + line)
            if f["name"] in summaries:
                st.markdown(f"  - AI summary: *{summaries[f['name']]}*")
            report.append(line.replace("`", "").replace("*", ""))
        if not funcs:
            st.write("No functions defined.")
        st.subheader("Key concepts")
        for c in core.key_concepts(tree):
            st.markdown(f"- **{c}**" + (f": {core.CONCEPTS[c]}" if level == "Beginner" else ""))

    with t2:
        rows = core.line_by_line(code, tree)
        report += ["", "LINE BY LINE"]
        for no, src, note in rows:
            a, b = st.columns([2, 3])
            a.code(f"{no:>3} | {src}", language="python")
            b.write(note)
            report.append(f"{no}: {src.strip()}  ->  {note}")

    with t3:
        report += ["", "COMPLEXITY (estimate)"]
        for f in funcs:
            c = core.complexity(f["node"])
            st.markdown(f"- `{f['name']}`: **{c}**")
            report.append(f"{f['name']}: {c}")
        st.caption("This is a heuristic estimate based on loops and recursion, not a proof.")

    with t4:
        hints = core.bug_hints(tree)
        report += ["", "BUG HINTS"]
        for ln, msg in hints:
            st.warning(f"Line {ln}: {msg}")
            report.append(f"Line {ln}: {msg}")
        if not hints:
            st.success("No issues found.")

    with t5:
        for f in funcs:
            st.code(core.make_docstring(f["node"], summaries.get(f["name"])), language="python")

    st.download_button("Download explanation (.txt)", "\n".join(report), "codelens_report.txt")
