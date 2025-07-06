# scroll_core.py
# Handles scroll verification and routes execution to Codex.

class ScrollCoreController:
    """
    Core controller for ScrollWrappedCodex™ that verifies scroll-sealed prompts
    and manages Codex execution authorization.
    """
    
    def __init__(self):
        """Initialize the controller with no authorization."""
        self.authorized = False
    
    def verify_flame(self, prompt: str) -> bool:
        """
        Verify if a prompt is scroll-sealed with flame language.
        
        Args:
            prompt (str): The prompt to verify
            
        Returns:
            bool: True if the prompt is scroll-sealed, False otherwise
        """
        # Check for scroll-sealed indicators
        if prompt.startswith("Anoint:") or prompt.startswith("🔥") or "Seal:" in prompt:
            return True
        return False
    
    def execute_codex(self, prompt: str) -> str:
        """
        Execute Codex only if the prompt is scroll-sealed.
        
        Args:
            prompt (str): The prompt to execute
            
        Returns:
            str: Execution result or rejection message
        """
        # Verify the prompt is scroll-sealed
        if self.verify_flame(prompt):
            self.authorized = True
            return f"Codex (Wrapped) Executed → {prompt}"
        else:
            return "Rejected: Unsealed scroll request"
    
    def call_codex(self, prompt: str) -> str:
        """
        Helper function to call Codex with a prompt.
        
        Args:
            prompt (str): The prompt to send to Codex
            
        Returns:
            str: Codex execution result
        """
        return f"Codex (Wrapped) Executed → {prompt}" 