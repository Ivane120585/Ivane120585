# lashon_compiler.py
# Translates .scroll flame-language commands into regular code prompts.

def compile_lashon(scroll_lines: list[str]) -> list[str]:
    """
    Compile Lashon HaScroll flame-language into executable Codex prompts.
    
    This function translates sacred scroll commands into standardized flame-style
    prompts that can be executed by the ScribeCodex agent.
    
    Args:
        scroll_lines (list[str]): List of lines from a .scroll file
        
    Returns:
        list[str]: List of transformed executable prompts
    """
    compiled_prompts = []
    
    for line in scroll_lines:
        line = line.strip()  # Remove whitespace
        
        # Skip empty lines
        if not line:
            continue
            
        # Map scroll keywords to flame-style prompts
        if line.startswith("Anoint:"):
            # Extract the value after "Anoint:"
            value = line[8:].strip()
            compiled_prompts.append(f"🔥Initialize sacred service: {value}")
            
        elif line.startswith("Build:"):
            # Extract the value after "Build:"
            value = line[7:].strip()
            compiled_prompts.append(f"🔥Construct module: {value}")
            
        elif line.startswith("Seal:"):
            # Extract the value after "Seal:"
            value = line[6:].strip()
            compiled_prompts.append(f"🔥Apply flame seal level {value}")
            
        elif line.startswith("Judge:"):
            # Extract the value after "Judge:"
            value = line[7:].strip()
            compiled_prompts.append(f"🔥Evaluate scroll logic: {value}")
            
        else:
            # Unknown scroll line - add as comment
            compiled_prompts.append(f"// Unknown scroll line: {line}")
    
    return compiled_prompts

if __name__ == "__main__":
    test_input = [
        "Anoint: ScrollJustice API",
        "Build: VerdictEngine", 
        "Seal: With ScrollSeal 3"
    ]
    for line in compile_lashon(test_input):
        print(line) 