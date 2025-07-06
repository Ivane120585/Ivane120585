#!/usr/bin/env python3
"""
Scroll Embassy Initializer
Initializes ScrollEmbassy for a new city
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import datetime

class ScrollEmbassyInitializer:
    """Sacred initializer for creating new ScrollEmbassies"""
    
    def __init__(self):
        self.embassy_config_dir = Path("scroll_phase_11/scroll_embassy_blueprints")
        self.nation_map_file = Path("scroll_phase_11/scrollnation_map.json")
        self.scrollx_nodes_dir = Path("scrollx_marketplace")
        
    def initialize_embassy(self, city_name: str, country: str, region: str = None) -> Dict:
        """
        Initialize ScrollEmbassy for a new city
        
        Args:
            city_name: Name of the city
            country: Country name
            region: Geographic region
            
        Returns:
            Embassy configuration dictionary
        """
        try:
            print(f"🏛️ Initializing ScrollEmbassy for {city_name}, {country}")
            
            # Create embassy configuration
            embassy_config = self._create_embassy_config(city_name, country, region)
            
            # Assign local builders
            self._assign_local_builders(embassy_config)
            
            # Initialize ScrollX satellite node
            self._initialize_scrollx_node(embassy_config)
            
            # Generate visual grid if template exists
            self._generate_visual_grid(embassy_config)
            
            # Save embassy configuration
            self._save_embassy_config(embassy_config)
            
            print(f"✅ ScrollEmbassy initialized for {city_name}")
            return embassy_config
            
        except Exception as e:
            print(f"❌ Error initializing embassy: {str(e)}")
            return {}
    
    def _create_embassy_config(self, city_name: str, country: str, region: str = None) -> Dict:
        """Create embassy configuration"""
        embassy_id = f"EMBASSY_{city_name.upper().replace(' ', '_')}"
        
        config = {
            "embassy_id": embassy_id,
            "city": city_name,
            "country": country,
            "region": region or "Unknown",
            "status": "Initialized",
            "created_date": datetime.datetime.now().isoformat(),
            "embassy_zones": {
                "altar_zone": {
                    "description": "Sacred flame altar for scroll consecration",
                    "capacity": 50,
                    "status": "Active"
                },
                "council_chamber": {
                    "description": "SeerCircle deliberation chamber",
                    "capacity": 25,
                    "status": "Active"
                },
                "learning_hall": {
                    "description": "Scroll education and training center",
                    "capacity": 100,
                    "status": "Active"
                },
                "treasury": {
                    "description": "ScrollCoin vault and financial center",
                    "capacity": 10,
                    "status": "Active"
                },
                "scrollide_terminal": {
                    "description": "ScrollIDE development environment",
                    "capacity": 20,
                    "status": "Active"
                }
            },
            "assigned_builders": [],
            "assigned_seers": [],
            "flame_zones": {},
            "scrollx_node": {
                "node_id": f"SCROLLX_{city_name.upper().replace(' ', '_')}",
                "status": "Initialized",
                "products": [],
                "transactions": []
            },
            "satellite_portal": {
                "url": f"https://scrollverse.com/{city_name.lower().replace(' ', '-')}",
                "status": "Active",
                "features": ["Builder Dashboard", "Marketplace", "Learning Zone", "Judgment Zone"]
            }
        }
        
        return config
    
    def _assign_local_builders(self, embassy_config: Dict):
        """Assign local builders to embassy"""
        try:
            # Load nation map to find local builders
            if self.nation_map_file.exists():
                with open(self.nation_map_file, 'r') as f:
                    nation_map = json.load(f)
                
                city = embassy_config["city"]
                country = embassy_config["country"]
                
                # Find builders in the same city/country
                for nation in nation_map.get("scrollnations", []):
                    if nation["country"] == country:
                        for builder in nation.get("builders", []):
                            if builder["city"] == city:
                                embassy_config["assigned_builders"].append({
                                    "scroll_id": builder["scroll_id"],
                                    "name": builder["name"],
                                    "role": builder["role"],
                                    "primary_sphere": builder["primary_sphere"],
                                    "seal_level": builder["seal_level"]
                                })
                                
                                # Add to seers if applicable
                                if builder["role"] in ["ScrollSeer", "ScrollProphet", "ScrollJudge"]:
                                    embassy_config["assigned_seers"].append({
                                        "scroll_id": builder["scroll_id"],
                                        "name": builder["name"],
                                        "role": builder["role"],
                                        "ordination_level": builder.get("ordination_level", "FlameBearer")
                                    })
                
                print(f"👥 Assigned {len(embassy_config['assigned_builders'])} builders to embassy")
                print(f"👁️ Assigned {len(embassy_config['assigned_seers'])} seers to embassy")
        
        except Exception as e:
            print(f"❌ Error assigning local builders: {str(e)}")
    
    def _initialize_scrollx_node(self, embassy_config: Dict):
        """Initialize ScrollX satellite node"""
        try:
            node_id = embassy_config["scrollx_node"]["node_id"]
            city_name = embassy_config["city"]
            
            # Create node directory
            node_dir = self.scrollx_nodes_dir / node_id
            node_dir.mkdir(parents=True, exist_ok=True)
            
            # Create node configuration
            node_config = {
                "node_id": node_id,
                "city": city_name,
                "country": embassy_config["country"],
                "status": "Active",
                "created_date": datetime.datetime.now().isoformat(),
                "products": [],
                "transactions": [],
                "local_builders": len(embassy_config["assigned_builders"]),
                "local_seers": len(embassy_config["assigned_seers"])
            }
            
            # Save node config
            with open(node_dir / "node_config.json", 'w') as f:
                json.dump(node_config, f, indent=2)
            
            # Create products catalog
            products_catalog = {
                "node_id": node_id,
                "city": city_name,
                "products": [],
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            with open(node_dir / "products_catalog.json", 'w') as f:
                json.dump(products_catalog, f, indent=2)
            
            print(f"📦 Initialized ScrollX node: {node_id}")
        
        except Exception as e:
            print(f"❌ Error initializing ScrollX node: {str(e)}")
    
    def _generate_visual_grid(self, embassy_config: Dict):
        """Generate visual grid if template exists"""
        try:
            template_file = self.embassy_config_dir / "scrolltemple_layout.dxf"
            
            if template_file.exists():
                print(f"🎨 Generating visual grid for {embassy_config['city']}")
                
                # Create visual grid configuration
                grid_config = {
                    "embassy_id": embassy_config["embassy_id"],
                    "city": embassy_config["city"],
                    "grid_type": "sacred_geometry",
                    "zones": list(embassy_config["embassy_zones"].keys()),
                    "generated_date": datetime.datetime.now().isoformat()
                }
                
                # Save grid config
                grid_file = self.embassy_config_dir / f"{embassy_config['embassy_id']}_grid.json"
                with open(grid_file, 'w') as f:
                    json.dump(grid_config, f, indent=2)
                
                print(f"🎨 Visual grid generated: {grid_file}")
            else:
                print(f"ℹ️ No visual template found for {embassy_config['city']}")
        
        except Exception as e:
            print(f"❌ Error generating visual grid: {str(e)}")
    
    def _save_embassy_config(self, embassy_config: Dict):
        """Save embassy configuration"""
        try:
            # Create embassy config file
            config_file = self.embassy_config_dir / f"{embassy_config['embassy_id']}_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump(embassy_config, f, indent=2)
            
            # Update city template
            self._update_city_template(embassy_config)
            
            print(f"💾 Embassy config saved: {config_file}")
        
        except Exception as e:
            print(f"❌ Error saving embassy config: {str(e)}")
    
    def _update_city_template(self, embassy_config: Dict):
        """Update city template with new embassy"""
        try:
            city_template_file = self.embassy_config_dir / "scrollcity_template.geojson"
            
            if city_template_file.exists():
                with open(city_template_file, 'r') as f:
                    city_template = json.load(f)
                
                # Add new embassy to template
                embassy_feature = {
                    "type": "Feature",
                    "properties": {
                        "name": embassy_config["city"],
                        "country": embassy_config["country"],
                        "embassy_id": embassy_config["embassy_id"],
                        "embassy_status": embassy_config["status"],
                        "builders_count": len(embassy_config["assigned_builders"]),
                        "seers_count": len(embassy_config["assigned_seers"]),
                        "created_date": embassy_config["created_date"]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [0, 0]  # Placeholder coordinates
                    }
                }
                
                city_template["features"].append(embassy_feature)
                
                # Save updated template
                with open(city_template_file, 'w') as f:
                    json.dump(city_template, f, indent=2)
                
                print(f"🗺️ Updated city template with {embassy_config['city']} embassy")
        
        except Exception as e:
            print(f"❌ Error updating city template: {str(e)}")
    
    def get_embassy_status(self, city_name: str) -> Optional[Dict]:
        """Get embassy status for a city"""
        try:
            embassy_id = f"EMBASSY_{city_name.upper().replace(' ', '_')}"
            config_file = self.embassy_config_dir / f"{embassy_id}_config.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                return None
        
        except Exception as e:
            print(f"❌ Error getting embassy status: {str(e)}")
            return None
    
    def list_embassies(self) -> List[Dict]:
        """List all initialized embassies"""
        try:
            embassies = []
            
            if self.embassy_config_dir.exists():
                for config_file in self.embassy_config_dir.glob("*_config.json"):
                    with open(config_file, 'r') as f:
                        embassy_config = json.load(f)
                        embassies.append({
                            "embassy_id": embassy_config["embassy_id"],
                            "city": embassy_config["city"],
                            "country": embassy_config["country"],
                            "status": embassy_config["status"],
                            "builders_count": len(embassy_config["assigned_builders"]),
                            "seers_count": len(embassy_config["assigned_seers"]),
                            "created_date": embassy_config["created_date"]
                        })
            
            return embassies
        
        except Exception as e:
            print(f"❌ Error listing embassies: {str(e)}")
            return []

# Example usage and testing
if __name__ == "__main__":
    # Initialize embassy initializer
    initializer = ScrollEmbassyInitializer()
    
    # Test embassy initialization
    test_cities = [
        ("Accra", "Ghana", "West Africa"),
        ("Lagos", "Nigeria", "West Africa"),
        ("Nairobi", "Kenya", "East Africa"),
        ("Cairo", "Egypt", "North Africa")
    ]
    
    print("🏛️ Testing Scroll Embassy Initializer:")
    print("=" * 50)
    
    for city, country, region in test_cities:
        print(f"\n🔥 Initializing embassy for {city}, {country}")
        embassy_config = initializer.initialize_embassy(city, country, region)
        
        if embassy_config:
            print(f"✅ Embassy initialized: {embassy_config['embassy_id']}")
            print(f"   Builders: {len(embassy_config['assigned_builders'])}")
            print(f"   Seers: {len(embassy_config['assigned_seers'])}")
            print(f"   ScrollX Node: {embassy_config['scrollx_node']['node_id']}")
    
    # List all embassies
    print(f"\n📋 Embassy Summary:")
    embassies = initializer.list_embassies()
    for embassy in embassies:
        print(f"  {embassy['city']}, {embassy['country']}: {embassy['builders_count']} builders, {embassy['seers_count']} seers") 