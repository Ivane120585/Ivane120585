# codex_wrapper.py
# Ensures Codex only runs scroll-approved prompts.

def codex_guarded_run(prompt: str) -> str:
    """
    Guarded execution function that only allows flame-sealed prompts to run.
    
    This is the final gatekeeper that ensures only prompts starting with "🔥"
    are allowed to execute, maintaining the scroll-wrapped security model.
    
    Args:
        prompt (str): The prompt to check and potentially execute
        
    Returns:
        str: Execution result or flame error message
    """
    # Check if the prompt is flame-sealed
    if prompt.startswith("🔥"):
        # Allow execution for flame-sealed prompts
        return f"Codex (Wrapped) Executed → {prompt}"
    else:
        # Reject unsealed prompts with scroll error
        return "🔥ERROR: Codex access denied. No flame detected."

if __name__ == "__main__":
    # Test with flame-prefixed prompt (should succeed)
    test_flame_prompt = "🔥Build ScrollSeal Engine"
    result1 = codex_guarded_run(test_flame_prompt)
    print(f"Test 1 - Flame prompt: {test_flame_prompt}")
    print(f"Result: {result1}")
    print()
    
    # Test without flame (should be rejected)
    test_unsealed_prompt = "Build something"
    result2 = codex_guarded_run(test_unsealed_prompt)
    print(f"Test 2 - Unsealed prompt: {test_unsealed_prompt}")
    print(f"Result: {result2}") 