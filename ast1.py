import os
import ast
import json
import importlib.util
import sys
from typing import Dict, Any, List

class PythonProjectParser:
    def __init__(self, project_path: str):
        """
        Initialize the Python Project Parser
        
        :param project_path: Root directory of the Python project
        """
        self.project_path = os.path.abspath(project_path)
        self.project_structure: Dict[str, Any] = {}
        
        # Add project path to Python path to enable import resolution
        sys.path.insert(0, self.project_path)
    
    def _is_python_file(self, filename: str) -> bool:
        """
        Check if a file is a Python source file
        
        :param filename: Name of the file
        :return: Boolean indicating if the file is a Python source file
        """
        return filename.endswith('.py') and not filename.startswith('__')
    
    def _extract_dependencies(self, node: ast.AST) -> List[str]:
        """
        Extract import dependencies from an AST node
        
        :param node: AST node to analyze
        :return: List of imported module names
        """
        dependencies = []
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Import):
                dependencies.extend([alias.name for alias in child.names])
            elif isinstance(child, ast.ImportFrom):
                module = child.module or ''
                dependencies.extend([f"{module}.{alias.name}" for alias in child.names])
        return dependencies
    
    def _parse_function(self, func_node: ast.FunctionDef) -> Dict[str, Any]:
        """
        Parse a function node and extract its details
        
        :param func_node: AST function definition node
        :return: Dictionary with function details
        """
        variables = {}
        for child in ast.iter_child_nodes(func_node):
            if isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        variables[target.id] = ast.unparse(child.value).strip()
        
        return {
            'name': func_node.name,
            'variables': variables,
            'dependencies': self._extract_dependencies(func_node),
            'line_number': func_node.lineno
        }
    
    def _parse_class(self, class_node: ast.ClassDef) -> Dict[str, Any]:
        """
        Parse a class node and extract its details
        
        :param class_node: AST class definition node
        :return: Dictionary with class details
        """
        methods = {}
        class_variables = {}
        
        for child in ast.iter_child_nodes(class_node):
            if isinstance(child, ast.FunctionDef):
                methods[child.name] = self._parse_function(child)
            elif isinstance(child, ast.Assign):
                for target in child.targets:
                    if isinstance(target, ast.Name):
                        class_variables[target.id] = ast.unparse(child.value).strip()
        
        return {
            'name': class_node.name,
            'methods': methods,
            'variables': class_variables,
            'dependencies': self._extract_dependencies(class_node),
            'line_number': class_node.lineno
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a single Python file
        
        :param file_path: Full path to the Python file
        :return: Dictionary with file's AST structure
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read())
        
        file_structure = {
            'functions': {},
            'classes': {},
            'dependencies': self._extract_dependencies(tree)
        }
        
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = self._parse_function(node)
                file_structure['functions'][func_info['name']] = func_info
            
            if isinstance(node, ast.ClassDef):
                class_info = self._parse_class(node)
                file_structure['classes'][class_info['name']] = class_info
        
        return file_structure
    
    def parse_project(self) -> Dict[str, Any]:
        """
        Parse entire Python project
        
        :return: Nested dictionary representing project structure
        """
        for root, _, files in os.walk(self.project_path):
            module_name = os.path.relpath(root, self.project_path).replace(os.path.sep, '.')
            
            for file in files:
                if self._is_python_file(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, self.project_path)
                    
                    # Initialize module structure if not exists
                    if module_name not in self.project_structure:
                        self.project_structure[module_name] = {}
                    
                    # Parse file and add to project structure
                    self.project_structure[module_name][file] = self.parse_file(file_path)
        
        return self.project_structure
    
    def save_to_json(self, output_path: str = 'project_ast.json'):
        """
        Save project AST structure to a JSON file
        
        :param output_path: Path to save the JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.project_structure, f, indent=2)

def main(project_path: str, output_path: str = 'project_ast.json'):
    """
    Main function to parse a Python project
    
    :param project_path: Path to the Python project
    :param output_path: Path to save the JSON output
    """
    parser = PythonProjectParser(project_path)
    parser.parse_project()
    parser.save_to_json(output_path)
    print(f"Project AST parsed and saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <project_path> [output_path]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'project_ast.json'
    main(project_path, output_path)