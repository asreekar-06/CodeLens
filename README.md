CodeLens — Offline Python Code Explainer

CodeLens is a Python code explanation tool that helps developers and beginners understand Python programs through **AST-based static analysis, rule-based explanations, complexity estimates, bug hints, and optional AI-powered summaries**.

The application provides an interactive Streamlit interface that turns Python source code into structured, beginner-friendly insights.

Features

- Code Overview: Counts functions, classes, loops, conditions, comprehensions, imports, and exception-handling blocks.
- Line-by-Line Explanation: Provides plain-English explanations for supported Python statements.
- Complexity Estimation: Estimates time complexity using heuristic analysis of loops, recursion, and sorting operations.
- Bug Hints: Identifies selected suspicious coding patterns, such as unused imports, unused variables, mutable default arguments, and bare exception handlers.
- Docstring Generation: Generates Google-style docstring templates for Python functions.
- Optional AI Summaries: Uses the CodeT5 model to generate natural-language summaries of functions.
- Beginner and Intermediate Modes: Lets users choose their preferred explanation detail.
- Python File Upload: Accepts .py files for analysis.
- Downloadable Reports: Exports explanations and analysis results as a text file.
- Local Analysis: The core AST-based features work locally without external AI API calls.

How It Works

Python Code Input --> Input Validation --> AST Parsing --> Rule-Based Static Analysis (Code Overview, Line-by-Line Explanation, Complexity Estimate, Bug Hints, Docstring Templates) --> Optional CodeT5 Function Summaries --> Streamlit Results and Downloadable Report

The main analysis engine uses Python's built-in ast module. CodeT5 is an optional component used for function summarization; it does not perform the project's complexity estimation or bug-hint checks.

Tech Stack

- Language: Python
- User Interface: Streamlit
- Static Analysis: Python ast module
- AI Model: Salesforce CodeT5 (Salesforce/codet5-base-multi-sum)
- AI Framework: Hugging Face Transformers
- Model Runtime: PyTorch

Project Structure

CodeLens/
├── app.py
├── core.py
├── summarizer.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore


File & Purpose 
app.py - Streamlit interface and analysis workflow 
core.py - AST parsing, explanations, complexity estimates, bug hints, and docstring templates 
summarizer.py - Optional CodeT5 function summaries 
requirements.txt - Python dependencies 
README.md - Project documentation 

Getting Started

Prerequisites

- Python 3.10 or later recommended
- pip
- Internet access for the initial download of the optional CodeT5 model

1. Clone the repository

git clone https://github.com/asreekar-06/CodeLens.git
cd CodeLens

2. Create a virtual environment

python -m venv venv
.\venv\Scripts\Activate.ps1

If PowerShell blocks activation, you can use Command Prompt and run:

venv\Scripts\activate.bat

3. Install dependencies

python -m pip install -r requirements.txt

4. Launch the application

streamlit run app.py

Streamlit will display a local URL in your terminal. Open that URL in your browser.

Using CodeLens

1. Launch the application.
2. Paste Python code into the editor or upload a .py file.
3. Select the desired explanation level.
4. Enable the optional CodeT5 summary feature if required.
5. Click Explain.
6. Explore the results in the available tabs:
   - Explanation
   - Line-by-Line
   - Complexity
   - Bug Hints
   - Docstrings
7. Download the generated explanation report if needed.

Offline Functionality

The AST-based analysis features run locally and do not require external AI APIs.

The optional CodeT5 model must be downloaded the first time it is used. Once the model and tokenizer are cached locally, AI summaries can run offline, provided the required dependencies and model files are available.

Limitations

- Complexity analysis is heuristic and may not accurately classify every algorithm.
- Bug hints cover selected static patterns and cannot detect every logical or runtime error.
- A result of "No issues found" does not guarantee that the code is bug-free.
- The application limits analysis to 300 lines per submission.
- AI summaries depend on the availability of the local CodeT5 model and its dependencies.
- The current implementation focuses on Python code.

Future Improvements

- Expand static-analysis rules and bug detection.
- Improve complexity estimation for more algorithmic patterns.
- Add unit-test suggestions and test-case generation.
- Support additional programming languages.
- Improve reporting and visualization.
- Add more code examples and automated tests.

License
See the [LICENSE](LICENSE) file for licensing details.

Author
Addepalli Sreekar

GitHub: [@asreekar-06](https://github.com/asreekar-06)

-------------------------------------------------------------------------------

CodeLens — making Python code easier to understand, one statement at a time.
