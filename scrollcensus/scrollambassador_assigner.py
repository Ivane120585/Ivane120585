#!/usr/bin/env python3
"""
ScrollAmbassador Assigner
Auto-assigns eligible builders to sectors and updates registries
"""

import json
import csv
from typing import Dict, List, Optional
from pathlib import Path
import datetime

class ScrollAmbassadorAssigner:
    """Sacred ambassador assignment system"""
    
    def __init__(self):
        self.nation_map = Path("scroll_phase_11/scrollnation_map.json")
        self.prophets_registry = Path("scroll_phase_11/scrollprophets_registry.json")
        self.ambassadors_md = Path("scroll_phase_11/scrollambassadors.md")
        self.seer_queue = Path("scrollcensus/seercircle_queue.csv")
        
        # Define sectors and their requirements
        self.sectors = {
            "Government": {
                "min_seal": 4,
                "min_flame": 3,
                "required_spheres": ["Government", "Justice"],
                "description": "Diplomatic relations and governance"
            },
            "Technology": {
                "min_seal": 3,
                "min_flame": 2,
                "required_spheres": ["Technology"],
                "description": "Digital infrastructure and innovation"
            },
            "Justice": {
                "min_seal": 5,
                "min_flame": 4,
                "required_spheres": ["Justice", "Governance"],
                "description": "Legal systems and dispute resolution"
            },
            "Worship": {
                "min_seal": 4,
                "min_flame": 3,
                "required_spheres": ["Prophecy", "Justice"],
                "description": "Spiritual guidance and sacred practices"
            },
            "Education": {
                "min_seal": 3,
                "min_flame": 2,
                "required_spheres": ["Education", "Technology"],
                "description": "Knowledge transfer and skill development"
            },
            "Wealth": {
                "min_seal": 4,
                "min_flame": 3,
                "required_spheres": ["Wealth", "Technology"],
                "description": "Economic development and resource management"
            },
            "Media": {
                "min_seal": 3,
                "min_flame": 2,
                "required_spheres": ["Media", "Technology"],
                "description": "Communication and information dissemination"
            }
        }
    
    def load_builders(self) -> List[Dict]:
        """Load all builders from nation map"""
        try:
            if not self.nation_map.exists():
                print(f"❌ Nation map not found: {self.nation_map}")
                return []
            
            with open(self.nation_map, 'r') as f:
                data = json.load(f)
            
            builders = []
            for nation in data.get("scrollnations", []):
                for builder in nation.get("builders", []):
                    # Add nation info to builder
                    builder["nation"] = nation["country"]
                    builder["region"] = nation["region"]
                    builders.append(builder)
            
            return builders
        
        except Exception as e:
            print(f"❌ Error loading builders: {str(e)}")
            return []
    
    def is_eligible_for_sector(self, builder: Dict, sector: str) -> bool:
        """Check if builder is eligible for a specific sector"""
        sector_reqs = self.sectors.get(sector)
        if not sector_reqs:
            return False
        
        # Check seal level
        seal_level = builder.get("seal_level", 0)
        if seal_level < sector_reqs["min_seal"]:
            return False
        
        # Check flame level
        flame_level = builder.get("flame_level", 0)
        if flame_level < sector_reqs["min_flame"]:
            return False
        
        # Check required spheres
        primary_sphere = builder.get("primary_sphere")
        secondary_spheres = builder.get("secondary_spheres", [])
        all_spheres = [primary_sphere] + secondary_spheres
        
        required_spheres = sector_reqs["required_spheres"]
        if not any(sphere in all_spheres for sphere in required_spheres):
            return False
        
        return True
    
    def assign_ambassadors(self) -> Dict:
        """Assign eligible builders to ambassador sectors"""
        print("🔥 Starting ScrollAmbassador assignment")
        print("=" * 50)
        
        # Load builders
        builders = self.load_builders()
        if not builders:
            print("❌ No builders found to assign")
            return {"success": False, "error": "No builders found"}
        
        print(f"📋 Found {len(builders)} builders to evaluate")
        
        # Track assignments
        assignments = {sector: [] for sector in self.sectors.keys()}
        unassigned = []
        
        # Evaluate each builder
        for builder in builders:
            builder_name = builder.get("name", "Unknown")
            scroll_id = builder.get("scroll_id", "Unknown")
            
            print(f"\n👤 Evaluating {builder_name} ({scroll_id})")
            
            # Find eligible sectors
            eligible_sectors = []
            for sector in self.sectors.keys():
                if self.is_eligible_for_sector(builder, sector):
                    eligible_sectors.append(sector)
            
            if not eligible_sectors:
                print(f"  ❌ No eligible sectors")
                unassigned.append(builder)
                continue
            
            # Assign to best matching sector
            best_sector = self._select_best_sector(builder, eligible_sectors)
            
            if best_sector:
                assignments[best_sector].append(builder)
                print(f"  ✅ Assigned to {best_sector}")
            else:
                print(f"  ❌ Could not assign to any sector")
                unassigned.append(builder)
        
        # Update registries with assignments
        self._update_ambassador_registry(assignments)
        self._update_prophets_registry(assignments)
        self._generate_assignment_report(assignments, unassigned)
        
        # Summary
        total_assigned = sum(len(assignments[sector]) for sector in assignments)
        print(f"\n📊 Ambassador Assignment Summary:")
        print(f"  ✅ Assigned: {total_assigned}")
        print(f"  ❌ Unassigned: {len(unassigned)}")
        print(f"  📋 Total: {len(builders)}")
        
        for sector, builders_list in assignments.items():
            if builders_list:
                print(f"  📍 {sector}: {len(builders_list)} ambassadors")
        
        return {
            "success": True,
            "total": len(builders),
            "assigned": total_assigned,
            "unassigned": len(unassigned),
            "assignments": assignments
        }
    
    def _select_best_sector(self, builder: Dict, eligible_sectors: List[str]) -> Optional[str]:
        """Select the best sector for a builder based on sphere alignment"""
        primary_sphere = builder.get("primary_sphere")
        secondary_spheres = builder.get("secondary_spheres", [])
        
        # Score each sector based on sphere alignment
        sector_scores = {}
        for sector in eligible_sectors:
            score = 0
            sector_reqs = self.sectors[sector]
            
            # Primary sphere match gets highest score
            if primary_sphere in sector_reqs["required_spheres"]:
                score += 10
            
            # Secondary sphere matches
            for sphere in secondary_spheres:
                if sphere in sector_reqs["required_spheres"]:
                    score += 5
            
            # Seal level bonus
            seal_level = builder.get("seal_level", 0)
            min_seal = sector_reqs["min_seal"]
            if seal_level > min_seal:
                score += (seal_level - min_seal)
            
            # Flame level bonus
            flame_level = builder.get("flame_level", 0)
            min_flame = sector_reqs["min_flame"]
            if flame_level > min_flame:
                score += (flame_level - min_flame)
            
            sector_scores[sector] = score
        
        # Return sector with highest score
        if sector_scores:
            return max(sector_scores.keys(), key=lambda k: sector_scores[k])
        
        return None
    
    def _update_ambassador_registry(self, assignments: Dict):
        """Update ambassador registry with new assignments"""
        try:
            # Create ambassador entries
            ambassador_entries = []
            
            for sector, builders in assignments.items():
                if not builders:
                    continue
                
                sector_info = self.sectors[sector]
                
                for builder in builders:
                    entry = f"""
## {builder['name']} - {sector} Ambassador

- **Scroll ID**: {builder['scroll_id']}
- **Flame ID**: {builder['flame_id']}
- **Sector**: {sector}
- **Region**: {builder['region']}
- **Country**: {builder['nation']}
- **City**: {builder['city']}
- **Primary Sphere**: {builder['primary_sphere']}
- **Secondary Spheres**: {', '.join(builder.get('secondary_spheres', []))}
- **Seal Level**: {builder['seal_level']}
- **Flame Level**: {builder['flame_level']}
- **Skills**: {', '.join(builder.get('skills', []))}
- **Sector Description**: {sector_info['description']}
- **Assignment Date**: {datetime.datetime.now().isoformat()}

---
"""
                    ambassador_entries.append(entry)
            
            # Write to ambassador markdown
            self.ambassadors_md.parent.mkdir(parents=True, exist_ok=True)
            with open(self.ambassadors_md, 'w') as f:
                f.write("# ScrollAmbassadors Registry\n\n")
                f.write("## Sector Assignments\n\n")
                for entry in ambassador_entries:
                    f.write(entry)
            
            print(f"👤 Updated ambassador registry: {len(ambassador_entries)} assignments")
        
        except Exception as e:
            print(f"❌ Error updating ambassador registry: {str(e)}")
    
    def _update_prophets_registry(self, assignments: Dict):
        """Update prophets registry with ambassador duties"""
        try:
            if not self.prophets_registry.exists():
                print("❌ Prophets registry not found")
                return
            
            with open(self.prophets_registry, 'r') as f:
                registry = json.load(f)
            
            # Update prophets with ambassador duties
            for prophet in registry.get("scrollprophets", []):
                scroll_id = prophet.get("scroll_id")
                
                # Find if this prophet is assigned as ambassador
                for sector, builders in assignments.items():
                    for builder in builders:
                        if builder.get("scroll_id") == scroll_id:
                            prophet["ambassador_sector"] = sector
                            prophet["ambassador_duties"] = self.sectors[sector]["description"]
                            prophet["assignment_date"] = datetime.datetime.now().isoformat()
                            break
            
            # Save updated registry
            with open(self.prophets_registry, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"👁️ Updated prophets registry with ambassador duties")
        
        except Exception as e:
            print(f"❌ Error updating prophets registry: {str(e)}")
    
    def _generate_assignment_report(self, assignments: Dict, unassigned: List[Dict]):
        """Generate detailed assignment report"""
        try:
            report_path = Path("scrollcensus/ambassador_assignment_report.md")
            
            with open(report_path, 'w') as f:
                f.write("# ScrollAmbassador Assignment Report\n\n")
                f.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n")
                
                # Summary
                total_assigned = sum(len(assignments[sector]) for sector in assignments)
                f.write(f"## Summary\n\n")
                f.write(f"- **Total Builders**: {total_assigned + len(unassigned)}\n")
                f.write(f"- **Assigned**: {total_assigned}\n")
                f.write(f"- **Unassigned**: {len(unassigned)}\n\n")
                
                # Sector breakdown
                f.write("## Sector Assignments\n\n")
                for sector, builders in assignments.items():
                    if builders:
                        f.write(f"### {sector}\n")
                        f.write(f"- **Count**: {len(builders)}\n")
                        f.write(f"- **Description**: {self.sectors[sector]['description']}\n")
                        f.write(f"- **Requirements**: Seal {self.sectors[sector]['min_seal']}+, Flame {self.sectors[sector]['min_flame']}+\n")
                        f.write(f"- **Required Spheres**: {', '.join(self.sectors[sector]['required_spheres'])}\n\n")
                        
                        for builder in builders:
                            f.write(f"  - **{builder['name']}** ({builder['scroll_id']}) - {builder['primary_sphere']}\n")
                        f.write("\n")
                
                # Unassigned builders
                if unassigned:
                    f.write("## Unassigned Builders\n\n")
                    for builder in unassigned:
                        f.write(f"- **{builder['name']}** ({builder['scroll_id']}) - {builder['primary_sphere']}\n")
                        f.write(f"  - Seal: {builder.get('seal_level', 0)}, Flame: {builder.get('flame_level', 0)}\n")
                        f.write(f"  - Secondary: {', '.join(builder.get('secondary_spheres', []))}\n\n")
            
            print(f"📊 Generated assignment report: {report_path}")
        
        except Exception as e:
            print(f"❌ Error generating assignment report: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize assigner
    assigner = ScrollAmbassadorAssigner()
    
    # Run ambassador assignment
    result = assigner.assign_ambassadors()
    
    if result["success"]:
        print(f"\n🎉 Ambassador assignment completed successfully!")
        print(f"   Assigned {result['assigned']} ambassadors")
        print(f"   {result['unassigned']} builders remain unassigned")
    else:
        print(f"\n⚠️ Ambassador assignment failed")
        print(f"   Error: {result.get('error', 'Unknown error')}") 