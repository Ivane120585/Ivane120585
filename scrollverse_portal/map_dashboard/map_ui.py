#!/usr/bin/env python3
"""
ScrollMap UI
Streamlit map viewer of ScrollNations
"""

import streamlit as st
import json
import folium
from streamlit_folium import folium_static
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
import plotly.express as px
import plotly.graph_objects as go

class ScrollMap:
    """Interactive map viewer for ScrollNations"""
    
    def __init__(self):
        self.map_file = Path("scrollverse_portal/map_dashboard/scroll_map.geojson")
        self.seer_zones_file = Path("scrollverse_portal/map_dashboard/seer_zone_overlay.json")
        self.map_data = self.load_map_data()
        self.seer_zones = self.load_seer_zones()
    
    def load_map_data(self) -> Dict:
        """Load map data from GeoJSON file"""
        try:
            with open(self.map_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.error("Map data file not found")
            return {"type": "FeatureCollection", "features": []}
    
    def load_seer_zones(self) -> Dict:
        """Load Seer zone overlay data"""
        try:
            with open(self.seer_zones_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"zones": []}
    
    def create_interactive_map(self) -> folium.Map:
        """Create interactive Folium map"""
        # Calculate center point
        features = self.map_data.get('features', [])
        if not features:
            return folium.Map(location=[0, 0], zoom_start=2)
        
        # Calculate center from all coordinates
        all_coords = []
        for feature in features:
            coords = feature['geometry']['coordinates']
            all_coords.append(coords)
        
        center_lat = sum(coord[1] for coord in all_coords) / len(all_coords)
        center_lon = sum(coord[0] for coord in all_coords) / len(all_coords)
        
        # Create map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=3,
            tiles='OpenStreetMap'
        )
        
        # Add embassy markers
        embassy_layer = folium.FeatureGroup(name="ScrollEmbassies")
        for feature in features:
            if feature['properties']['type'] == 'embassy':
                coords = feature['geometry']['coordinates']
                props = feature['properties']
                
                # Create popup content
                popup_content = f"""
                <div style="width: 200px;">
                    <h4>🏛️ {props['name']}</h4>
                    <p><strong>Location:</strong> {props['location']}</p>
                    <p><strong>Seal Level:</strong> {props['seal_level']}</p>
                    <p><strong>Builders:</strong> {props['builders']}</p>
                    <p><strong>Seers:</strong> {props['seers']}</p>
                    <p><strong>Flame Zone:</strong> {props['flame_zone']}</p>
                    <p><strong>Status:</strong> {props['status']}</p>
                </div>
                """
                
                # Choose icon color based on flame zone
                icon_color = {
                    'Justice': 'red',
                    'Prophecy': 'blue',
                    'Governance': 'green'
                }.get(props['flame_zone'], 'gray')
                
                folium.Marker(
                    location=[coords[1], coords[0]],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='flag'),
                    tooltip=f"🏛️ {props['name']}"
                ).add_to(embassy_layer)
        
        embassy_layer.add_to(m)
        
        # Add city markers
        city_layer = folium.FeatureGroup(name="ScrollCities")
        for feature in features:
            if feature['properties']['type'] == 'city':
                coords = feature['geometry']['coordinates']
                props = feature['properties']
                
                # Create popup content
                builders_list = ", ".join(props['builders'])
                seers_list = ", ".join(props['seers']) if props['seers'] else "None"
                
                popup_content = f"""
                <div style="width: 250px;">
                    <h4>🏙️ {props['name']}</h4>
                    <p><strong>Location:</strong> {props['location']}</p>
                    <p><strong>Builders:</strong> {builders_list}</p>
                    <p><strong>Seers:</strong> {seers_list}</p>
                    <p><strong>Flame Zone:</strong> {props['flame_zone']}</p>
                    <p><strong>Status:</strong> {props['status']}</p>
                </div>
                """
                
                # Choose icon color based on flame zone
                icon_color = {
                    'Justice': 'red',
                    'Prophecy': 'blue',
                    'Governance': 'green'
                }.get(props['flame_zone'], 'gray')
                
                folium.Marker(
                    location=[coords[1], coords[0]],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color=icon_color, icon='building'),
                    tooltip=f"🏙️ {props['name']}"
                ).add_to(city_layer)
        
        city_layer.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def create_statistics_dashboard(self):
        """Create statistics dashboard"""
        features = self.map_data.get('features', [])
        metadata = self.map_data.get('metadata', {})
        
        # Calculate statistics
        embassies = [f for f in features if f['properties']['type'] == 'embassy']
        cities = [f for f in features if f['properties']['type'] == 'city']
        
        total_builders = sum(f['properties']['builders'] for f in features)
        total_seers = sum(f['properties']['seers'] for f in features)
        
        # Flame zone distribution
        flame_zones = {}
        for feature in features:
            zone = feature['properties']['flame_zone']
            flame_zones[zone] = flame_zones.get(zone, 0) + 1
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏛️ Embassies", len(embassies))
        with col2:
            st.metric("🏙️ Cities", len(cities))
        with col3:
            st.metric("👷 Builders", total_builders)
        with col4:
            st.metric("👁️ Seers", total_seers)
        
        # Flame zone chart
        st.subheader("🔥 Flame Zone Distribution")
        if flame_zones:
            fig = px.pie(
                values=list(flame_zones.values()),
                names=list(flame_zones.keys()),
                title="Distribution by Flame Zone",
                color_discrete_map={
                    'Justice': '#ff4444',
                    'Prophecy': '#4444ff',
                    'Governance': '#44ff44'
                }
            )
            st.plotly_chart(fig)
        
        # Regional statistics
        st.subheader("🌍 Regional Statistics")
        
        # Create regional data
        regional_data = []
        for feature in features:
            props = feature['properties']
            regional_data.append({
                'Region': props['location'].split(', ')[-1],
                'Type': props['type'],
                'Builders': props['builders'],
                'Seers': props['seers'],
                'Flame Zone': props['flame_zone']
            })
        
        if regional_data:
            df = pd.DataFrame(regional_data)
            
            # Regional builder count
            builder_counts = df.groupby('Region')['Builders'].sum().reset_index()
            fig = px.bar(
                builder_counts,
                x='Region',
                y='Builders',
                title="Builders by Region",
                color='Builders',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig)
    
    def create_builder_directory(self):
        """Create builder directory"""
        st.subheader("👷 Builder Directory")
        
        features = self.map_data.get('features', [])
        all_builders = []
        
        for feature in features:
            props = feature['properties']
            location = props['location']
            flame_zone = props['flame_zone']
            
            # Add builders
            for builder in props['builders']:
                builder_type = "Seer" if "ScrollSeer" in builder else "Builder"
                all_builders.append({
                    'Name': builder,
                    'Type': builder_type,
                    'Location': location,
                    'Flame Zone': flame_zone
                })
        
        if all_builders:
            df = pd.DataFrame(all_builders)
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                builder_type_filter = st.selectbox(
                    "Filter by Type",
                    ["All"] + list(df['Type'].unique())
                )
            with col2:
                flame_zone_filter = st.selectbox(
                    "Filter by Flame Zone",
                    ["All"] + list(df['Flame Zone'].unique())
                )
            
            # Apply filters
            filtered_df = df.copy()
            if builder_type_filter != "All":
                filtered_df = filtered_df[filtered_df['Type'] == builder_type_filter]
            if flame_zone_filter != "All":
                filtered_df = filtered_df[filtered_df['Flame Zone'] == flame_zone_filter]
            
            st.dataframe(filtered_df, use_container_width=True)
    
    def create_seer_zone_overlay(self):
        """Create Seer zone overlay visualization"""
        st.subheader("👁️ Seer Zone Overlay")
        
        if not self.seer_zones.get('zones'):
            st.info("No Seer zone data available")
            return
        
        # Create zone visualization
        zones_data = []
        for zone in self.seer_zones['zones']:
            zones_data.append({
                'Seer': zone['seer_name'],
                'Zone': zone['zone_name'],
                'Seal Level': zone['seal_level'],
                'Enforcement Level': zone['enforcement_level'],
                'Builders': len(zone['assigned_builders'])
            })
        
        if zones_data:
            df = pd.DataFrame(zones_data)
            
            # Zone statistics
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df,
                    x='Zone',
                    y='Builders',
                    title="Builders per Seer Zone",
                    color='Seal Level',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig)
            
            with col2:
                fig = px.scatter(
                    df,
                    x='Seal Level',
                    y='Enforcement Level',
                    size='Builders',
                    color='Zone',
                    title="Seer Zone Power Distribution",
                    hover_data=['Seer']
                )
                st.plotly_chart(fig)
    
    def run(self):
        """Run the ScrollMap interface"""
        st.set_page_config(
            page_title="ScrollMap",
            page_icon="🗺️",
            layout="wide"
        )
        
        st.title("🗺️ ScrollMap")
        st.markdown("**Global ScrollNations and ScrollEmbassies**")
        
        # Sidebar navigation
        st.sidebar.title("🗺️ Navigation")
        page = st.sidebar.selectbox(
            "Choose a view:",
            ["🗺️ Interactive Map", "📊 Statistics", "👷 Builder Directory", "👁️ Seer Zones"]
        )
        
        if page == "🗺️ Interactive Map":
            st.header("🗺️ Interactive ScrollMap")
            st.write("Explore ScrollNations, ScrollEmbassies, and their builders across the globe.")
            
            # Create and display map
            map_obj = self.create_interactive_map()
            folium_static(map_obj, width=1200, height=600)
            
            # Map legend
            st.markdown("""
            ### Legend
            - 🏛️ **Red Flag**: Justice Embassy
            - 🏛️ **Blue Flag**: Prophecy Embassy  
            - 🏛️ **Green Flag**: Governance Embassy
            - 🏙️ **Red Building**: Justice City
            - 🏙️ **Blue Building**: Prophecy City
            - 🏙️ **Green Building**: Governance City
            """)
        
        elif page == "📊 Statistics":
            self.create_statistics_dashboard()
        
        elif page == "👷 Builder Directory":
            self.create_builder_directory()
        
        elif page == "👁️ Seer Zones":
            self.create_seer_zone_overlay()
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        ### Map Data
        - **Total Embassies**: 6
        - **Total Cities**: 24
        - **Total Builders**: 24
        - **Total Seers**: 6
        
        ### Flame Zones
        - **Justice**: 10 locations
        - **Prophecy**: 8 locations
        - **Governance**: 6 locations
        """)

# Run the map
if __name__ == "__main__":
    scroll_map = ScrollMap()
    scroll_map.run() 