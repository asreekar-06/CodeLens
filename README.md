# CodeLens: Offline Python Code Explainer
Pipeline: Input code -> AST parsing -> rule-based explanation + (optional) CodeT5 summary -> tabs in Streamlit.
Setup: python -m venv venv; activate it; pip install -r requirements.txt; streamlit run app.py
The CodeT5 model (Salesforce/codet5-base-multi-sum) downloads once, then works offline.
Files: core.py (AST engine), summarizer.py (CodeT5), app.py (UI).
