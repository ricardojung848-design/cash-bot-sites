import ast
from pathlib import Path
from typing import Any, List, Dict
from doctor_core.logging import log_doctor


class AutoDocs:
    """
    MEGA-PRO-Version:
    - Analysiert autonom alle Python-Dateien im Projekt (Core & Modules)
    - Extrahiert dynamisch Klassen, Methoden und Docstrings via Abstract Syntax Trees (AST)
    - Generiert eine strukturierte, professionelle Markdown-Dokumentation
    - Aktualisiert die Dokumentation synchron zur Laufzeit nach System-Erweiterungen
    """

    def __init__(self, engine_manager: Any = None):
        self.engines = engine_manager
        self.base_dir = Path(__file__).resolve().parent.parent
        self.modules_dir = self.base_dir / "modules"
        self.core_dir = self.base_dir / "doctor_core"
        self.docs_dir = self.base_dir / "docs"
        self.output_file = self.docs_dir / "README_MODULES.md"

    def generate(self) -> bool:
        """Scannt die Verzeichnisse, extrahiert die Metadaten und schreibt die System-Doku."""
        log_doctor("AutoDocs: Starte autonome Generierung der System-Dokumentation.")

        # Verzeichnisse absichern
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        all_modules_data: Dict[str, List[Dict[str, Any]]] = {
            "Doctor Core (Zentrale)": self._parse_directory(self.core_dir),
            "Dynamische Module (Erweiterungen)": self._parse_directory(self.modules_dir)
        }

        total_files = sum(len(files) for files in all_modules_data.values())
        if total_files == 0:
            log_doctor("AutoDocs: Keine Quellcodedateien zur Dokumentation lokalisiert.")
            return False

        # Markdown generieren
        try:
            markdown_content = self._build_markdown(all_modules_data)
            self.output_file.write_text(markdown_content, encoding="utf-8")
            log_doctor(f"AutoDocs: Dokumentation erfolgreich exportiert -> {self.output_file.name}")
            return True
        except Exception as e:
            log_doctor(f"AutoDocs: Fehler beim Schreiben der Dokumentationsdatei: {e}")
            return False

    def _parse_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Liest ein Verzeichnis aus und parst alle Python-Dateien strukturell."""
        parsed_files = []
        if not directory.exists():
            return parsed_files

        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix == ".py" and not file_path.name.startswith("_"):
                try:
                    file_info = self._parse_python_file(file_path)
                    parsed_files.append(file_info)
                except Exception as e:
                    log_doctor(f"AutoDocs: Überspringe Datei {file_path.name} wegen Parse-Fehler: {e}")
        
        return parsed_files

    def _parse_python_file(self, file_path: Path) -> Dict[str, Any]:
        """Nutzt AST, um Klassen und Methoden sicher zu analysieren, ohne den Code auszuführen."""
        code = file_path.read_text(encoding="utf-8")
        tree = ast.parse(code)
        
        file_doc = ast.get_docstring(tree) or "Keine Modul-Beschreibung hinterlegt."
        classes_info = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                class_doc = ast.get_docstring(node) or "Keine Klassen-Beschreibung vorhanden."
                methods = []
                
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        method_doc = ast.get_docstring(sub_node) or "Keine Dokumentation."
                        methods.append({
                            "name": sub_node.name,
                            "doc": method_doc.split("\n")[0] # Nur die erste Zeile für die Übersicht
                        })
                
                classes_info.append({
                    "name": node.name,
                    "doc": class_doc,
                    "methods": methods
                })

        return {
            "filename": file_path.name,
            "doc": file_doc,
            "classes": classes_info
        }

    def _build_markdown(self, data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Erzeugt das finale, saubere Markdown-Layout."""
        import time
        generation_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        md = f"# 🩺 Agent Doctor - System- & Modul-Dokumentation\n"
        md += f"> *Generiert am: {generation_time} (Autonome PRO-Dokumentation)*\n\n"
        md += "---\n\n"

        for section_name, files in data.items():
            md += f"## 📁 {section_name}\n\n"
            if not files:
                md += "*Keine aktiven Komponenten in dieser Sektion.*\n\n"
                continue

            for file in files:
                md += f"### 📄 Modul: `{file['filename']}`\n"
                md += f"*{file['doc'].strip()}*\n\n"
                
                for cls in file["classes"]:
                    md += f"#### 🏛️ Klasse: `{cls['name']}`\n"
                    md += f"> {cls['doc'].strip()}\n\n"
                    
                    if cls["methods"]:
                        md += "| Methode / Funktion | Kurzbeschreibung |\n"
                        md += "| :--- | :--- |\n"
                        for method in cls["methods"]:
                            md += f"| `{method['name']}()` | {method['doc']} |\n"
                        md += "\n"
                md += "---\n\n"
        
        return md