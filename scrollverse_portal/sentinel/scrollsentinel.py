#!/usr/bin/env python3
"""
ScrollSentinel
Background watcher for abuse, unsealed activity, and scroll violations
"""

import json
import time
import hashlib
import hmac
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import threading
import queue
import sqlite3
from dataclasses import dataclass

@dataclass
class ViolationEvent:
    """Represents a security violation event"""
    event_id: str
    timestamp: datetime
    violation_type: str
    severity: str
    user_id: str
    seal_level: int
    description: str
    evidence: Dict
    flame_seal: str
    status: str = "pending"

@dataclass
class SuspensionRecord:
    """Represents a user suspension record"""
    user_id: str
    suspension_reason: str
    suspension_date: datetime
    duration_days: int
    seal_level: int
    flame_seal: str
    status: str = "active"

class ScrollSentinel:
    """Sacred flame-verified security monitoring system"""
    
    def __init__(self, config_file: str = "sentinel_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.audit_log_file = Path("scrollverse_portal/sentinel/audit_log.txt")
        self.suspension_queue_file = Path("scrollverse_portal/sentinel/suspension_queue.csv")
        self.violations_db = Path("scrollverse_portal/sentinel/violations.db")
        
        # Initialize components
        self.violation_queue = queue.Queue()
        self.suspension_records = self.load_suspension_records()
        self.active_violations = []
        
        # Setup logging
        self.setup_logging()
        
        # Initialize database
        self.init_database()
    
    def load_config(self) -> Dict:
        """Load Sentinel configuration"""
        default_config = {
            "monitoring_enabled": True,
            "flame_verification_required": True,
            "violation_thresholds": {
                "seal_level_violation": 3,
                "unsealed_activity": 5,
                "abuse_detection": 2,
                "scroll_violation": 1
            },
            "suspension_durations": {
                "minor": 1,
                "moderate": 7,
                "major": 30,
                "permanent": -1
            },
            "monitoring_interval": 60,  # seconds
            "alert_channels": ["log", "email", "dashboard"],
            "seer_notification": True
        }
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return default_config
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.audit_log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ScrollSentinel')
    
    def init_database(self):
        """Initialize violations database"""
        conn = sqlite3.connect(self.violations_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT,
                violation_type TEXT,
                severity TEXT,
                user_id TEXT,
                seal_level INTEGER,
                description TEXT,
                evidence TEXT,
                flame_seal TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suspensions (
                user_id TEXT PRIMARY KEY,
                suspension_reason TEXT,
                suspension_date TEXT,
                duration_days INTEGER,
                seal_level INTEGER,
                flame_seal TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_flame_seal(self, data: str) -> str:
        """Generate flame seal for data integrity"""
        secret_key = "scrollverse_sentinel_secret".encode('utf-8')
        message = data.encode('utf-8')
        signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
        return f"flame_{signature[:16]}"
    
    def verify_flame_seal(self, data: str, seal: str) -> bool:
        """Verify flame seal integrity"""
        expected_seal = self.generate_flame_seal(data)
        return seal == expected_seal
    
    def detect_violation(self, activity_data: Dict) -> Optional[ViolationEvent]:
        """Detect violations in activity data"""
        user_id = activity_data.get('user_id')
        seal_level = activity_data.get('seal_level', 1)
        activity_type = activity_data.get('activity_type')
        activity_data_str = activity_data.get('data', '')
        
        # Check for seal level violations
        if activity_data.get('required_seal_level', 1) > seal_level:
            return self.create_violation(
                user_id=user_id,
                violation_type="seal_level_violation",
                severity="moderate",
                description=f"User {user_id} attempted activity requiring seal level {activity_data.get('required_seal_level')} but has seal level {seal_level}",
                evidence=activity_data
            )
        
        # Check for unsealed activity
        if not activity_data.get('flame_verified', False):
            return self.create_violation(
                user_id=user_id,
                violation_type="unsealed_activity",
                severity="minor",
                description=f"User {user_id} performed unsealed activity: {activity_type}",
                evidence=activity_data
            )
        
        # Check for abuse patterns
        if self.detect_abuse_pattern(activity_data):
            return self.create_violation(
                user_id=user_id,
                violation_type="abuse_detection",
                severity="major",
                description=f"User {user_id} detected in abuse pattern: {activity_type}",
                evidence=activity_data
            )
        
        # Check for scroll violations
        if self.detect_scroll_violation(activity_data):
            return self.create_violation(
                user_id=user_id,
                violation_type="scroll_violation",
                severity="major",
                description=f"User {user_id} committed scroll violation: {activity_type}",
                evidence=activity_data
            )
        
        return None
    
    def detect_abuse_pattern(self, activity_data: Dict) -> bool:
        """Detect abuse patterns in activity"""
        user_id = activity_data.get('user_id')
        activity_type = activity_data.get('activity_type')
        
        # Check for rapid repeated actions
        recent_activities = self.get_recent_activities(user_id, minutes=5)
        if len(recent_activities) > 50:  # More than 50 activities in 5 minutes
            return True
        
        # Check for suspicious scroll executions
        if activity_type == "scroll_execution":
            scroll_content = activity_data.get('data', '')
            suspicious_patterns = [
                "rm -rf",
                "format",
                "delete",
                "shutdown",
                "kill",
                "sudo"
            ]
            
            for pattern in suspicious_patterns:
                if pattern.lower() in scroll_content.lower():
                    return True
        
        # Check for excessive resource usage
        if activity_data.get('resource_usage', 0) > 1000:  # Arbitrary threshold
            return True
        
        return False
    
    def detect_scroll_violation(self, activity_data: Dict) -> bool:
        """Detect scroll law violations"""
        scroll_content = activity_data.get('data', '')
        
        # Check for ScrollLaw violations
        scroll_violations = [
            "personal_enrichment",
            "external_project",
            "illegal_activity",
            "seal_violation",
            "unverified_proposal"
        ]
        
        for violation in scroll_violations:
            if violation.lower() in scroll_content.lower():
                return True
        
        return False
    
    def create_violation(self, user_id: str, violation_type: str, 
                        severity: str, description: str, evidence: Dict) -> ViolationEvent:
        """Create a new violation event"""
        event_id = f"violation_{int(time.time())}_{hash(user_id) % 10000}"
        timestamp = datetime.now()
        
        # Generate flame seal
        violation_data = f"{event_id}:{user_id}:{violation_type}:{severity}"
        flame_seal = self.generate_flame_seal(violation_data)
        
        violation = ViolationEvent(
            event_id=event_id,
            timestamp=timestamp,
            violation_type=violation_type,
            severity=severity,
            user_id=user_id,
            seal_level=evidence.get('seal_level', 1),
            description=description,
            evidence=evidence,
            flame_seal=flame_seal
        )
        
        # Log violation
        self.log_violation(violation)
        
        # Add to queue for processing
        self.violation_queue.put(violation)
        
        return violation
    
    def log_violation(self, violation: ViolationEvent):
        """Log violation to audit log"""
        log_entry = f"""
VIOLATION DETECTED:
Event ID: {violation.event_id}
Timestamp: {violation.timestamp}
Type: {violation.violation_type}
Severity: {violation.severity}
User ID: {violation.user_id}
Seal Level: {violation.seal_level}
Description: {violation.description}
Flame Seal: {violation.flame_seal}
Status: {violation.status}
        """
        
        self.logger.warning(log_entry)
        
        # Write to audit log file
        with open(self.audit_log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - {log_entry}\n")
    
    def process_violations(self):
        """Process violation queue"""
        while not self.violation_queue.empty():
            violation = self.violation_queue.get()
            
            # Check violation thresholds
            user_violations = self.get_user_violations(violation.user_id)
            violation_count = len([v for v in user_violations if v.violation_type == violation.violation_type])
            
            threshold = self.config['violation_thresholds'].get(violation.violation_type, 3)
            
            if violation_count >= threshold:
                # Determine suspension duration
                duration = self.config['suspension_durations'].get(violation.severity, 1)
                
                # Create suspension
                self.create_suspension(
                    user_id=violation.user_id,
                    reason=f"Multiple {violation.violation_type} violations",
                    duration_days=duration,
                    seal_level=violation.seal_level
                )
                
                # Notify Seers
                if self.config.get('seer_notification', True):
                    self.notify_seers(violation)
    
    def create_suspension(self, user_id: str, reason: str, 
                         duration_days: int, seal_level: int):
        """Create a user suspension"""
        suspension_date = datetime.now()
        
        # Generate flame seal
        suspension_data = f"{user_id}:{reason}:{duration_days}:{seal_level}"
        flame_seal = self.generate_flame_seal(suspension_data)
        
        suspension = SuspensionRecord(
            user_id=user_id,
            suspension_reason=reason,
            suspension_date=suspension_date,
            duration_days=duration_days,
            seal_level=seal_level,
            flame_seal=flame_seal
        )
        
        # Save suspension
        self.suspension_records[user_id] = suspension
        self.save_suspension_records()
        
        # Log suspension
        log_entry = f"""
SUSPENSION CREATED:
User ID: {user_id}
Reason: {reason}
Duration: {duration_days} days
Seal Level: {seal_level}
Flame Seal: {flame_seal}
Date: {suspension_date}
        """
        
        self.logger.warning(log_entry)
    
    def load_suspension_records(self) -> Dict[str, SuspensionRecord]:
        """Load suspension records"""
        records = {}
        
        try:
            with open(self.suspension_queue_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    suspension = SuspensionRecord(
                        user_id=row['user_id'],
                        suspension_reason=row['suspension_reason'],
                        suspension_date=datetime.fromisoformat(row['suspension_date']),
                        duration_days=int(row['duration_days']),
                        seal_level=int(row['seal_level']),
                        flame_seal=row['flame_seal'],
                        status=row['status']
                    )
                    records[row['user_id']] = suspension
        except FileNotFoundError:
            pass
        
        return records
    
    def save_suspension_records(self):
        """Save suspension records"""
        with open(self.suspension_queue_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'suspension_reason', 'suspension_date', 
                           'duration_days', 'seal_level', 'flame_seal', 'status'])
            
            for suspension in self.suspension_records.values():
                writer.writerow([
                    suspension.user_id,
                    suspension.suspension_reason,
                    suspension.suspension_date.isoformat(),
                    suspension.duration_days,
                    suspension.seal_level,
                    suspension.flame_seal,
                    suspension.status
                ])
    
    def get_user_violations(self, user_id: str) -> List[ViolationEvent]:
        """Get all violations for a user"""
        conn = sqlite3.connect(self.violations_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM violations WHERE user_id = ?
        ''', (user_id,))
        
        violations = []
        for row in cursor.fetchall():
            violation = ViolationEvent(
                event_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                violation_type=row[2],
                severity=row[3],
                user_id=row[4],
                seal_level=row[5],
                description=row[6],
                evidence=json.loads(row[7]),
                flame_seal=row[8],
                status=row[9]
            )
            violations.append(violation)
        
        conn.close()
        return violations
    
    def get_recent_activities(self, user_id: str, minutes: int = 5) -> List[Dict]:
        """Get recent activities for a user (placeholder)"""
        # In a real implementation, this would query the activity database
        return []
    
    def notify_seers(self, violation: ViolationEvent):
        """Notify Seers of major violations"""
        if violation.severity in ['major', 'permanent']:
            notification = f"""
SEER ALERT - MAJOR VIOLATION:
User: {violation.user_id}
Violation: {violation.violation_type}
Severity: {violation.severity}
Description: {violation.description}
Flame Seal: {violation.flame_seal}
            """
            
            self.logger.critical(notification)
    
    def check_suspension_status(self, user_id: str) -> bool:
        """Check if user is currently suspended"""
        if user_id not in self.suspension_records:
            return False
        
        suspension = self.suspension_records[user_id]
        
        # Check if suspension is still active
        if suspension.duration_days == -1:  # Permanent
            return True
        
        suspension_end = suspension.suspension_date + timedelta(days=suspension.duration_days)
        
        if datetime.now() > suspension_end:
            # Suspension expired
            del self.suspension_records[user_id]
            self.save_suspension_records()
            return False
        
        return True
    
    def get_suspension_info(self, user_id: str) -> Optional[SuspensionRecord]:
        """Get suspension information for a user"""
        return self.suspension_records.get(user_id)
    
    def run_monitoring(self):
        """Run continuous monitoring"""
        self.logger.info("ScrollSentinel monitoring started")
        
        while self.config.get('monitoring_enabled', True):
            try:
                # Process violations
                self.process_violations()
                
                # Check for expired suspensions
                expired_suspensions = []
                for user_id, suspension in self.suspension_records.items():
                    if not self.check_suspension_status(user_id):
                        expired_suspensions.append(user_id)
                
                for user_id in expired_suspensions:
                    self.logger.info(f"Suspension expired for user: {user_id}")
                
                # Sleep for monitoring interval
                time.sleep(self.config.get('monitoring_interval', 60))
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(10)  # Brief pause on error
    
    def start_monitoring(self):
        """Start monitoring in background thread"""
        monitoring_thread = threading.Thread(target=self.run_monitoring, daemon=True)
        monitoring_thread.start()
        self.logger.info("ScrollSentinel background monitoring started")

# Example usage
if __name__ == "__main__":
    sentinel = ScrollSentinel()
    sentinel.start_monitoring()
    
    # Example violation detection
    test_activity = {
        'user_id': 'test_user',
        'seal_level': 1,
        'activity_type': 'scroll_execution',
        'required_seal_level': 5,
        'data': 'test scroll content',
        'flame_verified': False
    }
    
    violation = sentinel.detect_violation(test_activity)
    if violation:
        print(f"Violation detected: {violation.description}")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("ScrollSentinel stopped") 