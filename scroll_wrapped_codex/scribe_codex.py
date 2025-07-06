# scribe_codex.py
# Main agent that interprets scroll commands.

from .scroll_core import ScrollCoreController

class ScribeCodex:
    """
    Main agent that interprets scroll commands and translates them into Codex prompts.
    Uses ScrollCoreController to verify and execute scroll-sealed requests.
    """
    
    def __init__(self):
        """Initialize the scribe with a ScrollCoreController kernel."""
        self.kernel = ScrollCoreController()
    
    def interpret_scroll(self, scroll_command: str) -> str:
        """
        Translate scroll commands into Codex prompts.
        
        Args:
            scroll_command (str): The scroll command to interpret
            
        Returns:
            str: The translated prompt with flame emoji
        """
        # Simulate turning scroll commands into Codex prompts
        return "🔥" + scroll_command
    
    def execute(self, scroll_command: str) -> str:
        """
        Execute a scroll command through the Codex wrapper.
        
        Args:
            scroll_command (str): The scroll command to execute
            
        Returns:
            str: The execution result from Codex
        """
        # Interpret the scroll command into a prompt
        prompt = self.interpret_scroll(scroll_command)
        
        # Pass the prompt to the kernel for execution
        return self.kernel.execute_codex(prompt)

if __name__ == "__main__":
    scribe = ScribeCodex()
    result = scribe.execute("Anoint: Build ScrollJustice Gateway")
    print(result) 