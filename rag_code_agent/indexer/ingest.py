from rag_code_agent.analysis.graph import DependencyGraph
from rag_code_agent.indexer.chunker import CodeChunker
from rag_code_agent.retrieval.vector_store import VectorStore
import os

class Ingestor:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.graph = DependencyGraph(root_dir)
        self.chunker = CodeChunker()
        self.vector_store = VectorStore(persistence_path=os.path.join(root_dir, "data/vector_store.pkl"))

    def run(self):
        print("Building Dependency Graph...")
        self.graph.build()
        print(f"Graph built: {self.graph.summary()}")

        print("Chunking and Indexing files...")
        all_chunks = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    # Skip the data directory to avoid self-indexing the DB
                    if "data" in file_path:
                        continue
                        
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        chunks = self.chunker.chunk_file(file_path, content)
                        all_chunks.extend(chunks)
                    except Exception as e:
                        print(f"Failed to ingest {file_path}: {e}")
        
        print(f"Adding {len(all_chunks)} chunks to Vector Store...")
        self.vector_store.add_chunks(all_chunks)
        print("Ingestion complete.")
