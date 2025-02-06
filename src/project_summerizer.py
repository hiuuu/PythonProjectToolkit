"""
Python Project Analyzer CLI Tool
"""
import argparse
import ast
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
import fnmatch
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class ProjectSummerizer:
    """Main analysis engine with enhanced path handling and error checking"""
    
    def __init__(self, root_dir: Path, output_dir: Path):
        self.root_dir = root_dir.resolve()
        self.output_dir = output_dir.resolve()
        self.ignore_patterns = []
        self.backup_dir = self.output_dir / "backups"

    def load_gitignore_patterns(self, addons=None):
        """Load and process .gitignore patterns with improved regex handling"""
        gitignore_path = self.root_dir / ".gitignore"
        addons = addons or ["tests/", "backups/", "docs/", "test*", "_*"]
        
        patterns = []
        if gitignore_path.exists():
            with gitignore_path.open(encoding='utf-8') as f:
                patterns += [
                    line.strip() for line in f.read().splitlines()
                    if line.strip() and not line.startswith("#")
                ]
                
        patterns.extend(addons)
        self.ignore_patterns = list({self._convert_pattern_to_regex(p) for p in patterns})

    @staticmethod
    def _convert_pattern_to_regex(pattern: str) -> str:
        """Convert .gitignore patterns to regex with proper escaping"""
        pattern = re.escape(pattern.replace("/", os.sep))
        pattern = pattern.replace(r"\*", ".*").replace(r"\.", "\\.")
        
        if pattern.endswith(os.sep):
            pattern = f"^{pattern[:-1]}.*$"
        else:
            pattern = f"^{pattern}$"
            
        return pattern.replace(os.sep, r"[\\/]")

    def generate_summary(self, summary_file: Path, undocumented_file: Path):
        """Main analysis workflow with improved error handling"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        with summary_file.open('w', encoding='utf-8') as sf, \
             undocumented_file.open('w', encoding='utf-8') as uf:

            self._write_file_headers(sf, uf)
            self._generate_structure(sf)
            self._analyze_code(sf, uf)

        self._update_gitignore()
        logging.info(f"Analysis complete: {summary_file}")

    def _write_file_headers(self, summary_file, undocumented_file):
        """Write standardized headers to output files"""
        analysis_prompt = """**AI Analysis Prompt (Copy-Paste Ready):**
        
Analyze this project structure focusing on:
1. Architecture efficiency
2. Code quality metrics
3. Performance bottlenecks
4. Scalability potential

Provide recommendations in this format:
- [High/Medium/Low Impact] [Category] Concise Suggestion (Cost-Benefit Rationale)

Constraints:
- Max 10 key suggestions
- Technical specificity
- Minimal resource prioritization
- No verbose explanations

Example:
- [High] [Arch] Extract shared utils to module (Reduce 40% code duplication)
- [Medium] [Perf] Cache DB queries in user/auth routes (Save ~200ms/request)
    """

        headers = {
            summary_file: [
                "=== Project Summary and AI Analysis Guide ===",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Project Root: {self.root_dir}",
                "\n" + analysis_prompt + "\n",
                "\nProject Structure:\n"
            ],
            undocumented_file: [
                "=== Undocumented Code Elements ===",
                "Use this format for documentation generation:",
                "File: <relative_path> | Element: <type> | Name: <name>"
            ]
        }
        
        for file, lines in headers.items():
            file.write("\n".join(lines) + "\n\n")            

    def _generate_structure(self, output_handle):
        """Generate directory structure visualization"""
        output_handle.write(f"{self.root_dir.name}/\n")
        self._tree_walk(self.root_dir, output_handle, "")

    def _tree_walk(self, current_dir: Path, handle, prefix: str):
        """Recursive directory tree generator"""
        try:
            items = sorted([
                p for p in current_dir.iterdir() 
                if not p.name.startswith('.') and not any(
                    re.search(pattern, str(p)) 
                    for pattern in self.ignore_patterns
                )
            ], key=lambda p: (not p.is_dir(), p.name.lower()))

            for i, path in enumerate(items):
                is_last = i == len(items) - 1
                if path.is_dir():
                    handle.write(f"{prefix}{'└── ' if is_last else '├── '}{path.name}/\n")
                    self._tree_walk(path, handle, prefix + ("    " if is_last else "│   "))
                elif path.suffix == '.py':
                    handle.write(f"{prefix}{'└── ' if is_last else '├── '}{path.name}\n")
        except OSError as e:
            logging.error(f"Directory traversal error: {e}")

    def _analyze_code(self, summary_handle, undocumented_handle):
        """Analyze Python files with AST parsing"""
        for py_file in self.root_dir.rglob("*.py"):
            if any(re.search(p, str(py_file)) for p in self.ignore_patterns):
                continue

            try:
                with py_file.open(encoding='utf-8') as f:
                    self._process_file(
                        ast.parse(f.read(), filename=str(py_file)),
                        py_file,
                        summary_handle,
                        undocumented_handle
                    )
            except (SyntaxError, UnicodeDecodeError) as e:
                logging.warning(f"Skipped {py_file}: {e}")

    def _process_file(self, module, file_path, summary_handle, undocumented_handle):
        """Process individual Python files"""
        rel_path = file_path.relative_to(self.root_dir)
        summary_handle.write(f"\nFile: {rel_path}\n")

        for node in module.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                self._handle_code_element(node, rel_path, summary_handle, undocumented_handle)

    def _handle_code_element(self, node, rel_path, summary_handle, undocumented_handle):
        """Handle class/function definitions with docstring checking"""
        docstring = ast.get_docstring(node) or "No documentation"
        element_type = "Class" if isinstance(node, ast.ClassDef) else "Function"
        
        summary_handle.write(f"  {element_type}: {node.name}\n")
        summary_handle.write(f"    Documentation: {docstring[:100]}...\n")

        if docstring == "No documentation":
            undocumented_handle.write(
                f"File: {rel_path} | Element: {element_type} | Name: {node.name}\n"
            )

    def _update_gitignore(self):
        """Update .gitignore with safety checks"""
        gitignore = self.output_dir / ".gitignore"
        entries = [
            "# Project analysis outputs",
            "project_summary_*.txt",
            "undocumented_code_*.txt",
            "backups/"
        ]

        if gitignore.exists():
            existing = gitignore.read_text(encoding='utf-8')
            entries = [e for e in entries if e not in existing]

        if entries:
            with gitignore.open('a', encoding='utf-8') as f:
                f.write("\n" + "\n".join(entries))

def configure_cli():
    """Set up command line interface with argparse"""
    parser = argparse.ArgumentParser(
        description="Python Project Analysis Toolkit",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        'project_root',
        type=Path,
        nargs='?',
        default=Path.cwd(),
        help="Path to project root directory"
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=Path,
        default=Path.cwd(),
        help="Output directory for analysis files"
    )
    parser.add_argument(
        '--summary-file',
        type=Path,
        help="Custom filename for project summary"
    )
    parser.add_argument(
        '--undocumented-file',
        type=Path,
        help="Custom filename for undocumented elements"
    )
    parser.add_argument(
        '--no-gitignore',
        action='store_true',
        help="Disable .gitignore updates"
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def main():
    """Main CLI execution flow"""
    args = configure_cli()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        analyzer = ProjectSummerizer(args.project_root, args.output_dir)
        analyzer.load_gitignore_patterns()

        summary_file = args.summary_file or analyzer.output_dir / f"project_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        undocumented_file = args.undocumented_file or analyzer.output_dir / f"undocumented_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        analyzer.generate_summary(summary_file, undocumented_file)
        
        if not args.no_gitignore:
            analyzer._update_gitignore()

        print(f"\nAnalysis complete:\n- Summary: {summary_file}\n- Undocumented: {undocumented_file}")

    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
    
"""
USAGE

# Basic usage
python project_analyzer.py /path/to/project

# Custom output directory
python project_analyzer.py -o ./reports

# Custom filenames
python project_analyzer.py --summary-file overview.txt --undocumented-file missing_docs.txt

# Disable .gitignore updates
python project_analyzer.py --no-gitignore

# Verbose output
python project_analyzer.py -v

# Analyze current directory
python project_analyzer.py

# Analyze specific project with custom outputs
python project_analyzer.py ~/projects/myapp -o ./analysis --summary-file myapp_report.txt

# Generate outputs without modifying .gitignore
python project_analyzer.py --no-gitignore

"""