# RAG Code Agent

A specialized LLM agent designed for codebase analysis that combines **Static Analysis** with **Retrieval-Augmented Generation (RAG)**.

## 🧠 Concept

Traditional RAG builds embeddings on raw text chunks, often losing the structural context of code (like class hierarchies or function boundaries). This agent improves upon that by:

1.  **Logical Chunking**: Instead of arbitrary text windows, code is split by logical definitions (Classes and Functions) using Python's `ast` module.
2.  **Static Analysis (Graph)**: It builds a dependency graph (`rag_code_agent/analysis/graph.py`) to understand relationships between files and symbols, ensuring derived context isn't just similar words, but structurally relevant code.
3.  **Local Hybrid Retrieval**: Uses `sentence-transformers` for semantic search, powered by a lightweight Numpy-based vector store (`vector_store.pkl`). No heavyweight database (like Chroma/Pinecone) is strictly required for this scale.

## 🚀 Installation

The agent is designed to be lightweight and local-first.

```bash
# Install dependencies
pip install -r requirements.txt
```

## 🛠️ Usage

The CLI (`main.py`) provides two primary modes: `ingest` and `query`.

### 1. Ingest a Codebase
This parses the target directory, builds the dependency graph, chunks the code, and saves the vector index locally.

```bash
python main.py --target ./ ingest
```

**Output:**
```
Starting Ingestion for: C:\Path\To\Repo
Building Dependency Graph...
Graph built: {'nodes': 45, 'edges': 60, 'files': 12}
Chunking and Indexing files...
Adding 35 chunks to Vector Store...
Generating embeddings...
Ingestion complete.
```

### 2. Query the Agent
Ask questions about the logic, architecture, or specific implementations.

```bash
python main.py --target ./ query --q "Explain the VectorStore implementation"
```

**Output:**
```
Querying Agent on: C:\Path\To\Repo
Loading Dependency Graph...

Agent received query: Explain the VectorStore implementation

Retrieved Context (Top 2):
--- File: rag_code_agent/retrieval/vector_store.py | class: VectorStore ---
class VectorStore:
    def __init__(self, persistence_path: ...):
        self.documents = []
        self.embeddings = None
        # ... (source code) ...

--- Generated Prompt (Ready for LLM) ---
You are an expert software engineer analyzing a codebase.
Answer the user's question based ONLY on the provided context.

Query: Explain the VectorStore implementation
...
```

## 📂 Architecture

- **`analysis/`**: Contains the `DependencyGraph` builder using `ast`.
- **`indexer/`**: `CodeChunker` logic to split files by AST nodes.
- **`retrieval/`**: `VectorStore` implementation using Numpy & Pickle.
- **`agent/`**: `CodeAgent` orchestrator combining graph + vector search.
