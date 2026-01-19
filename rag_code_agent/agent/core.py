import os
from rag_code_agent.retrieval.vector_store import VectorStore
from rag_code_agent.analysis.graph import DependencyGraph

class CodeAgent:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.vector_store = VectorStore(persistence_path=os.path.join(root_dir, "data/vector_store.pkl"))
        self.graph = DependencyGraph(root_dir)
        # Note: Graph needs to be built/loaded. 
        # For this PoC, we rebuild or assume it's cheap to build. 
        # Ideally, we serialize/deserialize the graph.
        print("Loading Dependency Graph...")
        self.graph.build()

    def query(self, user_query: str):
        print(f"Agent received query: {user_query}")
        
        # 1. Retrieve relevant code chunks
        results = self.vector_store.query(user_query, n_results=5)
        
        # 2. Extract specific entities (naive intent understanding)
        # If the user asks about a specific file/class, we could look it up in the Graph
        # For now, we trust the vector search.
        
        # 3. Assemble Context
        context_str = "Context from Codebase:\n\n"
        for res in results:
            meta = res['metadata']
            context_str += f"--- File: {meta['file_path']} | {meta['type']}: {meta['name']} ---\n"
            context_str += f"{res['content']}\n\n"

        # 4. Construct Prompt
        prompt = f"""You are an expert software engineer analyzing a codebase.
Answer the user's question based ONLY on the provided context.

Query: {user_query}

{context_str}

Answer:"""

        # 5. Call LLM (Placeholder)
        # In a real scenario: response = openai.chat.completions.create(...)
        print("\n--- Constructed Prompt ---")
        print(prompt[:500] + "...(truncated)...")
        print("--------------------------\n")
        
        return {
            "prompt": prompt,
            "retrieved_chunks": results
        }
