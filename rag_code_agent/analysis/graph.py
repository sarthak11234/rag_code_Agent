import ast
import os
import networkx as nx
from pathlib import Path
from typing import Dict, List, Set, Optional

class CodeNode:
    def __init__(self, name: str, type: str, file_path: str, line_no: int):
        self.name = name
        self.type = type # 'file', 'class', 'function'
        self.file_path = file_path
        self.line_no = line_no
        self.id = f"{file_path}:{name}" if type != 'file' else file_path

    def __repr__(self):
        return f"<CodeNode {self.name} ({self.type})>"

class DependencyGraph:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        self.graph = nx.DiGraph()
        self.nodes_map: Dict[str, CodeNode] = {}

    def build(self):
        """Scans the directory and builds the graph."""
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._process_file(file_path)

    def _process_file(self, file_path: Path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = str(file_path.relative_to(self.root_dir))
            file_node = CodeNode(rel_path, 'file', str(file_path), 0)
            self._add_node(file_node)

            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._process_class(node, file_node)
                elif isinstance(node, ast.FunctionDef):
                    if not isinstance(getattr(node, 'parent', None), ast.ClassDef): # Top level only for now
                         self._process_function(node, file_node)
                
                # Basic Import Handling (Edges)
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # For now just linking file to import names (simplified)
                    pass

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def _process_class(self, node: ast.ClassDef, file_node: CodeNode):
        class_node = CodeNode(node.name, 'class', file_node.file_path, node.lineno)
        self._add_node(class_node)
        self.graph.add_edge(file_node.id, class_node.id, type='defines')
        
        # Traverse methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                 self._process_function(item, class_node)

    def _process_function(self, node: ast.FunctionDef, parent_node: CodeNode):
        func_node = CodeNode(node.name, 'function', parent_node.file_path, node.lineno)
        self._add_node(func_node)
        self.graph.add_edge(parent_node.id, func_node.id, type='defines')

    def _add_node(self, node: CodeNode):
        self.nodes_map[node.id] = node
        self.graph.add_node(node.id, data=node)

    def get_definitions(self, file_path: str) -> List[CodeNode]:
        """Returns all definitions in a file."""
        # This is a naive implementation, real one would traverse graph edges
        abs_path = str(Path(file_path).resolve())
        definitions = []
        if abs_path in self.nodes_map:
             # Find children
             for neighbor in self.graph.neighbors(abs_path):
                 definitions.append(self.nodes_map[neighbor])
        return definitions

    def summary(self):
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "files": len([n for n in self.nodes_map.values() if n.type == 'file'])
        }
