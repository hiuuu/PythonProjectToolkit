
# **Python Project Toolkit**

A collection of powerful CLI tools for Python developers to analyze, document, and improve their projects. This toolkit includes:

1. **Project Summarizer**: Analyzes Python projects, generates structure summaries, and identifies undocumented code.
2. **LLM CLI**: Communicates with Large Language Models (LLMs) for code analysis and documentation generation.
3. **Project Scaffolder**: Creates minimal Python project structures with best practices.

---

## **Features**

### **Project Summarizer**
- Generates tree-like project structure visualizations.
- Identifies documented and undocumented code elements.
- Provides AI-ready prompts for project analysis and improvement.
- Automatically updates `.gitignore` to exclude generated files.

### **LLM CLI**
- Communicates with LLM APIs (e.g., OpenRouter) for code analysis.
- Caches API responses to reduce costs and improve performance.
- Supports customizable prompts and model parameters.

### **Project Scaffolder**
- Creates minimal Python project structures with essential files.
- Supports multiple templates (basic, web, data-science).
- Integrates Git initialization and virtual environment creation.

---

## **Installation**

### **Prerequisites**
- Python 3.8 or higher
- `pip` for package management

### **Steps**
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/python-project-toolkit.git
   cd python-project-toolkit
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your API key (optional for LLM features):
   - Create a `.env` file in the project root:
     ```env
     OPENROUTER_API_KEY=your_api_key_here
     ```

---

## **Usage**

### **Project Summarizer**
Analyze a Python project:
```bash
python project_summarizer.py /path/to/your/project
```

#### **Options**
| **Flag**            | **Description**                                      | **Example**                              |
|----------------------|------------------------------------------------------|------------------------------------------|
| `-o`, `--output-dir` | Specify output directory for analysis files          | `-o ./reports`                           |
| `--summary-file`     | Custom filename for project summary                  | `--summary-file overview.txt`            |
| `--undocumented-file`| Custom filename for undocumented code elements       | `--undocumented-file missing_docs.txt`   |
| `--no-gitignore`     | Disable `.gitignore` updates                         | `--no-gitignore`                         |
| `-v`, `--verbose`    | Enable verbose logging for debugging                 | `-v`                                     |

---

### **LLM CLI**
Communicate with an LLM:
```bash
python llm_cli.py "Your prompt here"
```

#### **Options**
| **Flag**            | **Description**                                      | **Example**                              |
|----------------------|------------------------------------------------------|------------------------------------------|
| `-f`, `--file`       | Read prompt from a file                              | `-f input.txt`                           |
| `-o`, `--output`     | Save output to a file                                | `-o output.txt`                          |
| `-m`, `--model`      | Specify LLM model                                    | `-m meta-llama/llama-3.2-1b-instruct`    |
| `-t`, `--temperature`| Set sampling temperature                             | `-t 0.7`                                 |
| `--api-key`          | Use a custom API key                                 | `--api-key $CUSTOM_KEY`                  |
| `--api-url`          | Use a custom API endpoint                            | `--api-url https://custom-api.example.com`|

---

### **Project Scaffolder**
Create a new Python project:
```bash
python create_project.py my_project
```

#### **Options**
| **Flag**            | **Description**                                      | **Example**                              |
|----------------------|------------------------------------------------------|------------------------------------------|
| `-t`, `--template`   | Project template (basic, web, data-science)          | `-t web`                                 |
| `-g`, `--git`        | Initialize Git repository                            | `-g`                                     |
| `-v`, `--venv`       | Create virtual environment                           | `-v`                                     |
| `-r`, `--requirements`| Add packages to `requirements.txt`                  | `-r "flask,pandas>=1.4.0"`               |

---

## **Output Examples**

### **Project Summarizer**
1. **Project Summary** (`project_summary_*.txt`):
   ```text
   Project Structure:
   my_project/
   ├── src/
   │   ├── __init__.py
   │   └── main.py
   ├── tests/
   └── README.md

   File: src/main.py
     Function: main
       Documentation: No documentation...
   ```

2. **Undocumented Code** (`undocumented_code_*.txt`):
   ```text
   File: src/main.py | Element: Function | Name: main
   ```

---

### **LLM CLI**
Example output:
```text
The main function serves as the entry point for the application. It initializes the program and calls other necessary functions.
```

---

### **Project Scaffolder**
Generated structure:
```text
my_project/
├── src/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── __init__.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## **Development**

### **Dependencies**
- `requests` for API communication.
- `python-dotenv` for environment variable management.
- `argparse` for CLI argument parsing.
- `pathlib` for cross-platform path handling.

### **Running Tests**
```bash
python -m pytest tests/
```

### **Contributing**
1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature-name`.
3. Commit your changes: `git commit -m "Add your feature"`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request.

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## **Acknowledgments**

- Built with ❤️ by Hamed Zandieh (hamed.zandieh@gmail.com).
- Inspired by the need for better project documentation and scaffolding tools.
- Special thanks to the Python community for amazing libraries and tools.

---

## **Support**

For questions, issues, or feature requests, please [open an issue](https://github.com/hiuuu/EfficientCoding/issues).



