#!/usr/bin/env python3
"""
Scroll Nation Map Updater
Assigns builders to nations, ScrollCities, and FlameZones
"""

import json
import csv
from typing import Dict, List, Optional
from pathlib import Path
import datetime

class ScrollNationMapUpdater:
    """Sacred updater for assigning builders to geographic and flame zones"""
    
    def __init__(self):
        self.nation_map_file = Path("scroll_phase_11/scrollnation_map.json")
        self.embassy_blueprints_dir = Path("scroll_phase_11/scroll_embassy_blueprints")
        self.seer_queue_file = Path("scrollcensus/seercircle_queue.csv")
        
    def load_nation_map(self) -> Dict:
        """Load current nation map"""
        if self.nation_map_file.exists():
            with open(self.nation_map_file, 'r') as f:
                return json.load(f)
        else:
            return {"scrollnations": []}
    
    def save_nation_map(self, nation_map: Dict):
        """Save updated nation map"""
        self.nation_map_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.nation_map_file, 'w') as f:
            json.dump(nation_map, f, indent=2)
    
    def assign_builder_to_nation(self, builder_data: Dict) -> bool:
        """
        Assign a builder to their appropriate nation
        
        Args:
            builder_data: Builder census data
            
        Returns:
            True if assignment successful
        """
        try:
            nation_map = self.load_nation_map()
            
            # Find or create nation entry
            nation_entry = None
            for nation in nation_map["scrollnations"]:
                if nation["country"] == builder_data["country"]:
                    nation_entry = nation
                    break
            
            if not nation_entry:
                nation_entry = {
                    "country": builder_data["country"],
                    "region": builder_data["region"],
                    "builders": [],
                    "embassies": [],
                    "seers": [],
                    "flame_zones": {},
                    "created_date": datetime.datetime.now().isoformat()
                }
                nation_map["scrollnations"].append(nation_entry)
            
            # Create builder entry
            builder_entry = {
                "name": builder_data["full_name"],
                "scroll_id": builder_data["scroll_id"],
                "flame_id": builder_data["flame_id"],
                "city": builder_data["city"],
                "role": builder_data["preferred_role"],
                "primary_sphere": builder_data["primary_flame_sphere"],
                "secondary_spheres": builder_data.get("secondary_spheres", []),
                "seal_level": builder_data["seal_level"],
                "flame_level": builder_data["flame_level"],
                "skills": builder_data.get("skills", []),
                "ordination_level": builder_data.get("ordination_level", "FlameBearer"),
                "submission_date": builder_data["submission_timestamp"],
                "assigned_date": datetime.datetime.now().isoformat()
            }
            
            # Add to builders list
            nation_entry["builders"].append(builder_entry)
            
            # Add to seers if applicable
            if builder_data.get("preferred_role") in ["ScrollSeer", "ScrollProphet", "ScrollJudge"]:
                nation_entry["seers"].append(builder_entry)
            
            # Assign to flame zone
            self._assign_to_flame_zone(nation_entry, builder_entry)
            
            # Check for embassy assignment
            self._check_embassy_assignment(nation_entry, builder_entry)
            
            # Save updated map
            self.save_nation_map(nation_map)
            
            print(f"✅ Assigned {builder_data['full_name']} to {builder_data['country']}")
            return True
            
        except Exception as e:
            print(f"❌ Error assigning builder: {str(e)}")
            return False
    
    def _assign_to_flame_zone(self, nation_entry: Dict, builder_entry: Dict):
        """Assign builder to appropriate flame zone"""
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
    
    def _check_embassy_assignment(self, nation_entry: Dict, builder_entry: Dict):
        """Check if builder should be assigned to embassy"""
        city = builder_entry["city"]
        
        # Check if embassy exists in city
        for embassy in nation_entry.get("embassies", []):
            if embassy["city"] == city:
                if "assigned_builders" not in embassy:
                    embassy["assigned_builders"] = []
                embassy["assigned_builders"].append(builder_entry["scroll_id"])
                print(f"🏛️ Assigned {builder_entry['name']} to embassy in {city}")
                break
    
    def update_embassy_blueprints(self, city_name: str, country: str):
        """Update embassy blueprints for a new city"""
        try:
            # Load city template
            city_template_file = self.embassy_blueprints_dir / "scrollcity_template.geojson"
            
            if city_template_file.exists():
                with open(city_template_file, 'r') as f:
                    city_template = json.load(f)
                
                # Create new city entry
                new_city = {
                    "type": "Feature",
                    "properties": {
                        "name": city_name,
                        "country": country,
                        "embassy_status": "Planned",
                        "builders_count": 0,
                        "flame_zones": [],
                        "created_date": datetime.datetime.now().isoformat()
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]  # Placeholder coordinates
                    }
                }
                
                city_template["features"].append(new_city)
                
                # Save updated template
                with open(city_template_file, 'w') as f:
                    json.dump(city_template, f, indent=2)
                
                print(f"🏛️ Updated embassy blueprints for {city_name}, {country}")
            
        except Exception as e:
            print(f"❌ Error updating embassy blueprints: {str(e)}")
    
    def update_ambassadors_md(self, builder_data: Dict):
        """Update ambassadors markdown file"""
        try:
            ambassadors_file = Path("scroll_phase_11/scrollambassadors.md")
            ambassadors_file.parent.mkdir(parents=True, exist_ok=True)
            
            if builder_data.get("preferred_role") == "ScrollAmbassador":
                ambassador_entry = f"""
## {builder_data['full_name']} - ScrollAmbassador

- **Scroll ID**: {builder_data['scroll_id']}
- **Flame ID**: {builder_data['flame_id']}
- **Region**: {builder_data['region']}
- **Country**: {builder_data['country']}
- **City**: {builder_data['city']}
- **Primary Sphere**: {builder_data['primary_flame_sphere']}
- **Seal Level**: {builder_data['seal_level']}
- **Flame Level**: {builder_data['flame_level']}
- **Skills**: {', '.join(builder_data.get('skills', []))}
- **Submission Date**: {builder_data['submission_timestamp']}

---
"""
                
                with open(ambassadors_file, "a") as f:
                    f.write(ambassador_entry)
                
                print(f"👤 Updated ambassadors registry: {builder_data['scroll_id']}")
        
        except Exception as e:
            print(f"❌ Error updating ambassadors: {str(e)}")
    
    def check_seer_eligibility(self, builder_data: Dict) -> bool:
        """Check if builder is eligible for Seer ordination"""
        seal_level = builder_data.get("seal_level", 0)
        flame_level = builder_data.get("flame_level", 0)
        primary_sphere = builder_data.get("primary_flame_sphere")
        preferred_role = builder_data.get("preferred_role")
        
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
    
    def add_to_seer_queue(self, builder_data: Dict):
        """Add eligible builder to SeerCircle queue"""
        try:
            if not self.check_seer_eligibility(builder_data):
                return
            
            # Load existing queue
            queue_entries = []
            if self.seer_queue_file.exists():
                with open(self.seer_queue_file, 'r') as f:
                    reader = csv.DictReader(f)
                    queue_entries = list(reader)
            
            # Create new entry
            new_entry = {
                "scroll_id": builder_data["scroll_id"],
                "full_name": builder_data["full_name"],
                "flame_id": builder_data["flame_id"],
                "region": builder_data["region"],
                "country": builder_data["country"],
                "city": builder_data["city"],
                "seal_level": str(builder_data["seal_level"]),
                "flame_level": str(builder_data["flame_level"]),
                "primary_sphere": builder_data["primary_flame_sphere"],
                "preferred_role": builder_data["preferred_role"],
                "endorsed_by": builder_data.get("ordained_by", ""),
                "review_status": "Pending",
                "testimony_logs": f"Eligible for {builder_data['preferred_role']} ordination",
                "ordination_result": "Pending",
                "submission_date": builder_data["submission_timestamp"]
            }
            
            queue_entries.append(new_entry)
            
            # Save updated queue
            self.seer_queue_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.seer_queue_file, 'w', newline='') as f:
                fieldnames = queue_entries[0].keys() if queue_entries else []
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(queue_entries)
            
            print(f"👁️ Added {builder_data['full_name']} to SeerCircle queue")
        
        except Exception as e:
            print(f"❌ Error adding to SeerCircle queue: {str(e)}")
    
    def process_census_data(self, builder_data: Dict):
        """Process complete census data for a builder"""
        print(f"🔥 Processing census data for {builder_data['full_name']}")
        
        # Assign to nation
        if self.assign_builder_to_nation(builder_data):
            # Update embassy blueprints
            self.update_embassy_blueprints(builder_data["city"], builder_data["country"])
            
            # Update ambassadors
            self.update_ambassadors_md(builder_data)
            
            # Check Seer eligibility
            if self.check_seer_eligibility(builder_data):
                self.add_to_seer_queue(builder_data)
            
            print(f"✅ Completed processing for {builder_data['scroll_id']}")
        else:
            print(f"❌ Failed to process census data for {builder_data['scroll_id']}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize updater
    updater = ScrollNationMapUpdater()
    
    # Test builder data
    test_builder = {
        "full_name": "Test Builder",
        "scroll_id": "SCROLLTEST123",
        "flame_id": "FLAMETEST456",
        "region": "West Africa",
        "country": "Ghana",
        "city": "Accra",
        "preferred_role": "ScrollSeer",
        "primary_flame_sphere": "Justice",
        "seal_level": 6,
        "flame_level": 5,
        "skills": ["Python", "Flask", "Justice"],
        "ordination_level": "FlameBearer",
        "submission_timestamp": datetime.datetime.now().isoformat()
    }
    
    print("🔥 Testing Scroll Nation Map Updater:")
    print("=" * 50)
    
    # Process test builder
    updater.process_census_data(test_builder)
    
    # Show nation map stats
    nation_map = updater.load_nation_map()
    print(f"\n📊 Nation Map Statistics:")
    print(f"  Total Nations: {len(nation_map['scrollnations'])}")
    
    for nation in nation_map["scrollnations"]:
        print(f"  {nation['country']}: {len(nation['builders'])} builders, {len(nation['seers'])} seers") 