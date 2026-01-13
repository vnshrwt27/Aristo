"""
Interactive CLI for Multi-Agent RAG System
Features: Loading animations, colored output, step-by-step progress tracking
"""
import asyncio
import sys
import os
from typing import Optional
import threading
import time
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestrator import AgentOrchestrator

# ANSI color codes for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

class ThinkingAnimation:
    """Shows animated thinking indicator while processing"""
    def __init__(self, message: str = "Thinking"):
        self.message = message
        self.is_running = False
        self.thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_step = ""
    
    def _animate(self):
        idx = 0
        while self.is_running:
            frame = self.frames[idx % len(self.frames)]
            sys.stdout.write(f'\r{Colors.CYAN}{frame} {self.message}{Colors.ENDC} {Colors.DIM}{self.current_step}{Colors.ENDC}')
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
    
    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
    
    def update_step(self, step: str):
        self.current_step = f"[{step}]"
    
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear the line
        sys.stdout.flush()

def print_banner():
    """Display welcome banner"""
    banner = f"""
{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗
║            Multi-Agent RAG System                     ║
║                                                           ║
║  Ask questions and get AI-powered answers from your docs ║
╚═══════════════════════════════════════════════════════════╝{Colors.ENDC}
"""
    print(banner)

def print_step(step_name: str, status: str = "processing"):
    """Print processing step with emoji"""
    emoji_map = {
        "processing": "⚙️",
        "done": "✅",
        "error": "❌"
    }
    color_map = {
        "processing": Colors.YELLOW,
        "done": Colors.GREEN,
        "error": Colors.RED
    }
    
    emoji = emoji_map.get(status, "•")
    color = color_map.get(status, Colors.ENDC)
    
    print(f"{color}{emoji} {step_name}{Colors.ENDC}")

def print_section(title: str, content: str):
    """Print a formatted section"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}═══ {title} ═══{Colors.ENDC}")
    print(f"{Colors.DIM}{content}{Colors.ENDC}")

def format_report(report: str) -> str:
    """Add syntax highlighting to markdown report"""
    # Simple markdown formatting for terminal
    lines = report.split('\n')
    formatted = []
    
    for line in lines:
        if line.startswith('# '):
            formatted.append(f"{Colors.BOLD}{Colors.CYAN}{line}{Colors.ENDC}")
        elif line.startswith('## '):
            formatted.append(f"{Colors.BOLD}{Colors.BLUE}{line}{Colors.ENDC}")
        elif line.startswith('### '):
            formatted.append(f"{Colors.BOLD}{Colors.GREEN}{line}{Colors.ENDC}")
        elif line.startswith('- ') or line.startswith('* '):
            formatted.append(f"{Colors.YELLOW}  •{Colors.ENDC} {line[2:]}")
        elif line.startswith('```'):
            formatted.append(f"{Colors.DIM}{line}{Colors.ENDC}")
        else:
            formatted.append(line)
    
    return '\n'.join(formatted)

async def process_query(orchestrator: AgentOrchestrator, query: str):
    """Process a query with visual feedback"""
    animation = ThinkingAnimation("Processing your query")
    
    try:
        print(f"\n{Colors.BOLD}Query:{Colors.ENDC} {Colors.GREEN}{query}{Colors.ENDC}\n")
        
        # Start animation
        animation.start()
        
        # Simulate step updates (in real scenario, you'd integrate with orchestrator callbacks)
        steps = [
            ("Refining query", 1),
            ("Retrieving documents", 2),
            ("Synthesizing information", 3),
            ("Generating report", 1)
        ]
        
        # Run the orchestrator
        result_task = asyncio.create_task(orchestrator.run(query))
        
        # Simulate progress updates
        for step_name, duration in steps:
            animation.update_step(step_name)
            await asyncio.sleep(duration)
        
        # Wait for actual result
        result = await result_task
        
        # Stop animation
        animation.stop()
        
        # Print completion steps
        print_step("Query refined", "done")
        if result.refined_query and result.refined_query != query:
            print(f"  {Colors.DIM}→ {result.refined_query}{Colors.ENDC}")
        
        print_step("Documents retrieved", "done")
        print(f"  {Colors.DIM}→ Found {len(result.retrieved_chunks)} relevant chunks{Colors.ENDC}")
        
        print_step("Information synthesized", "done")
        print_step("Report generated", "done")
        
        # Display the final report
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}ANSWER{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        formatted_report = format_report(result.final_report)
        print(formatted_report)
        
        # Display metadata if available
        if result.metadata:
            print(f"\n{Colors.DIM}{'─'*60}{Colors.ENDC}")
            print(f"{Colors.DIM}Query Intent: {result.query_intent or 'N/A'}{Colors.ENDC}")
            print(f"{Colors.DIM}Complexity: {result.query_complexity or 'N/A'}{Colors.ENDC}")
            if result.metadata.get('key_concepts'):
                concepts = ', '.join(result.metadata['key_concepts'])
                print(f"{Colors.DIM}Key Concepts: {concepts}{Colors.ENDC}")
        
        print(f"{Colors.DIM}{'─'*60}{Colors.ENDC}\n")
        
        return result
        
    except Exception as e:
        animation.stop()
        print_step(f"Error: {str(e)}", "error")
        raise

async def interactive_mode():
    """Run interactive Q&A session"""
    print_banner()
    
    print(f"{Colors.YELLOW}Initializing agents...{Colors.ENDC}")
    
    try:
        orchestrator = AgentOrchestrator()
        print(f"{Colors.GREEN}✓ System ready!{Colors.ENDC}\n")
    except Exception as e:
        print(f"{Colors.RED}✗ Failed to initialize: {e}{Colors.ENDC}")
        return
    
    print(f"{Colors.DIM}Commands:{Colors.ENDC}")
    print(f"  {Colors.CYAN}• Type your question and press Enter{Colors.ENDC}")
    print(f"  {Colors.CYAN}• Type 'quit' or 'exit' to leave{Colors.ENDC}")
    print(f"  {Colors.CYAN}• Type 'clear' to clear screen{Colors.ENDC}\n")
    
    session_count = 0
    
    while True:
        try:
            # Get user input
            query = input(f"{Colors.BOLD}{Colors.BLUE}❯{Colors.ENDC} ").strip()
            
            if not query:
                continue
            
            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.GREEN}Thanks for using Multi-Agent RAG! Goodbye! 👋{Colors.ENDC}")
                break
            
            if query.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_banner()
                continue
            
            # Process the query
            session_count += 1
            start_time = time.time()
            
            await process_query(orchestrator, query)
            
            elapsed = time.time() - start_time
            print(f"{Colors.DIM}⏱  Processing time: {elapsed:.2f}s{Colors.ENDC}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrupted. Type 'quit' to exit.{Colors.ENDC}\n")
        except Exception as e:
            print(f"\n{Colors.RED}Error: {str(e)}{Colors.ENDC}\n")
            print(f"{Colors.DIM}Please try again or type 'quit' to exit.{Colors.ENDC}\n")

async def single_query_mode(query: str):
    """Process a single query and exit"""
    print_banner()
    
    print(f"{Colors.YELLOW}Initializing agents...{Colors.ENDC}")
    orchestrator = AgentOrchestrator()
    print(f"{Colors.GREEN} System ready!{Colors.ENDC}\n")
    
    await process_query(orchestrator, query)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Single query mode
        query = ' '.join(sys.argv[1:])
        asyncio.run(single_query_mode(query))
    else:
        # Interactive mode
        asyncio.run(interactive_mode())

if __name__ == "__main__":
    main()