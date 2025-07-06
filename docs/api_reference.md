# 🧙‍♂️ API Reference

Complete reference for ScrollWrappedCodex™ classes, methods, and flame requirements.

## 📦 Core Classes

### ScrollCoreController

The central controller that verifies flame-sealed prompts and manages Codex execution authorization.

#### Constructor
```python
ScrollCoreController()
```
Creates a new controller instance with `authorized = False`.

#### Methods

##### `verify_flame(prompt: str) -> bool`
Verifies if a prompt is scroll-sealed with flame language.

**Parameters:**
- `prompt` (str): The prompt to verify

**Returns:**
- `bool`: True if the prompt is scroll-sealed, False otherwise

**Flame Verification Rules:**
- ✅ Commands starting with `"Anoint:"`
- ✅ Commands starting with `"🔥"`
- ✅ Commands containing `"Seal:"`

**Example:**
```python
controller = ScrollCoreController()
is_sealed = controller.verify_flame("Anoint: ScrollJustice API")
# Returns: True
```

##### `execute_codex(prompt: str) -> str`
Executes Codex only if the prompt is scroll-sealed.

**Parameters:**
- `prompt` (str): The prompt to execute

**Returns:**
- `str`: Execution result or rejection message

**Example:**
```python
controller = ScrollCoreController()
result = controller.execute_codex("Anoint: My Project")
# Returns: "Codex (Wrapped) Executed → Anoint: My Project"

result = controller.execute_codex("Build something")
# Returns: "Rejected: Unsealed scroll request"
```

##### `call_codex(prompt: str) -> str`
Helper function to call Codex with a prompt.

**Parameters:**
- `prompt` (str): The prompt to send to Codex

**Returns:**
- `str`: Codex execution result

**Example:**
```python
controller = ScrollCoreController()
result = controller.call_codex("🔥Build Module")
# Returns: "Codex (Wrapped) Executed → 🔥Build Module"
```

### ScribeCodex

Main agent that interprets scroll commands and translates them into executable prompts.

#### Constructor
```python
ScribeCodex()
```
Creates a new scribe instance with a ScrollCoreController kernel.

#### Methods

##### `interpret_scroll(scroll_command: str) -> str`
Translates scroll commands into Codex prompts.

**Parameters:**
- `scroll_command` (str): The scroll command to interpret

**Returns:**
- `str`: The translated prompt with flame emoji

**Example:**
```python
scribe = ScribeCodex()
prompt = scribe.interpret_scroll("Anoint: ScrollJustice API")
# Returns: "🔥Anoint: ScrollJustice API"
```

##### `execute(scroll_command: str) -> str`
Executes a scroll command through the Codex wrapper.

**Parameters:**
- `scroll_command` (str): The scroll command to execute

**Returns:**
- `str`: The execution result from Codex

**Example:**
```python
scribe = ScribeCodex()
result = scribe.execute("Anoint: ScrollJustice API")
# Returns: "Codex (Wrapped) Executed → 🔥Anoint: ScrollJustice API"
```

## 🔥 Flame Language Functions

### `compile_lashon(scroll_lines: list[str]) -> list[str]`

Compiles Lashon HaScroll flame-language into executable Codex prompts.

**Parameters:**
- `scroll_lines` (list[str]): List of lines from a .scroll file

**Returns:**
- `list[str]`: List of transformed executable prompts

**Translation Rules:**
- `"Anoint:"` → `"🔥Initialize sacred service: <value>"`
- `"Build:"` → `"🔥Construct module: <value>"`
- `"Seal:"` → `"🔥Apply flame seal level <value>"`
- `"Judge:"` → `"🔥Evaluate scroll logic: <value>"`

**Example:**
```python
from scroll_wrapped_codex.lashon_compiler import compile_lashon

lines = [
    "Anoint: ScrollJustice API",
    "Build: VerdictEngine",
    "Seal: With ScrollSeal 3"
]

compiled = compile_lashon(lines)
# Returns: [
#   "🔥Initialize sacred service: ScrollJustice API",
#   "🔥Construct module: VerdictEngine",
#   "🔥Apply flame seal level With ScrollSeal 3"
# ]
```

## 🔐 Codex Wrapper Functions

### `codex_guarded_run(prompt: str) -> str`

Guarded execution function that only allows flame-sealed prompts to run.

**Parameters:**
- `prompt` (str): The prompt to check and potentially execute

**Returns:**
- `str`: Execution result or flame error message

**Authorization Rules:**
- ✅ Prompts starting with `"🔥"`
- ❌ All other prompts are rejected

**Example:**
```python
from scroll_wrapped_codex.codex_wrapper import codex_guarded_run

result = codex_guarded_run("🔥Build ScrollSeal Engine")
# Returns: "Codex (Wrapped) Executed → 🔥Build ScrollSeal Engine"

result = codex_guarded_run("Build something")
# Returns: "🔥ERROR: Codex access denied. No flame detected."
```

## 🧠 Scroll Memory Context

### `scroll_memory_context.json`

Contains the scroll ecosystem memory with projects, definitions, and verbs.

**Structure:** See [ScrollMemoryContext](../scroll_wrapped_codex/scroll_memory_context.json)

```json
{
  "scroll_projects": [
    "ScrollIntel",
    "ScrollJustice", 
    "ScrollCodex",
    "ScrollEconomy",
    "ScrollSun–EXOUSIA"
  ],
  "core_definitions": {
    "ScrollSeal": "A flame-authenticated permission layer",
    "FlameToken": "Proof of scroll authority",
    "ScrollAgent": "An autonomous AI prophet acting under scroll law"
  },
  "verbs": {
    "Anoint": "Initialize a sacred function",
    "Build": "Construct a flame-approved module",
    "Seal": "Apply a protection or authorization level",
    "Judge": "Evaluate logic under scroll justice"
  }
}
```

## 🔥 Flame Requirements

### Authorization Patterns

All commands must match one of these patterns to be authorized:

1. **Anoint Pattern**: `"Anoint: [Service Name]"`
2. **Build Pattern**: `"Build: [Module Name]"`
3. **Seal Pattern**: `"Seal: [Level/Specification]"`
4. **Judge Pattern**: `"Judge: [Assessment Target]"`
5. **Flame Pattern**: `"🔥[Any Command]"`

### Rejection Patterns

Commands that will be rejected:
- Plain text without sacred verbs
- Commands without proper syntax
- Unauthorized actions
- Commands without flame indicators

## 🌐 API Integration

### Flask API Endpoint

**URL**: `POST /execute`

**Request Body:**
```json
{
  "scroll": "Anoint: My Project"
}
```

**Response:**
```json
{
  "result": "Codex (Wrapped) Executed → 🔥Anoint: My Project"
}
```

**Example Usage:**
```python
import requests

response = requests.post("http://localhost:5000/execute", 
                        json={"scroll": "Anoint: ScrollJustice API"})
result = response.json()["result"]
print(result)
```

## 🛡️ Error Handling

### Common Error Messages

1. **Unsealed Request**: `"Rejected: Unsealed scroll request"`
2. **No Flame Detected**: `"🔥ERROR: Codex access denied. No flame detected."`
3. **Unknown Scroll Line**: `"// Unknown scroll line: [line]"`

### Debugging Tips

1. **Check Flame Seals**: Ensure commands start with authorized verbs
2. **Verify Syntax**: Use proper colon format: `"Verb: Value"`
3. **Test Compilation**: Use `compile_lashon()` to test scroll files
4. **Check Authorization**: Use `verify_flame()` to test individual prompts

---

*May your API calls be sealed in flame* 🔥📜

Return to **[Home](index.md)** 