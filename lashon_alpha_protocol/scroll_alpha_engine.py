#!/usr/bin/env python3
"""
Scroll Alpha Engine
Parser and dispatcher for Hebrew-letter scroll commands
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class ScrollAlphaEngine:
    """Sacred engine for parsing and executing Hebrew-letter scroll commands"""
    
    def __init__(self, commands_file: str = "scroll_hebrew_commands.json"):
        self.commands_file = Path(commands_file)
        self.commands = self._load_commands()
        self.scribe = None  # Will be initialized with ScribeCodex
        self.flame_level = 1  # Default flame level
        
    def _load_commands(self) -> Dict:
        """Load Hebrew command mappings from JSON file"""
        if self.commands_file.exists():
            try:
                with open(self.commands_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('lashon_alpha_protocol', {}).get('commands', {})
            except Exception as e:
                print(f"Error loading Hebrew commands: {e}")
                return {}
        return {}
    
    def set_scribe(self, scribe):
        """Set the ScribeCodex instance for execution"""
        self.scribe = scribe
    
    def set_flame_level(self, level: int):
        """Set the current flame level for command validation"""
        self.flame_level = level
    
    def parse_hebrew_command(self, line: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        Parse a Hebrew-letter scroll command
        
        Returns:
            Tuple of (hebrew_letter, scroll_verb, arguments)
        """
        if not line.strip():
            return None, None, []
        
        parts = line.strip().split()
        if not parts:
            return None, None, []
        
        hebrew_letter = parts[0]
        
        # Check if it's a Hebrew letter command
        if hebrew_letter in self.commands:
            command_info = self.commands[hebrew_letter]
            scroll_verb = command_info.get('scroll_verb', '')
            arguments = parts[1:] if len(parts) > 1 else []
            return hebrew_letter, scroll_verb, arguments
        
        return None, None, []
    
    def validate_flame_level(self, hebrew_letter: str) -> bool:
        """Validate if current flame level can execute this command"""
        if hebrew_letter not in self.commands:
            return False
        
        required_level = self.commands[hebrew_letter].get('flame_level', 1)
        return self.flame_level >= required_level
    
    def execute_hebrew_command(self, line: str) -> str:
        """Execute a Hebrew-letter scroll command"""
        hebrew_letter, scroll_verb, arguments = self.parse_hebrew_command(line)
        
        if not hebrew_letter:
            return f"🔥 ERROR: Invalid Hebrew scroll command format"
        
        if not self.validate_flame_level(hebrew_letter):
            required_level = self.commands[hebrew_letter].get('flame_level', 1)
            return f"🔥 ERROR: Flame level {required_level} required for '{hebrew_letter}'. Current level: {self.flame_level}"
        
        if not self.scribe:
            return f"🔥 ERROR: ScribeCodex not initialized"
        
        # Execute the command
        try:
            result = self._execute_command(hebrew_letter, scroll_verb, arguments)
            return f"🔥 {hebrew_letter} {scroll_verb}: {result}"
        except Exception as e:
            return f"🔥 ERROR executing {hebrew_letter} {scroll_verb}: {str(e)}"
    
    def _execute_command(self, hebrew_letter: str, scroll_verb: str, arguments: List[str]) -> str:
        """Execute the specific Hebrew command"""
        command_info = self.commands[hebrew_letter]
        engine_call = command_info.get('engine_call', '')
        
        # Map to ScribeCodex methods
        method_mapping = {
            'scribe.execute_anoint': self.scribe.anoint_scroll,
            'scribe.execute_build': self.scribe.build_module,
            'scribe.execute_gather': self.scribe.gather_resources,
            'scribe.execute_deploy': self.scribe.deploy_application,
            'scribe.execute_hear': self.scribe.hear_command,
            'scribe.execute_verify': self.scribe.verify_integrity,
            'scribe.execute_zakar': self.scribe.remember_covenant,
            'scribe.execute_consecrate': self.scribe.consecrate_session,
            'scribe.execute_test': self.scribe.test_integrity,
            'scribe.execute_yield': self.scribe.yield_result,
            'scribe.execute_keep': self.scribe.keep_in_ledger,
            'scribe.execute_learn': self.scribe.learn_patterns,
            'scribe.execute_measure': self.scribe.measure_accuracy,
            'scribe.execute_name': self.scribe.name_entity,
            'scribe.execute_seal': self.scribe.seal_with_flame,
            'scribe.execute_observe': self.scribe.observe_events,
            'scribe.execute_proclaim': self.scribe.proclaim_output,
            'scribe.execute_judge': self.scribe.judge_execution,
            'scribe.execute_quarantine': self.scribe.quarantine_paths,
            'scribe.execute_restore': self.scribe.restore_backup,
            'scribe.execute_send': self.scribe.send_to_witness,
            'scribe.execute_terminate': self.scribe.terminate_rejected
        }
        
        method = method_mapping.get(engine_call)
        if not method:
            return f"Method '{engine_call}' not found"
        
        # Execute with arguments
        args_str = ' '.join(arguments) if arguments else ''
        return method(args_str)
    
    def get_command_info(self, hebrew_letter: str) -> Optional[Dict]:
        """Get information about a Hebrew command"""
        return self.commands.get(hebrew_letter)
    
    def list_available_commands(self) -> List[str]:
        """List all available Hebrew commands for current flame level"""
        available = []
        for letter, info in self.commands.items():
            if self.validate_flame_level(letter):
                available.append(f"{letter} - {info.get('scroll_verb', '')}")
        return available
    
    def validate_scroll_file(self, scroll_content: List[str]) -> List[str]:
        """Validate a scroll file containing Hebrew commands"""
        errors = []
        for line_num, line in enumerate(scroll_content, 1):
            if line.strip() and not line.startswith('#'):
                hebrew_letter, _, _ = self.parse_hebrew_command(line)
                if hebrew_letter and not self.validate_flame_level(hebrew_letter):
                    required_level = self.commands[hebrew_letter].get('flame_level', 1)
                    errors.append(f"Line {line_num}: Flame level {required_level} required for '{hebrew_letter}'")
        return errors

class HebrewScrollParser:
    """Parser for Hebrew-letter scroll files"""
    
    def __init__(self, engine: ScrollAlphaEngine):
        self.engine = engine
    
    def parse_scroll_file(self, file_path: str) -> List[str]:
        """Parse a scroll file and return execution results"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            results = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    result = self.engine.execute_hebrew_command(line)
                    results.append(result)
            
            return results
        except Exception as e:
            return [f"🔥 ERROR parsing scroll file: {str(e)}"]
    
    def validate_scroll_file(self, file_path: str) -> List[str]:
        """Validate a scroll file for errors"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            return self.engine.validate_scroll_file(lines)
        except Exception as e:
            return [f"🔥 ERROR validating scroll file: {str(e)}"]

# Example usage and testing
if __name__ == "__main__":
    # Initialize engine
    engine = ScrollAlphaEngine()
    
    # Set flame level
    engine.set_flame_level(3)
    
    # Test Hebrew commands
    test_commands = [
        "א Anoint: ScrollJustice VerdictEngine",
        "ב Build: ScrollSealValidator",
        "ג Gather: FlameTokenPool",
        "ד Deploy: JudgmentRunner",
        "ה Hear: ScrollWitness",
        "ו Verify: UserSealLevel",
        "ז Zakar: CovenantLogs",
        "ח Consecrate: SecureSession",
        "ט Test: IntegrityFlame",
        "י Yield: Verdict Summary",
        "כ Keep: ScrollToLedger",
        "ל Learn: FlamePatterns",
        "מ Measure: JudgmentAccuracy",
        "נ Name: FlameSealID",
        "ס Seal: With ScrollSeal 4",
        "ע Observe: ScrollEvents",
        "פ Proclaim: RighteousOutput",
        "צ Judge: VerdictEngine",
        "ק Quarantine: UnsealedPaths",
        "ר Restore: RighteousBackup",
        "ש Send: Logs to WitnessCloud",
        "ת Terminate: RejectedScrolls"
    ]
    
    print("🔥 Testing Hebrew Scroll Commands:")
    print("=" * 50)
    
    for command in test_commands:
        result = engine.execute_hebrew_command(command)
        print(f"{result}")
    
    print("\n🔥 Available commands for flame level 3:")
    available = engine.list_available_commands()
    for cmd in available:
        print(f"  {cmd}") 