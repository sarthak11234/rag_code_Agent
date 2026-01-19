import argparse
import sys
import os

# Ensure we can import modules from the parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_code_agent.indexer.ingest import Ingestor
from rag_code_agent.agent.core import CodeAgent
from rich.console import Console
from rich.markdown import Markdown

console = Console()

def main():
    parser = argparse.ArgumentParser(description="RAG Code Agent")
    parser.add_argument("--target", type=str, default=".", help="Target codebase directory")
    parser.add_argument("action", choices=["ingest", "query"], help="Action to perform")
    parser.add_argument("--q", type=str, help="Query string (required for 'query' action)")
    
    args = parser.parse_args()
    
    target_dir = os.path.abspath(args.target)
    
    if args.action == "ingest":
        console.print(f"[bold green]Starting Ingestion for: {target_dir}[/bold green]")
        ingestor = Ingestor(target_dir)
        ingestor.run()
        
    elif args.action == "query":
        if not args.q:
            console.print("[bold red]Error: --q is required for query action[/bold red]")
            return
            
        console.print(f"[bold blue]Querying Agent on: {target_dir}[/bold blue]")
        agent = CodeAgent(target_dir)
        result = agent.query(args.q)
        
        console.print("\n[bold]Retrieved Context (Top 2):[/bold]")
        for chunk in result['retrieved_chunks'][:2]:
            console.print(f"[dim]{chunk['metadata']['file_path']}:{chunk['metadata']['name']}[/dim]")
            console.print(Markdown(f"```python\n{chunk['content']}\n```"))
            
        console.print("\n[bold]Generated Prompt (Preview):[/bold]")
        console.print(result['prompt'][:500] + "...")

if __name__ == "__main__":
    main()
