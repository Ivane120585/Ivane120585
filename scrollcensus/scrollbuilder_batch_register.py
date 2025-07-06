#!/usr/bin/env python3
"""
ScrollBuilder Batch Register
Batch-imports JSON builder entries and validates against ScrollSeal minimum
"""

import json
import csv
from typing import Dict, List, Optional
from pathlib import Path
import datetime

class ScrollBuilderBatchRegister:
    """Sacred batch register for importing multiple builders at once"""
    
    def __init__(self):
        self.entries_file = Path("scrollcensus/scrollcensus_form_entries.json")
        self.prophets_registry = Path("scroll_phase_11/scrollprophets_registry.json")
        self.nation_map = Path("scroll_phase_11/scrollnation_map.json")
        self.seer_queue = Path("scrollcensus/seercircle_queue.csv")
        self.ambassadors_md = Path("scroll_phase_11/scrollambassadors.md")
        
    def load_entries(self) -> List[Dict]:
        """Load builder entries from JSON file"""
        try:
            with open(self.entries_file, 'r') as f:
                data = json.load(f)
                return data.get("scrollcensus_entries", {}).get("entries", [])
        except FileNotFoundError:
            print(f"❌ Entries file not found: {self.entries_file}")
            return []
        except Exception as e:
            print(f"❌ Error loading entries: {str(e)}")
            return []
    
    def validate_builder(self, builder: Dict) -> List[str]:
        """Validate a single builder entry"""
        errors = []
        
        # Check required fields
        required_fields = [
            "full_name", "scroll_id", "flame_id", "region", "country", 
            "city", "seal_level", "flame_level", "primary_flame_sphere", 
            "preferred_role", "scroll_covenant_accepted"
        ]
        
        for field in required_fields:
            if not builder.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Check seal level requirements
        role = builder.get("preferred_role")
        seal_level = builder.get("seal_level", 0)
        
        seal_requirements = {
            "ScrollBuilder": 1,
            "ScrollAmbassador": 3,
            "ScrollSeer": 5,
            "ScrollProphet": 7,
            "ScrollJudge": 8
        }
        
        if role in seal_requirements:
            required_seal = seal_requirements[role]
            if seal_level < required_seal:
                errors.append(f"Seal level {seal_level} insufficient for {role} (requires {required_seal})")
        
        # Check flame level requirements
        flame_requirements = {
            "ScrollBuilder": 1,
            "ScrollAmbassador": 2,
            "ScrollSeer": 4,
            "ScrollProphet": 6,
            "ScrollJudge": 7
        }
        
        flame_level = builder.get("flame_level", 0)
        if role in flame_requirements:
            required_flame = flame_requirements[role]
            if flame_level < required_flame:
                errors.append(f"Flame level {flame_level} insufficient for {role} (requires {required_flame})")
        
        # Check covenant acceptance
        if not builder.get("scroll_covenant_accepted"):
            errors.append("Scroll covenant must be accepted")
        
        return errors
    
    def register_builder(self, builder: Dict) -> bool:
        """Register a single builder to all appropriate registries"""
        try:
            # Validate builder
            errors = self.validate_builder(builder)
            if errors:
                print(f"❌ Validation errors for {builder.get('full_name', 'Unknown')}:")
                for error in errors:
                    print(f"  - {error}")
                return False
            
            print(f"✅ Registering {builder['full_name']} ({builder['scroll_id']})")
            
            # Register to prophets registry if Seer/Prophet/Judge
            if builder.get("preferred_role") in ["ScrollSeer", "ScrollProphet", "ScrollJudge"]:
                self._register_to_prophets(builder)
            
            # Register to nation map
            self._register_to_nation_map(builder)
            
            # Register to ambassadors if applicable
            if builder.get("preferred_role") == "ScrollAmbassador":
                self._register_to_ambassadors(builder)
            
            # Add to SeerCircle queue if eligible
            if self._is_seer_eligible(builder):
                self._add_to_seer_queue(builder)
            
            return True
            
        except Exception as e:
            print(f"❌ Error registering {builder.get('full_name', 'Unknown')}: {str(e)}")
            return False
    
    def _register_to_prophets(self, builder: Dict):
        """Register to prophets registry"""
        try:
            # Load existing registry
            if self.prophets_registry.exists():
                with open(self.prophets_registry, 'r') as f:
                    registry = json.load(f)
            else:
                registry = {"scrollprophets": []}
            
            # Create prophet entry
            prophet_entry = {
                "name": builder["full_name"],
                "scroll_id": builder["scroll_id"],
                "flame_id": builder["flame_id"],
                "assigned_region": builder["region"],
                "country": builder["country"],
                "ordination_level": builder.get("ordination_level", "FlameBearer"),
                "scroll_council_status": "Active",
                "primary_sphere": builder["primary_flame_sphere"],
                "seal_level": builder["seal_level"],
                "flame_level": builder["flame_level"],
                "ordination_date": builder.get("ordination_date"),
                "ordained_by": builder.get("ordained_by"),
                "submission_date": builder["submission_timestamp"]
            }
            
            registry["scrollprophets"].append(prophet_entry)
            
            # Save registry
            self.prophets_registry.parent.mkdir(parents=True, exist_ok=True)
            with open(self.prophets_registry, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"👁️ Registered to prophets: {builder['scroll_id']}")
        
        except Exception as e:
            print(f"❌ Error registering to prophets: {str(e)}")
    
    def _register_to_nation_map(self, builder: Dict):
        """Register to nation map"""
        try:
            # Load existing map
            if self.nation_map.exists():
                with open(self.nation_map, 'r') as f:
                    nation_map = json.load(f)
            else:
                nation_map = {"scrollnations": []}
            
            # Find or create nation entry
            nation_entry = None
            for nation in nation_map["scrollnations"]:
                if nation["country"] == builder["country"]:
                    nation_entry = nation
                    break
            
            if not nation_entry:
                nation_entry = {
                    "country": builder["country"],
                    "region": builder["region"],
                    "builders": [],
                    "embassies": [],
                    "seers": [],
                    "flame_zones": {},
                    "created_date": datetime.datetime.now().isoformat()
                }
                nation_map["scrollnations"].append(nation_entry)
            
            # Create builder entry
            builder_entry = {
                "name": builder["full_name"],
                "scroll_id": builder["scroll_id"],
                "flame_id": builder["flame_id"],
                "city": builder["city"],
                "role": builder["preferred_role"],
                "primary_sphere": builder["primary_flame_sphere"],
                "secondary_spheres": builder.get("secondary_spheres", []),
                "seal_level": builder["seal_level"],
                "flame_level": builder["flame_level"],
                "skills": builder.get("skills", []),
                "ordination_level": builder.get("ordination_level", "FlameBearer"),
                "submission_date": builder["submission_timestamp"],
                "assigned_date": datetime.datetime.now().isoformat()
            }
            
            # Add to builders list
            nation_entry["builders"].append(builder_entry)
            
            # Add to seers if applicable
            if builder.get("preferred_role") in ["ScrollSeer", "ScrollProphet", "ScrollJudge"]:
                nation_entry["seers"].append(builder_entry)
            
            # Assign to flame zone
            self._assign_to_flame_zone(nation_entry, builder_entry)
            
            # Save map
            with open(self.nation_map, 'w') as f:
                json.dump(nation_map, f, indent=2)
            
            print(f"🗺️ Registered to nation map: {builder['country']}")
        
        except Exception as e:
            print(f"❌ Error registering to nation map: {str(e)}")
    
    def _assign_to_flame_zone(self, nation_entry: Dict, builder_entry: Dict):
        """Assign builder to flame zone"""
        primary_sphere = builder_entry["primary_sphere"]
        
        if "flame_zones" not in nation_entry:
            nation_entry["flame_zones"] = {}
        
        if primary_sphere not in nation_entry["flame_zones"]:
            nation_entry["flame_zones"][primary_sphere] = {
                "builders": [],
                "seal_level": 0,
                "flame_level": 0,
                "created_date": datetime.datetime.now().isoformat()
            }
        
        # Add builder to flame zone
        nation_entry["flame_zones"][primary_sphere]["builders"].append(builder_entry)
        
        # Update zone stats
        zone = nation_entry["flame_zones"][primary_sphere]
        zone["seal_level"] = max(zone["seal_level"], builder_entry["seal_level"])
        zone["flame_level"] = max(zone["flame_level"], builder_entry["flame_level"])
    
    def _register_to_ambassadors(self, builder: Dict):
        """Register to ambassadors markdown"""
        try:
            ambassador_entry = f"""
## {builder['full_name']} - ScrollAmbassador

- **Scroll ID**: {builder['scroll_id']}
- **Flame ID**: {builder['flame_id']}
- **Region**: {builder['region']}
- **Country**: {builder['country']}
- **City**: {builder['city']}
- **Primary Sphere**: {builder['primary_flame_sphere']}
- **Seal Level**: {builder['seal_level']}
- **Flame Level**: {builder['flame_level']}
- **Skills**: {', '.join(builder.get('skills', []))}
- **Submission Date**: {builder['submission_timestamp']}

---
"""
            
            self.ambassadors_md.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ambassadors_md, "a") as f:
                f.write(ambassador_entry)
            
            print(f"👤 Registered to ambassadors: {builder['scroll_id']}")
        
        except Exception as e:
            print(f"❌ Error registering to ambassadors: {str(e)}")
    
    def _is_seer_eligible(self, builder: Dict) -> bool:
        """Check if builder is eligible for Seer ordination"""
        seal_level = builder.get("seal_level", 0)
        flame_level = builder.get("flame_level", 0)
        primary_sphere = builder.get("primary_flame_sphere")
        preferred_role = builder.get("preferred_role")
        
        # Check basic requirements
        if seal_level < 5 or flame_level < 4:
            return False
        
        # Check sphere requirements
        required_spheres = ["Justice", "Prophecy", "Governance"]
        if primary_sphere not in required_spheres:
            return False
        
        # Check role preference
        if preferred_role not in ["ScrollSeer", "ScrollProphet"]:
            return False
        
        return True
    
    def _add_to_seer_queue(self, builder: Dict):
        """Add eligible builder to SeerCircle queue"""
        try:
            # Load existing queue
            queue_entries = []
            if self.seer_queue.exists():
                with open(self.seer_queue, 'r') as f:
                    reader = csv.DictReader(f)
                    queue_entries = list(reader)
            
            # Create new entry
            new_entry = {
                "scroll_id": builder["scroll_id"],
                "full_name": builder["full_name"],
                "flame_id": builder["flame_id"],
                "region": builder["region"],
                "country": builder["country"],
                "city": builder["city"],
                "seal_level": str(builder["seal_level"]),
                "flame_level": str(builder["flame_level"]),
                "primary_sphere": builder["primary_flame_sphere"],
                "preferred_role": builder["preferred_role"],
                "endorsed_by": builder.get("ordained_by", ""),
                "review_status": "Pending",
                "testimony_logs": f"Eligible for {builder['preferred_role']} ordination",
                "ordination_result": "Pending",
                "submission_date": builder["submission_timestamp"]
            }
            
            queue_entries.append(new_entry)
            
            # Save updated queue
            self.seer_queue.parent.mkdir(parents=True, exist_ok=True)
            with open(self.seer_queue, 'w', newline='') as f:
                fieldnames = queue_entries[0].keys() if queue_entries else []
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(queue_entries)
            
            print(f"👁️ Added to SeerCircle queue: {builder['scroll_id']}")
        
        except Exception as e:
            print(f"❌ Error adding to SeerCircle queue: {str(e)}")
    
    def batch_register(self) -> Dict:
        """Register all builders in batch"""
        print("🔥 Starting batch registration of ScrollBuilders")
        print("=" * 50)
        
        # Load entries
        entries = self.load_entries()
        if not entries:
            print("❌ No entries found to register")
            return {"success": False, "error": "No entries found"}
        
        print(f"📋 Found {len(entries)} builders to register")
        
        # Register each builder
        success_count = 0
        error_count = 0
        errors = []
        
        for i, builder in enumerate(entries, 1):
            print(f"\n[{i}/{len(entries)}] Processing {builder.get('full_name', 'Unknown')}")
            
            if self.register_builder(builder):
                success_count += 1
            else:
                error_count += 1
                errors.append(f"{builder.get('full_name', 'Unknown')}: Registration failed")
        
        # Summary
        print(f"\n📊 Batch Registration Summary:")
        print(f"  ✅ Successful: {success_count}")
        print(f"  ❌ Failed: {error_count}")
        print(f"  📋 Total: {len(entries)}")
        
        if errors:
            print(f"\n❌ Errors:")
            for error in errors:
                print(f"  - {error}")
        
        return {
            "success": error_count == 0,
            "total": len(entries),
            "successful": success_count,
            "failed": error_count,
            "errors": errors
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize batch register
    batch_register = ScrollBuilderBatchRegister()
    
    # Run batch registration
    result = batch_register.batch_register()
    
    if result["success"]:
        print(f"\n🎉 Batch registration completed successfully!")
        print(f"   Registered {result['successful']} builders")
    else:
        print(f"\n⚠️ Batch registration completed with errors")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}") 