import ast
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Chunk:
    content: str
    file_path: str
    start_line: int
    end_line: int
    type: str # 'file', 'class', 'function'
    name: str

class CodeChunker:
    def __init__(self, max_tokens: int = 1000):
        self.max_tokens = max_tokens

    def chunk_file(self, file_path: str, content: str) -> List[Chunk]:
        """Chunks a python file by logical blocks (classes, functions)."""
        chunks = []
        try:
            tree = ast.parse(content)
            
            # File level summary chunk (simplified)
            # chunks.append(Chunk(content[:200], file_path, 1, 10, 'file_summary', 'root'))

            visited_nodes = set()

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    # Check if this node is top-level or method
                    # (Simplified: we treat methods as separate chunks too contextually)
                    
                    start = node.lineno
                    end = node.end_lineno if hasattr(node, 'end_lineno') else start + 10
                    
                    # Extract source segment
                    lines = content.splitlines()
                    # Python indices are 0-based, lineno is 1-based
                    code_segment = "\n".join(lines[start-1:end])
                    
                    chunks.append(Chunk(
                        content=code_segment,
                        file_path=file_path,
                        start_line=start,
                        end_line=end,
                        type='function' if isinstance(node, ast.FunctionDef) else 'class',
                        name=node.name
                    ))
                    visited_nodes.add(node)
            
            # TODO: Handle gaps (module level code that isn't in a func/class)
            
            return chunks

        except SyntaxError:
            # Fallback for non-python or broken files: simple line chunking
            return self._fallback_chunk(file_path, content)
        except Exception as e:
            print(f"Error chunking {file_path}: {e}")
            return []

    def _fallback_chunk(self, file_path: str, content: str) -> List[Chunk]:
        return [Chunk(content, file_path, 1, len(content.splitlines()), 'raw', 'raw')]
