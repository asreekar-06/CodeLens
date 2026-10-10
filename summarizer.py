"""Optional CodeT5 summaries. Runs locally; model downloads once, then works offline."""
import ast

MODEL = "Salesforce/codet5-base-multi-sum"
_cache = {}


def load():
    """Lazy-load tokenizer + model (only when first needed)."""
    if "m" not in _cache:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        _cache["m"] = (AutoTokenizer.from_pretrained(MODEL), AutoModelForSeq2SeqLM.from_pretrained(MODEL))
    return _cache["m"]


def summarize(code: str) -> str:
    """One-line English summary of a code snippet."""
    tok, model = load()
    ids = tok(code, return_tensors="pt", truncation=True, max_length=512).input_ids
    out = model.generate(ids, max_length=40, num_beams=4)
    return tok.decode(out[0], skip_special_tokens=True)


def summarize_functions(code: str, tree) -> dict:
    """{function_name: summary}. Raises if the model is unavailable (app catches it)."""
    res = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            seg = ast.get_source_segment(code, n)
            if seg:
                res[n.name] = summarize(seg)
    return res
