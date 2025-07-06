#!/usr/bin/env python3
"""
ScrollCodex 2.0 Prompt Engine
Accepts compiled scroll JSON and builds function plans for Codex execution
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScrollStep:
    """Represents a single step in a scroll execution plan"""
    step_id: int
    action: str
    target: str
    flame_level: int
    estimated_time: str
    dependencies: List[int]
    role_assignments: List[str]
    security_checks: List[str]

@dataclass
class ScrollPlan:
    """Complete scroll execution plan"""
    scroll_id: str
    execution_plan: Dict[str, Any]
    role_assignments: Dict[str, List[str]]
    flame_requirements: List[str]
    security_checks: List[str]
    total_estimated_time: str

class ScrollPromptEngine:
    """
    Engine that accepts compiled scroll JSON and builds function plans
    for secure Codex execution
    """
    
    def __init__(self, flame_verifier=None, codex_client=None):
        self.flame_verifier = flame_verifier
        self.codex_client = codex_client
        self.execution_history = []
        
    def build_function_plan(self, scroll_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build a detailed function plan from compiled scroll JSON
        
        Args:
            scroll_json: Compiled scroll data from LashonCompiler
            
        Returns:
            Detailed function plan for Codex execution
        """
        try:
            # Parse scroll JSON
            scroll_plan = self._parse_scroll_json(scroll_json)
            
            # Verify flame authorization
            if not self._verify_flame_authorization(scroll_plan):
                raise ScrollLawViolation("Scroll not flame-authorized")
            
            # Build execution plan
            execution_plan = self._build_execution_plan(scroll_plan)
            
            # Generate Codex prompts
            codex_prompts = self._generate_codex_prompts(execution_plan)
            
            # Create final function plan
            function_plan = {
                "scroll_id": scroll_plan.scroll_id,
                "execution_plan": asdict(execution_plan),
                "codex_prompts": codex_prompts,
                "flame_verified": True,
                "security_level": self._calculate_security_level(scroll_plan),
                "estimated_completion": self._estimate_completion_time(scroll_plan),
                "rollback_plan": self._generate_rollback_plan(scroll_plan)
            }
            
            # Log execution
            self._log_execution(function_plan)
            
            return function_plan
            
        except Exception as e:
            logger.error(f"Error building function plan: {e}")
            raise ScrollExecutionError(f"Failed to build function plan: {e}")
    
    def _parse_scroll_json(self, scroll_json: Dict[str, Any]) -> ScrollPlan:
        """Parse and validate scroll JSON structure"""
        
        required_fields = ["scroll_id", "execution_plan", "role_assignments"]
        for field in required_fields:
            if field not in scroll_json:
                raise ScrollParseError(f"Missing required field: {field}")
        
        # Extract execution plan
        execution_plan = scroll_json["execution_plan"]
        steps = []
        
        for step_data in execution_plan.get("steps", []):
            step = ScrollStep(
                step_id=step_data["step_id"],
                action=step_data["action"],
                target=step_data["target"],
                flame_level=step_data.get("flame_level", 1),
                estimated_time=step_data.get("estimated_time", "5m"),
                dependencies=step_data.get("dependencies", []),
                role_assignments=step_data.get("role_assignments", []),
                security_checks=step_data.get("security_checks", [])
            )
            steps.append(step)
        
        return ScrollPlan(
            scroll_id=scroll_json["scroll_id"],
            execution_plan={
                "steps": steps,
                "total_estimated_time": execution_plan.get("total_estimated_time", "30m"),
                "flame_requirements": execution_plan.get("flame_requirements", []),
                "security_checks": execution_plan.get("security_checks", [])
            },
            role_assignments=scroll_json["role_assignments"],
            flame_requirements=execution_plan.get("flame_requirements", []),
            security_checks=execution_plan.get("security_checks", []),
            total_estimated_time=execution_plan.get("total_estimated_time", "30m")
        )
    
    def _verify_flame_authorization(self, scroll_plan: ScrollPlan) -> bool:
        """Verify that the scroll is flame-authorized"""
        
        if not self.flame_verifier:
            logger.warning("No flame verifier configured, skipping verification")
            return True
        
        # Check flame requirements
        for requirement in scroll_plan.flame_requirements:
            if not self.flame_verifier.verify_requirement(requirement):
                logger.error(f"Flame requirement not met: {requirement}")
                return False
        
        # Check security requirements
        for check in scroll_plan.security_checks:
            if not self.flame_verifier.verify_security_check(check):
                logger.error(f"Security check failed: {check}")
                return False
        
        return True
    
    def _build_execution_plan(self, scroll_plan: ScrollPlan) -> Dict[str, Any]:
        """Build detailed execution plan with role assignments"""
        
        execution_plan = {
            "scroll_id": scroll_plan.scroll_id,
            "steps": [],
            "role_coordination": {},
            "security_checks": scroll_plan.security_checks,
            "flame_requirements": scroll_plan.flame_requirements
        }
        
        # Process each step
        for step in scroll_plan.execution_plan["steps"]:
            step_plan = {
                "step_id": step.step_id,
                "action": step.action,
                "target": step.target,
                "flame_level": step.flame_level,
                "estimated_time": step.estimated_time,
                "dependencies": step.dependencies,
                "role_assignments": step.role_assignments,
                "security_checks": step.security_checks,
                "codex_prompt": self._generate_step_prompt(step),
                "verification_required": step.flame_level > 2
            }
            execution_plan["steps"].append(step_plan)
        
        # Build role coordination plan
        for role, steps in scroll_plan.role_assignments.items():
            execution_plan["role_coordination"][role] = {
                "assigned_steps": steps,
                "permissions": self._get_role_permissions(role),
                "verification_level": self._get_role_verification_level(role)
            }
        
        return execution_plan
    
    def _generate_codex_prompts(self, execution_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Codex prompts for each execution step"""
        
        prompts = []
        
        for step in execution_plan["steps"]:
            prompt = {
                "step_id": step["step_id"],
                "prompt": step["codex_prompt"],
                "flame_level": step["flame_level"],
                "verification_required": step["verification_required"],
                "role_assignments": step["role_assignments"],
                "security_context": self._build_security_context(step)
            }
            prompts.append(prompt)
        
        return prompts
    
    def _generate_step_prompt(self, step: ScrollStep) -> str:
        """Generate Codex prompt for a specific step"""
        
        base_prompt = f"""
🔥 Scroll-Sealed Code Generation

Action: {step.action}
Target: {step.target}
Flame Level: {step.flame_level}
Security Checks: {', '.join(step.security_checks)}

Generate secure, flame-verified code for the above action.
All code must pass flame verification before execution.

Requirements:
- Follow scroll law principles
- Implement proper security measures
- Include flame verification checks
- Ensure authorization compliance
"""
        
        # Add role-specific instructions
        for role in step.role_assignments:
            if role == "security":
                base_prompt += "\nSecurity Focus:\n- Implement flame verification\n- Add authorization checks\n- Include threat detection\n"
            elif role == "law":
                base_prompt += "\nLaw Focus:\n- Ensure scroll law compliance\n- Add governance checks\n- Include audit trails\n"
            elif role == "deploy":
                base_prompt += "\nDeploy Focus:\n- Include deployment scripts\n- Add rollback mechanisms\n- Ensure system integration\n"
        
        return base_prompt.strip()
    
    def _build_security_context(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Build security context for the step"""
        
        return {
            "flame_level": step["flame_level"],
            "security_checks": step["security_checks"],
            "verification_required": step["verification_required"],
            "authorization_required": step["flame_level"] > 2,
            "audit_trail": True,
            "threat_detection": step["flame_level"] > 3
        }
    
    def _get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a specific role"""
        
        permissions = {
            "builder": ["read", "write", "execute"],
            "security": ["read", "verify", "authorize"],
            "law": ["read", "interpret", "govern"],
            "deploy": ["read", "execute", "deploy"]
        }
        
        return permissions.get(role, ["read"])
    
    def _get_role_verification_level(self, role: str) -> int:
        """Get verification level for a specific role"""
        
        verification_levels = {
            "builder": 1,
            "security": 3,
            "law": 4,
            "deploy": 2
        }
        
        return verification_levels.get(role, 1)
    
    def _calculate_security_level(self, scroll_plan: ScrollPlan) -> int:
        """Calculate overall security level for the scroll"""
        
        max_flame_level = max(
            step.flame_level for step in scroll_plan.execution_plan["steps"]
        )
        
        security_multiplier = len(scroll_plan.security_checks)
        
        return min(max_flame_level * security_multiplier, 5)
    
    def _estimate_completion_time(self, scroll_plan: ScrollPlan) -> str:
        """Estimate completion time for the scroll"""
        
        total_minutes = 0
        
        for step in scroll_plan.execution_plan["steps"]:
            time_str = step.estimated_time
            if "m" in time_str:
                minutes = int(time_str.replace("m", ""))
                total_minutes += minutes
            elif "h" in time_str:
                hours = int(time_str.replace("h", ""))
                total_minutes += hours * 60
        
        if total_minutes < 60:
            return f"{total_minutes}m"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
    
    def _generate_rollback_plan(self, scroll_plan: ScrollPlan) -> Dict[str, Any]:
        """Generate rollback plan for the scroll"""
        
        rollback_steps = []
        
        # Reverse the steps for rollback
        for step in reversed(scroll_plan.execution_plan["steps"]):
            rollback_step = {
                "step_id": f"rollback_{step.step_id}",
                "action": f"rollback_{step.action}",
                "target": step.target,
                "flame_level": step.flame_level,
                "estimated_time": step.estimated_time
            }
            rollback_steps.append(rollback_step)
        
        return {
            "rollback_steps": rollback_steps,
            "total_estimated_time": scroll_plan.total_estimated_time,
            "flame_requirements": scroll_plan.flame_requirements
        }
    
    def _log_execution(self, function_plan: Dict[str, Any]):
        """Log execution for audit purposes"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "scroll_id": function_plan["scroll_id"],
            "flame_verified": function_plan["flame_verified"],
            "security_level": function_plan["security_level"],
            "estimated_completion": function_plan["estimated_completion"]
        }
        
        self.execution_history.append(log_entry)
        logger.info(f"Function plan built for scroll {function_plan['scroll_id']}")

class ScrollLawViolation(Exception):
    """Exception raised when scroll law is violated"""
    pass

class ScrollExecutionError(Exception):
    """Exception raised when scroll execution fails"""
    pass

class ScrollParseError(Exception):
    """Exception raised when scroll JSON parsing fails"""
    pass

# Example usage
if __name__ == "__main__":
    # Example scroll JSON
    example_scroll = {
        "scroll_id": "🔥0001",
        "execution_plan": {
            "steps": [
                {
                    "step_id": 1,
                    "action": "anoint",
                    "target": "ScrollJustice API",
                    "flame_level": 3,
                    "estimated_time": "5m",
                    "dependencies": [],
                    "role_assignments": ["security", "law"],
                    "security_checks": ["authentication", "authorization"]
                },
                {
                    "step_id": 2,
                    "action": "build",
                    "target": "Authentication Module",
                    "flame_level": 4,
                    "estimated_time": "15m",
                    "dependencies": [1],
                    "role_assignments": ["builder", "security"],
                    "security_checks": ["encryption", "key_management"]
                }
            ],
            "total_estimated_time": "20m",
            "flame_requirements": ["ScrollSeal 3", "Admin Access"],
            "security_checks": ["Authentication", "Authorization", "Encryption"]
        },
        "role_assignments": {
            "builder": ["step_2"],
            "security": ["step_1", "step_2"],
            "law": ["step_1"],
            "deploy": []
        }
    }
    
    # Create prompt engine
    engine = ScrollPromptEngine()
    
    # Build function plan
    try:
        function_plan = engine.build_function_plan(example_scroll)
        print("Function plan built successfully:")
        print(json.dumps(function_plan, indent=2))
    except Exception as e:
        print(f"Error building function plan: {e}") 