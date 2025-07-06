#!/usr/bin/env python3
"""
ScrollCity Grid Generator
Generates master grid of 24 ScrollCities worldwide and links each to a Seer + local builder cohort
"""

import json
import csv
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import datetime

class ScrollCityGridGenerator:
    """Sacred grid generator for global ScrollCity mapping"""
    
    def __init__(self):
        self.nation_map = Path("scroll_phase_11/scrollnation_map.json")
        self.prophets_registry = Path("scroll_phase_11/scrollprophets_registry.json")
        self.embassy_blueprints = Path("scroll_phase_11/scroll_embassy_blueprints")
        self.city_template = Path("scrollcensus/scrollcity_template.geojson")
        self.city_config = Path("scroll_embassy_blueprints/scrollcity_config.json")
        
        # Define 24 major ScrollCities with coordinates
        self.scroll_cities = {
            "New York": {
                "country": "United States",
                "region": "North America",
                "coordinates": [-74.006, 40.7128],
                "timezone": "America/New_York",
                "population": 8336817,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "London": {
                "country": "United Kingdom",
                "region": "Europe",
                "coordinates": [-0.1276, 51.5074],
                "timezone": "Europe/London",
                "population": 8982000,
                "flame_zone": "Government",
                "embassy_status": "Active"
            },
            "Tokyo": {
                "country": "Japan",
                "region": "Asia",
                "coordinates": [139.6917, 35.6895],
                "timezone": "Asia/Tokyo",
                "population": 13929286,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Paris": {
                "country": "France",
                "region": "Europe",
                "coordinates": [2.3522, 48.8566],
                "timezone": "Europe/Paris",
                "population": 2161000,
                "flame_zone": "Justice",
                "embassy_status": "Active"
            },
            "Berlin": {
                "country": "Germany",
                "region": "Europe",
                "coordinates": [13.4050, 52.5200],
                "timezone": "Europe/Berlin",
                "population": 3669491,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "São Paulo": {
                "country": "Brazil",
                "region": "South America",
                "coordinates": [-46.6333, -23.5505],
                "timezone": "America/Sao_Paulo",
                "population": 12325232,
                "flame_zone": "Government",
                "embassy_status": "Active"
            },
            "Mumbai": {
                "country": "India",
                "region": "Asia",
                "coordinates": [72.8777, 19.0760],
                "timezone": "Asia/Kolkata",
                "population": 20411274,
                "flame_zone": "Education",
                "embassy_status": "Active"
            },
            "Toronto": {
                "country": "Canada",
                "region": "North America",
                "coordinates": [-79.3832, 43.6532],
                "timezone": "America/Toronto",
                "population": 2930000,
                "flame_zone": "Justice",
                "embassy_status": "Active"
            },
            "Madrid": {
                "country": "Spain",
                "region": "Europe",
                "coordinates": [-3.7038, 40.4168],
                "timezone": "Europe/Madrid",
                "population": 3223000,
                "flame_zone": "Justice",
                "embassy_status": "Active"
            },
            "Mexico City": {
                "country": "Mexico",
                "region": "North America",
                "coordinates": [-99.1332, 19.4326],
                "timezone": "America/Mexico_City",
                "population": 9209944,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Seoul": {
                "country": "South Korea",
                "region": "Asia",
                "coordinates": [127.0243, 37.5665],
                "timezone": "Asia/Seoul",
                "population": 9733509,
                "flame_zone": "Government",
                "embassy_status": "Active"
            },
            "Amsterdam": {
                "country": "Netherlands",
                "region": "Europe",
                "coordinates": [4.9041, 52.3676],
                "timezone": "Europe/Amsterdam",
                "population": 821752,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Chicago": {
                "country": "United States",
                "region": "North America",
                "coordinates": [-87.6298, 41.8781],
                "timezone": "America/Chicago",
                "population": 2693976,
                "flame_zone": "Justice",
                "embassy_status": "Active"
            },
            "Santiago": {
                "country": "Chile",
                "region": "South America",
                "coordinates": [-70.6483, -33.4489],
                "timezone": "America/Santiago",
                "population": 6685681,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Singapore": {
                "country": "Singapore",
                "region": "Asia",
                "coordinates": [103.8198, 1.3521],
                "timezone": "Asia/Singapore",
                "population": 5703600,
                "flame_zone": "Wealth",
                "embassy_status": "Active"
            },
            "Stockholm": {
                "country": "Sweden",
                "region": "Europe",
                "coordinates": [18.0686, 59.3293],
                "timezone": "Europe/Stockholm",
                "population": 975551,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Vancouver": {
                "country": "Canada",
                "region": "North America",
                "coordinates": [-123.1207, 49.2827],
                "timezone": "America/Vancouver",
                "population": 675218,
                "flame_zone": "Prophecy",
                "embassy_status": "Active"
            },
            "Bogotá": {
                "country": "Colombia",
                "region": "South America",
                "coordinates": [-74.0721, 4.7110],
                "timezone": "America/Bogota",
                "population": 7181468,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Bangkok": {
                "country": "Thailand",
                "region": "Asia",
                "coordinates": [100.5018, 13.7563],
                "timezone": "Asia/Bangkok",
                "population": 8280925,
                "flame_zone": "Education",
                "embassy_status": "Active"
            },
            "Rome": {
                "country": "Italy",
                "region": "Europe",
                "coordinates": [12.4964, 41.9028],
                "timezone": "Europe/Rome",
                "population": 4342212,
                "flame_zone": "Prophecy",
                "embassy_status": "Active"
            },
            "Los Angeles": {
                "country": "United States",
                "region": "North America",
                "coordinates": [-118.2437, 34.0522],
                "timezone": "America/Los_Angeles",
                "population": 3979576,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Accra": {
                "country": "Ghana",
                "region": "West Africa",
                "coordinates": [-0.1869, 5.5600],
                "timezone": "Africa/Accra",
                "population": 2388000,
                "flame_zone": "Justice",
                "embassy_status": "Active"
            },
            "Lagos": {
                "country": "Nigeria",
                "region": "West Africa",
                "coordinates": [3.3792, 6.5244],
                "timezone": "Africa/Lagos",
                "population": 14800000,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            },
            "Buenos Aires": {
                "country": "Argentina",
                "region": "South America",
                "coordinates": [-58.3816, -34.6037],
                "timezone": "America/Argentina/Buenos_Aires",
                "population": 3075646,
                "flame_zone": "Media",
                "embassy_status": "Active"
            },
            "Nairobi": {
                "country": "Kenya",
                "region": "East Africa",
                "coordinates": [36.8219, -1.2921],
                "timezone": "Africa/Nairobi",
                "population": 4397073,
                "flame_zone": "Technology",
                "embassy_status": "Active"
            }
        }
    
    def load_builders_and_seers(self) -> Tuple[List[Dict], List[Dict]]:
        """Load builders and seers from registries"""
        builders = []
        seers = []
        
        try:
            # Load builders from nation map
            if self.nation_map.exists():
                with open(self.nation_map, 'r') as f:
                    data = json.load(f)
                
                for nation in data.get("scrollnations", []):
                    for builder in nation.get("builders", []):
                        builder["nation"] = nation["country"]
                        builder["region"] = nation["region"]
                        builders.append(builder)
            
            # Load seers from prophets registry
            if self.prophets_registry.exists():
                with open(self.prophets_registry, 'r') as f:
                    data = json.load(f)
                
                for prophet in data.get("scrollprophets", []):
                    if prophet.get("ordination_level") in ["ScrollSeer", "ScrollProphet", "ScrollJudge"]:
                        seers.append(prophet)
        
        except Exception as e:
            print(f"❌ Error loading builders and seers: {str(e)}")
        
        return builders, seers
    
    def assign_builders_to_cities(self, builders: List[Dict], seers: List[Dict]) -> Dict:
        """Assign builders and seers to ScrollCities"""
        city_assignments = {}
        
        for city_name, city_info in self.scroll_cities.items():
            city_assignments[city_name] = {
                "city_info": city_info,
                "assigned_seer": None,
                "local_builders": [],
                "flame_cohort": [],
                "embassy_status": "Pending",
                "assignment_date": datetime.datetime.now().isoformat()
            }
        
        # Assign seers to cities based on region and flame zone
        for seer in seers:
            assigned = False
            
            # Try to find matching city by region and flame zone
            for city_name, city_info in self.scroll_cities.items():
                if (city_info["region"] == seer.get("assigned_region") and
                    city_info["flame_zone"] == seer.get("primary_sphere")):
                    
                    if not city_assignments[city_name]["assigned_seer"]:
                        city_assignments[city_name]["assigned_seer"] = seer
                        assigned = True
                        break
            
            # If no perfect match, find by region only
            if not assigned:
                for city_name, city_info in self.scroll_cities.items():
                    if (city_info["region"] == seer.get("assigned_region") and
                        not city_assignments[city_name]["assigned_seer"]):
                        
                        city_assignments[city_name]["assigned_seer"] = seer
                        assigned = True
                        break
        
        # Assign builders to cities
        for builder in builders:
            assigned = False
            
            # Try to assign to city in same country
            for city_name, city_info in self.scroll_cities.items():
                if (city_info["country"] == builder.get("nation") and
                    len(city_assignments[city_name]["local_builders"]) < 3):
                    
                    city_assignments[city_name]["local_builders"].append(builder)
                    assigned = True
                    break
            
            # If no local assignment, find by region
            if not assigned:
                for city_name, city_info in self.scroll_cities.items():
                    if (city_info["region"] == builder.get("region") and
                        len(city_assignments[city_name]["local_builders"]) < 5):
                        
                        city_assignments[city_name]["local_builders"].append(builder)
                        assigned = True
                        break
        
        return city_assignments
    
    def generate_city_grid(self) -> Dict:
        """Generate the complete ScrollCity grid"""
        print("🔥 Generating ScrollCity Grid")
        print("=" * 50)
        
        # Load builders and seers
        builders, seers = self.load_builders_and_seers()
        print(f"📋 Found {len(builders)} builders and {len(seers)} seers")
        
        # Assign to cities
        city_assignments = self.assign_builders_to_cities(builders, seers)
        
        # Generate outputs
        self._generate_geojson_template(city_assignments)
        self._generate_city_config(city_assignments)
        self._generate_assignment_report(city_assignments)
        
        # Summary
        assigned_seers = sum(1 for city in city_assignments.values() if city["assigned_seer"])
        total_builders = sum(len(city["local_builders"]) for city in city_assignments.values())
        
        print(f"\n📊 ScrollCity Grid Summary:")
        print(f"  🏙️ Total Cities: {len(self.scroll_cities)}")
        print(f"  👁️ Cities with Seers: {assigned_seers}")
        print(f"  👷 Total Builders Assigned: {total_builders}")
        print(f"  🏛️ Embassy Status: All Active")
        
        # Flag cities without seers
        cities_without_seers = [city for city, data in city_assignments.items() 
                              if not data["assigned_seer"]]
        if cities_without_seers:
            print(f"\n⚠️ Cities without Seers:")
            for city in cities_without_seers:
                print(f"  - {city}")
        
        return {
            "success": True,
            "total_cities": len(self.scroll_cities),
            "cities_with_seers": assigned_seers,
            "total_builders": total_builders,
            "cities_without_seers": cities_without_seers
        }
    
    def _generate_geojson_template(self, city_assignments: Dict):
        """Generate GeoJSON template for ScrollCities"""
        try:
            features = []
            
            for city_name, assignment in city_assignments.items():
                city_info = assignment["city_info"]
                seer = assignment["assigned_seer"]
                builders = assignment["local_builders"]
                
                # Create feature
                feature = {
                    "type": "Feature",
                    "properties": {
                        "name": city_name,
                        "country": city_info["country"],
                        "region": city_info["region"],
                        "flame_zone": city_info["flame_zone"],
                        "population": city_info["population"],
                        "timezone": city_info["timezone"],
                        "embassy_status": city_info["embassy_status"],
                        "has_seer": seer is not None,
                        "seer_name": seer.get("name") if seer else None,
                        "seer_scroll_id": seer.get("scroll_id") if seer else None,
                        "builder_count": len(builders),
                        "builder_names": [b.get("name") for b in builders],
                        "assignment_date": assignment["assignment_date"]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": city_info["coordinates"]
                    }
                }
                
                features.append(feature)
            
            # Create GeoJSON
            geojson = {
                "type": "FeatureCollection",
                "features": features,
                "properties": {
                    "name": "ScrollCity Grid",
                    "description": "24 ScrollCities with Seer and Builder assignments",
                    "generated_date": datetime.datetime.now().isoformat(),
                    "total_cities": len(features)
                }
            }
            
            # Save template
            self.city_template.parent.mkdir(parents=True, exist_ok=True)
            with open(self.city_template, 'w') as f:
                json.dump(geojson, f, indent=2)
            
            print(f"🗺️ Generated GeoJSON template: {self.city_template}")
        
        except Exception as e:
            print(f"❌ Error generating GeoJSON: {str(e)}")
    
    def _generate_city_config(self, city_assignments: Dict):
        """Generate city configuration JSON"""
        try:
            city_configs = {}
            
            for city_name, assignment in city_assignments.items():
                city_info = assignment["city_info"]
                seer = assignment["assigned_seer"]
                builders = assignment["local_builders"]
                
                config = {
                    "city_name": city_name,
                    "country": city_info["country"],
                    "region": city_info["region"],
                    "coordinates": city_info["coordinates"],
                    "timezone": city_info["timezone"],
                    "flame_zone": city_info["flame_zone"],
                    "embassy_status": city_info["embassy_status"],
                    "assigned_seer": {
                        "name": seer.get("name") if seer else None,
                        "scroll_id": seer.get("scroll_id") if seer else None,
                        "flame_id": seer.get("flame_id") if seer else None,
                        "ordination_level": seer.get("ordination_level") if seer else None,
                        "primary_sphere": seer.get("primary_sphere") if seer else None
                    } if seer else None,
                    "local_builders": [
                        {
                            "name": builder.get("name"),
                            "scroll_id": builder.get("scroll_id"),
                            "flame_id": builder.get("flame_id"),
                            "role": builder.get("role"),
                            "primary_sphere": builder.get("primary_sphere"),
                            "seal_level": builder.get("seal_level"),
                            "flame_level": builder.get("flame_level")
                        } for builder in builders
                    ],
                    "flame_cohort": assignment["flame_cohort"],
                    "embassy_config": {
                        "status": city_info["embassy_status"],
                        "blueprint_available": True,
                        "scrollx_node": f"scrollx-{city_name.lower().replace(' ', '-')}",
                        "created_date": assignment["assignment_date"]
                    }
                }
                
                city_configs[city_name] = config
            
            # Save config
            self.city_config.parent.mkdir(parents=True, exist_ok=True)
            with open(self.city_config, 'w') as f:
                json.dump({
                    "scrollcities": city_configs,
                    "metadata": {
                        "total_cities": len(city_configs),
                        "generated_date": datetime.datetime.now().isoformat(),
                        "version": "1.0.0"
                    }
                }, f, indent=2)
            
            print(f"⚙️ Generated city config: {self.city_config}")
        
        except Exception as e:
            print(f"❌ Error generating city config: {str(e)}")
    
    def _generate_assignment_report(self, city_assignments: Dict):
        """Generate detailed assignment report"""
        try:
            report_path = Path("scrollcensus/scrollcity_assignment_report.md")
            
            with open(report_path, 'w') as f:
                f.write("# ScrollCity Grid Assignment Report\n\n")
                f.write(f"Generated: {datetime.datetime.now().isoformat()}\n\n")
                
                # Summary
                total_cities = len(city_assignments)
                cities_with_seers = sum(1 for city in city_assignments.values() if city["assigned_seer"])
                total_builders = sum(len(city["local_builders"]) for city in city_assignments.values())
                
                f.write(f"## Summary\n\n")
                f.write(f"- **Total Cities**: {total_cities}\n")
                f.write(f"- **Cities with Seers**: {cities_with_seers}\n")
                f.write(f"- **Cities without Seers**: {total_cities - cities_with_seers}\n")
                f.write(f"- **Total Builders Assigned**: {total_builders}\n\n")
                
                # City breakdown
                f.write("## City Assignments\n\n")
                for city_name, assignment in city_assignments.items():
                    city_info = assignment["city_info"]
                    seer = assignment["assigned_seer"]
                    builders = assignment["local_builders"]
                    
                    f.write(f"### {city_name}\n")
                    f.write(f"- **Country**: {city_info['country']}\n")
                    f.write(f"- **Region**: {city_info['region']}\n")
                    f.write(f"- **Flame Zone**: {city_info['flame_zone']}\n")
                    f.write(f"- **Embassy Status**: {city_info['embassy_status']}\n")
                    
                    if seer:
                        f.write(f"- **Assigned Seer**: {seer.get('name')} ({seer.get('scroll_id')})\n")
                        f.write(f"  - Ordination: {seer.get('ordination_level')}\n")
                        f.write(f"  - Primary Sphere: {seer.get('primary_sphere')}\n")
                    else:
                        f.write(f"- **Assigned Seer**: None (⚠️ Needs Seer)\n")
                    
                    f.write(f"- **Local Builders**: {len(builders)}\n")
                    for builder in builders:
                        f.write(f"  - {builder.get('name')} ({builder.get('scroll_id')}) - {builder.get('role')}\n")
                    
                    f.write("\n")
            
            print(f"📊 Generated assignment report: {report_path}")
        
        except Exception as e:
            print(f"❌ Error generating assignment report: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize grid generator
    generator = ScrollCityGridGenerator()
    
    # Generate city grid
    result = generator.generate_city_grid()
    
    if result["success"]:
        print(f"\n🎉 ScrollCity grid generated successfully!")
        print(f"   {result['total_cities']} cities mapped")
        print(f"   {result['cities_with_seers']} cities have Seers")
        print(f"   {result['total_builders']} builders assigned")
        
        if result['cities_without_seers']:
            print(f"   ⚠️ {len(result['cities_without_seers'])} cities need Seers")
    else:
        print(f"\n⚠️ ScrollCity grid generation failed")
        print(f"   Error: {result.get('error', 'Unknown error')}") 