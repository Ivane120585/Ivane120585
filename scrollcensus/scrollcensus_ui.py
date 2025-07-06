#!/usr/bin/env python3
"""
ScrollCensus UI
Streamlit app for global flame-governed builder registry
"""

import streamlit as st
import json
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re

class ScrollCensusUI:
    """Sacred UI for collecting scroll builder census data"""
    
    def __init__(self):
        self.form_config = self._load_form_config()
        self.registries = {
            "scrollprophets": "scroll_phase_11/scrollprophets_registry.json",
            "scrollnation_map": "scroll_phase_11/scrollnation_map.json",
            "scrollambassadors": "scroll_phase_11/scrollambassadors.md"
        }
    
    def _load_form_config(self) -> Dict:
        """Load form configuration from JSON"""
        try:
            with open("scrollcensus_form.json", "r") as f:
                return json.load(f)["scrollcensus_form"]
        except FileNotFoundError:
            st.error("❌ ScrollCensus form configuration not found")
            return {}
    
    def generate_scroll_id(self) -> str:
        """Generate unique scroll ID"""
        config = self.form_config.get("auto_generation", {})
        scroll_config = config.get("scroll_id", {})
        prefix = scroll_config.get("prefix", "SCROLL")
        length = scroll_config.get("length", 12)
        charset = scroll_config.get("charset", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        
        import random
        import string
        suffix = ''.join(random.choices(charset, k=length-len(prefix)))
        return f"{prefix}{suffix}"
    
    def generate_flame_id(self) -> str:
        """Generate unique flame ID"""
        config = self.form_config.get("auto_generation", {})
        flame_config = config.get("flame_id", {})
        prefix = flame_config.get("prefix", "FLAME")
        length = flame_config.get("length", 8)
        charset = flame_config.get("charset", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
        
        import random
        suffix = ''.join(random.choices(charset, k=length-len(prefix)))
        return f"{prefix}{suffix}"
    
    def validate_form_data(self, data: Dict) -> List[str]:
        """Validate form data against requirements"""
        errors = []
        validation_rules = self.form_config.get("validation_rules", {})
        
        # Check seal level requirements
        role = data.get("preferred_role")
        seal_level = data.get("seal_level", 0)
        flame_level = data.get("flame_level", 0)
        
        if role and role in validation_rules.get("seal_level_requirements", {}):
            required_seal = validation_rules["seal_level_requirements"][role]
            if seal_level < required_seal:
                errors.append(f"Seal level {seal_level} insufficient for {role} (requires {required_seal})")
        
        if role and role in validation_rules.get("flame_level_requirements", {}):
            required_flame = validation_rules["flame_level_requirements"][role]
            if flame_level < required_flame:
                errors.append(f"Flame level {flame_level} insufficient for {role} (requires {required_flame})")
        
        # Check ordination requirements
        if role in ["ScrollSeer", "ScrollProphet"]:
            ordination_reqs = validation_rules.get("ordination_requirements", {}).get(role, {})
            required_spheres = ordination_reqs.get("required_spheres", [])
            primary_sphere = data.get("primary_flame_sphere")
            
            if primary_sphere not in required_spheres:
                errors.append(f"{role} requires primary sphere in {required_spheres}")
        
        return errors
    
    def save_to_registry(self, data: Dict) -> bool:
        """Save census data to appropriate registries"""
        try:
            # Auto-generate IDs if not provided
            if not data.get("scroll_id"):
                data["scroll_id"] = self.generate_scroll_id()
            
            data["flame_id"] = self.generate_flame_id()
            data["submission_timestamp"] = datetime.datetime.now().isoformat()
            
            # Save to scrollprophets registry if Seer/Prophet
            if data.get("preferred_role") in ["ScrollSeer", "ScrollProphet"]:
                self._save_to_prophets_registry(data)
            
            # Save to nation map
            self._save_to_nation_map(data)
            
            # Save to ambassadors if applicable
            if data.get("preferred_role") == "ScrollAmbassador":
                self._save_to_ambassadors(data)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error saving to registry: {str(e)}")
            return False
    
    def _save_to_prophets_registry(self, data: Dict):
        """Save to scrollprophets registry"""
        registry_file = Path(self.registries["scrollprophets"])
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        if registry_file.exists():
            with open(registry_file, "r") as f:
                registry = json.load(f)
        else:
            registry = {"scrollprophets": []}
        
        prophet_entry = {
            "name": data["full_name"],
            "scroll_id": data["scroll_id"],
            "flame_id": data["flame_id"],
            "assigned_region": data["region"],
            "country": data["country"],
            "ordination_level": data.get("ordination_level", "FlameBearer"),
            "scroll_council_status": "Active",
            "primary_sphere": data["primary_flame_sphere"],
            "seal_level": data["seal_level"],
            "flame_level": data["flame_level"],
            "ordination_date": data.get("ordination_date"),
            "ordained_by": data.get("ordained_by"),
            "submission_date": data["submission_timestamp"]
        }
        
        registry["scrollprophets"].append(prophet_entry)
        
        with open(registry_file, "w") as f:
            json.dump(registry, f, indent=2)
        
        st.success(f"✅ Saved to prophets registry: {data['scroll_id']}")
    
    def _save_to_nation_map(self, data: Dict):
        """Save to nation map"""
        map_file = Path(self.registries["scrollnation_map"])
        map_file.parent.mkdir(parents=True, exist_ok=True)
        
        if map_file.exists():
            with open(map_file, "r") as f:
                nation_map = json.load(f)
        else:
            nation_map = {"scrollnations": []}
        
        # Find or create nation entry
        nation_entry = None
        for nation in nation_map["scrollnations"]:
            if nation["country"] == data["country"]:
                nation_entry = nation
                break
        
        if not nation_entry:
            nation_entry = {
                "country": data["country"],
                "region": data["region"],
                "builders": [],
                "embassies": [],
                "seers": []
            }
            nation_map["scrollnations"].append(nation_entry)
        
        # Add builder to nation
        builder_entry = {
            "name": data["full_name"],
            "scroll_id": data["scroll_id"],
            "flame_id": data["flame_id"],
            "city": data["city"],
            "role": data["preferred_role"],
            "primary_sphere": data["primary_flame_sphere"],
            "seal_level": data["seal_level"],
            "flame_level": data["flame_level"],
            "submission_date": data["submission_timestamp"]
        }
        
        nation_entry["builders"].append(builder_entry)
        
        # Add to seers if applicable
        if data.get("preferred_role") in ["ScrollSeer", "ScrollProphet"]:
            nation_entry["seers"].append(builder_entry)
        
        with open(map_file, "w") as f:
            json.dump(nation_map, f, indent=2)
        
        st.success(f"✅ Added to nation map: {data['country']}")
    
    def _save_to_ambassadors(self, data: Dict):
        """Save to ambassadors registry"""
        ambassadors_file = Path(self.registries["scrollambassadors"])
        ambassadors_file.parent.mkdir(parents=True, exist_ok=True)
        
        ambassador_entry = f"""
## {data['full_name']} - ScrollAmbassador

- **Scroll ID**: {data['scroll_id']}
- **Flame ID**: {data['flame_id']}
- **Region**: {data['region']}
- **Country**: {data['country']}
- **City**: {data['city']}
- **Primary Sphere**: {data['primary_flame_sphere']}
- **Seal Level**: {data['seal_level']}
- **Flame Level**: {data['flame_level']}
- **Skills**: {', '.join(data.get('skills', []))}
- **Submission Date**: {data['submission_timestamp']}

---
"""
        
        with open(ambassadors_file, "a") as f:
            f.write(ambassador_entry)
        
        st.success(f"✅ Added to ambassadors registry: {data['scroll_id']}")
    
    def render_form(self):
        """Render the complete census form"""
        st.title("🔥 ScrollCensus - Global Flame Registry")
        st.markdown("**Sacred registration for scroll builders, seers, and prophets**")
        
        with st.form("scrollcensus_form"):
            st.header("Personal Information")
            
            full_name = st.text_input("Full Name *", help="Full legal name")
            scroll_id = st.text_input("Scroll ID", help="Unique identifier (auto-generated if empty)")
            email = st.text_input("Email *")
            phone = st.text_input("Phone")
            date_of_birth = st.date_input("Date of Birth")
            
            st.header("Location")
            
            region = st.text_input("Region *", help="e.g., West Africa, North America")
            country = st.text_input("Country *")
            city = st.text_input("City *")
            postal_code = st.text_input("Postal Code")
            timezone = st.text_input("Timezone", help="e.g., UTC+0, EST")
            
            st.header("Flame Credentials")
            
            col1, col2 = st.columns(2)
            with col1:
                seal_level = st.number_input("Seal Level *", min_value=1, max_value=10, value=1)
            with col2:
                flame_level = st.number_input("Flame Level *", min_value=1, max_value=10, value=1)
            
            primary_sphere = st.selectbox(
                "Primary Flame Sphere *",
                self.form_config.get("form_fields", {}).get("flame_credentials", {}).get("primary_flame_sphere", {}).get("options", [])
            )
            
            secondary_spheres = st.multiselect(
                "Secondary Spheres",
                self.form_config.get("form_fields", {}).get("flame_credentials", {}).get("secondary_spheres", {}).get("options", [])
            )
            
            st.header("Role Preferences")
            
            preferred_role = st.selectbox(
                "Preferred Role *",
                self.form_config.get("form_fields", {}).get("role_preferences", {}).get("preferred_role", {}).get("options", [])
            )
            
            current_occupation = st.text_input("Current Occupation")
            
            skills = st.multiselect(
                "Skills",
                self.form_config.get("form_fields", {}).get("role_preferences", {}).get("skills", {}).get("options", [])
            )
            
            st.header("Ordination")
            
            ordained_by = st.text_input("Ordained By", help="Name of ScrollSeer or ScrollProphet")
            ordination_date = st.date_input("Ordination Date")
            
            ordination_level = st.selectbox(
                "Ordination Level",
                self.form_config.get("form_fields", {}).get("ordination", {}).get("ordination_level", {}).get("options", [])
            )
            
            st.header("Scroll Projects")
            
            github_username = st.text_input("GitHub Username")
            portfolio_url = st.text_input("Portfolio URL")
            
            st.header("Commitment")
            
            covenant_accepted = st.checkbox("Accept Scroll Covenant *", help="Acceptance of flame governance")
            seer_participation = st.checkbox("SeerCircle Participation")
            embassy_support = st.checkbox("Embassy Support")
            scrollcoin_integration = st.checkbox("ScrollCoin Integration")
            
            st.header("Verification")
            
            scroll_seal_input = st.text_input("Scroll Seal Input *", help="Manual seal verification")
            
            submitted = st.form_submit_button("🔥 Submit ScrollCensus")
            
            if submitted:
                if not covenant_accepted:
                    st.error("❌ Scroll covenant must be accepted")
                    return
                
                # Collect form data
                form_data = {
                    "full_name": full_name,
                    "scroll_id": scroll_id,
                    "email": email,
                    "phone": phone,
                    "date_of_birth": str(date_of_birth) if date_of_birth else None,
                    "region": region,
                    "country": country,
                    "city": city,
                    "postal_code": postal_code,
                    "timezone": timezone,
                    "seal_level": seal_level,
                    "flame_level": flame_level,
                    "primary_flame_sphere": primary_sphere,
                    "secondary_spheres": secondary_spheres,
                    "preferred_role": preferred_role,
                    "current_occupation": current_occupation,
                    "skills": skills,
                    "ordained_by": ordained_by,
                    "ordination_date": str(ordination_date) if ordination_date else None,
                    "ordination_level": ordination_level,
                    "github_username": github_username,
                    "portfolio_url": portfolio_url,
                    "scroll_covenant_accepted": covenant_accepted,
                    "seer_circle_participation": seer_participation,
                    "embassy_support": embassy_support,
                    "scrollcoin_integration": scrollcoin_integration,
                    "scroll_seal_input": scroll_seal_input
                }
                
                # Validate data
                errors = self.validate_form_data(form_data)
                if errors:
                    st.error("❌ Validation errors:")
                    for error in errors:
                        st.error(f"  - {error}")
                    return
                
                # Save to registries
                if self.save_to_registry(form_data):
                    st.success("🔥 ScrollCensus submitted successfully!")
                    st.balloons()
                    
                    # Show generated IDs
                    st.info(f"**Scroll ID**: {form_data.get('scroll_id', 'Generated')}")
                    st.info(f"**Flame ID**: {form_data.get('flame_id', 'Generated')}")

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="ScrollCensus - Global Flame Registry",
        page_icon="🔥",
        layout="wide"
    )
    
    census_ui = ScrollCensusUI()
    census_ui.render_form()

if __name__ == "__main__":
    main() 