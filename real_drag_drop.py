"""
Simple Salesforce Layout Editor with Drag-Like Interface
=======================================================
Simplified drag-like interface with click-to-select and swap functionality.
- Click on field handles to select/swap
- Hide/show toggles next to each field  
- Original field positions preserved
- Hidden fields panel
- Always in "drag mode"

Author: Assistant for Vibe Coder
"""

import streamlit as st
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Page configuration
st.set_page_config(
    page_title="Salesforce Layout Editor", 
    page_icon="🎯",
    layout="wide"
)

# Enhanced Salesforce-like styling with drag handles
st.markdown("""
<style>
    .main > div {
        padding-top: 1rem;
    }
    
    .sf-header {
        background-color: #1B96FF;
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .sf-section {
        background-color: #FAFAF9;
        border: 1px solid #D8DDE6;
        border-radius: 0.25rem;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .sf-section-header {
        background-color: #F3F3F3;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #D8DDE6;
        font-weight: 600;
        color: #080707;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .sf-field-grid {
        padding: 1rem;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        background-color: white;
    }
    
    .sf-field {
        border: 1px solid #E5E5E5;
        border-radius: 0.25rem;
        padding: 0.75rem;
        background-color: #FAFAF9;
        transition: all 0.2s;
        position: relative;
        cursor: grab;
    }
    
    .sf-field:hover {
        border-color: #1B96FF;
        box-shadow: 0 2px 4px rgba(27, 150, 255, 0.1);
        transform: translateY(-1px);
    }
    
    .sf-field:active {
        cursor: grabbing;
    }
    
    .sf-field-selected {
        border-color: #1B96FF !important;
        box-shadow: 0 0 10px rgba(27, 150, 255, 0.3) !important;
        background-color: #F0F8FF !important;
        transform: translateY(-2px) !important;
    }
    
    .sf-field-target {
        border-color: #28a745 !important;
        box-shadow: 0 0 8px rgba(40, 167, 69, 0.3) !important;
        background-color: #F8FFF9 !important;
    }
    
    .sf-field-label {
        font-weight: 600;
        color: #3E3E3C;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.025rem;
        margin-bottom: 0.25rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .sf-field-value {
        color: #080707;
        font-size: 0.875rem;
        padding: 0.25rem 0;
        border-bottom: 1px solid #E5E5E5;
    }
    
    .drag-handle {
        color: #1B96FF;
        font-size: 1rem;
        cursor: grab;
        padding: 0.25rem;
        border-radius: 0.25rem;
        transition: all 0.2s;
    }
    
    .drag-handle:hover {
        background-color: rgba(27, 150, 255, 0.1);
        transform: scale(1.1);
    }
    
    .drag-handle:active {
        cursor: grabbing;
    }
    
    .hide-button {
        padding: 0.2rem 0.5rem;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        background-color: #f8f9fa;
        color: #6c757d;
        font-size: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .hide-button:hover {
        background-color: #e9ecef;
        color: #495057;
    }
    
    .hidden-panel {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .instructions {
        background-color: #E3F2FD;
        border-left: 4px solid #1B96FF;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .drag-status {
        background-color: #D1ECF1;
        border: 1px solid #BEE5EB;
        border-radius: 0.25rem;
        padding: 0.75rem;
        margin: 1rem 0;
        text-align: center;
        color: #0C5460;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class LayoutField:
    """A field in the layout"""
    id: str
    label: str
    value: str = "--"
    field_type: str = "text"
    visible: bool = True
    position: int = 0

@dataclass
class LayoutSection:
    """A section containing fields"""
    name: str
    title: str
    fields: List[LayoutField]
    expanded: bool = True

class SimpleDragEditor:
    """Simple drag-like editor with click-to-swap"""
    
    def __init__(self):
        self.init_session_state()
        self.load_original_layout()
    
    def init_session_state(self):
        """Initialize session state"""
        if 'sections' not in st.session_state:
            st.session_state.sections = []
        
        if 'selected_field' not in st.session_state:
            st.session_state.selected_field = None
            
        if 'show_hidden_panel' not in st.session_state:
            st.session_state.show_hidden_panel = False
    
    def load_original_layout(self):
        """Load exact layout from screenshot"""
        if not st.session_state.sections:
            # Account Information - exact grid positions
            account_fields = [
                # Row 1
                LayoutField("account_name", "Account Name", "Steed Standard Transport Ltd.", "text", True, 0),
                LayoutField("customer_id_us", "Customer Id TMW US", "", "text", True, 1),
                
                # Row 2
                LayoutField("enterprise_account", "Enterprise Account Number", "16484517", "text", True, 2),
                LayoutField("customer_id_cad", "Customer Id TMW CAD", "Steed Standard Transport - TMWCAN", "text", True, 3),
                
                # Row 3
                LayoutField("division", "Division", "PeopleNet/TMW CAD", "text", True, 4),
                LayoutField("customer_id_aud", "Customer Id TMW AUD", "", "text", True, 5),
                
                # Row 4
                LayoutField("type", "Type", "Customer", "picklist", True, 6),
                LayoutField("parent_child", "Parent or Child Account", "Parent", "picklist", True, 7),
                
                # Row 5
                LayoutField("account_status", "Account Status TMW", "CUSTOMER-(C) Live Customer", "picklist", True, 8),
                LayoutField("timezone", "Account Time Zone (US & CA)", "Eastern Standard Time", "picklist", True, 9),
                
                # Row 6
                LayoutField("tags", "Tags", "", "text", True, 10),
                LayoutField("phone", "Phone TMW", "(519) 271-9924 x230", "phone", True, 11),
                
                # Row 7
                LayoutField("lead_source", "Lead Source", "", "text", True, 12),
                LayoutField("fax", "Fax TMW", "", "phone", True, 13),
                
                # Row 8
                LayoutField("trimble_customer", "Trimble TMS Customer", "☐", "checkbox", True, 14),
                LayoutField("website", "Website", "http://www.ssl.ca/", "url", True, 15),
                
                # Row 9
                LayoutField("global_id", "Global ID", "G1005495", "text", True, 16),
                LayoutField("lead_source_detail", "Lead Source Detail", "", "text", True, 17),
                
                # Row 10
                LayoutField("customer_profile", "Customer Profile", "", "text", True, 18),
                LayoutField("support_maintenance", "Support & Maintenance", "18%", "percentage", True, 19),
                
                # Row 11
                LayoutField("account_stage_us", "Account Stage TMW US", "", "text", True, 20),
                LayoutField("drive_link", "Customer Drive Link", "", "url", True, 21),
                
                # Row 12
                LayoutField("account_stage_aud", "Account Stage TMW AUD", "", "text", True, 22),
                LayoutField("account_stage_cad", "Account Stage TMW CAD", "Customer", "picklist", True, 23),
            ]
            
            # Parent Hierarchy
            parent_fields = [
                LayoutField("parent_us", "Parent Account TMW US", "", "text", True, 0),
                LayoutField("parent_cad", "Parent Account TMW CAD", "", "text", True, 1),
                LayoutField("parent_account", "Parent Account", "", "text", True, 2),
                LayoutField("parent_netsuite", "Parent NetSuite Id", "", "text", True, 3),
            ]
            
            # Customer Success
            success_fields = [
                LayoutField("sentiment", "Customer Sentiment", "Average", "picklist", True, 0),
                LayoutField("risk_update", "At Risk Update", "", "text", True, 1),
                LayoutField("risk_status", "Enterprise Risk Status", "", "text", True, 2),
                LayoutField("totango_health", "Totango Customer Health", "Poor", "picklist", True, 3),
                LayoutField("risk_reason", "Enterprise Risk Reason", "", "text", True, 4),
                LayoutField("empty1", "", "", "text", False, 5),
                LayoutField("risk_severity", "Enterprise At-Risk Severity Level", "", "text", True, 6),
                LayoutField("empty2", "", "", "text", False, 7),
                LayoutField("product_risk", "Enterprise Product At Risk", "", "text", True, 8),
                LayoutField("empty3", "", "", "text", False, 9),
                LayoutField("segmentation", "Segmentation Tier", "Tier 5 CS Engage", "picklist", True, 10),
                LayoutField("empty4", "", "", "text", False, 11),
            ]
            
            st.session_state.sections = [
                LayoutSection("account_info", "Account Information", account_fields, True),
                LayoutSection("parent_hierarchy", "Parent Hierarchy", parent_fields, True),
                LayoutSection("customer_success", "Customer Success", success_fields, True)
            ]
    
    def swap_fields(self, section_name: str, field1_id: str, field2_id: str):
        """Swap two fields"""
        for section in st.session_state.sections:
            if section.name == section_name:
                field1 = next(f for f in section.fields if f.id == field1_id)
                field2 = next(f for f in section.fields if f.id == field2_id)
                field1.position, field2.position = field2.position, field1.position
                section.fields.sort(key=lambda x: x.position)
                break
    
    def render_instructions(self):
        """Render instructions"""
        st.markdown("""
        <div class="instructions">
            <h4>🎯 Drag-Like Layout Editor</h4>
            <p><strong>🔄 Rearrange:</strong> Click the ⋮⋮ drag handle on any field to select it, then click another field's handle to swap positions</p>
            <p><strong>👁️‍🗨️ Hide/Show:</strong> Click the hide button next to any field • Use "Show Hidden" to restore</p>
            <p><strong>📂 Sections:</strong> Click section headers to expand/collapse</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_drag_status(self):
        """Show drag status"""
        if st.session_state.selected_field:
            section_name, field_label, _ = st.session_state.selected_field
            st.markdown(f"""
            <div class="drag-status">
                🔄 <strong>"{field_label}"</strong> selected • Click another field's ⋮⋮ handle to swap positions • 
                <a href="#" onclick="window.location.reload()">Cancel</a>
            </div>
            """, unsafe_allow_html=True)
    
    def render_controls(self):
        """Render main controls"""
        col1, col2 = st.columns([3, 3])
        
        with col1:
            hidden_count = sum(len([f for f in s.fields if not f.visible and f.label]) for s in st.session_state.sections)
            if hidden_count > 0:
                panel_text = f"🙈 Hide Panel ({hidden_count})" if st.session_state.show_hidden_panel else f"👁️‍🗨️ Show Hidden ({hidden_count})"
                if st.button(panel_text):
                    st.session_state.show_hidden_panel = not st.session_state.show_hidden_panel
                    st.rerun()
        
        with col2:
            if st.button("🔄 Reset Layout"):
                st.session_state.sections = []
                st.session_state.selected_field = None
                self.load_original_layout()
                st.rerun()
    
    def render_hidden_panel(self):
        """Render hidden fields panel"""
        if st.session_state.show_hidden_panel:
            all_hidden = []
            for section in st.session_state.sections:
                for field in section.fields:
                    if not field.visible and field.label:
                        all_hidden.append((section.name, section.title, field))
            
            if all_hidden:
                st.markdown(f"""
                <div class="hidden-panel">
                    <h4>👁️‍🗨️ Hidden Fields ({len(all_hidden)} hidden)</h4>
                    <p>Click any field to make it visible again:</p>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns(4)
                for i, (section_name, section_title, field) in enumerate(all_hidden):
                    with cols[i % 4]:
                        if st.button(f"👁️ {field.label}", key=f"unhide_{section_name}_{field.id}"):
                            field.visible = True
                            st.rerun()
    
    def render_main_layout(self):
        """Render main layout"""
        st.markdown("""
        <div class="sf-header">
            <h1>🎯 Salesforce Layout Editor - Account Page</h1>
            <p>Click ⋮⋮ handles to select and swap field positions • Click 👁️‍🗨️ to hide fields</p>
        </div>
        """, unsafe_allow_html=True)
        
        self.render_drag_status()
        
        for section in st.session_state.sections:
            self.render_section(section)
    
    def render_section(self, section: LayoutSection):
        """Render a section with fields"""
        visible_count = len([f for f in section.fields if f.visible and f.label])
        hidden_count = len([f for f in section.fields if not f.visible and f.label])
        
        # Section header
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"""
            <div class="sf-section">
                <div class="sf-section-header">
                    <span>{'📂' if section.expanded else '📁'} {section.title}</span>
                    <span style="font-size: 0.8em; color: #666;">
                        {visible_count} visible{f' • {hidden_count} hidden' if hidden_count > 0 else ''}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("👁️" if section.expanded else "👁️‍🗨️", key=f"toggle_{section.name}"):
                section.expanded = not section.expanded
                st.rerun()
        
        if section.expanded:
            sorted_fields = sorted(section.fields, key=lambda x: x.position)
            visible_fields = [f for f in sorted_fields if f.visible and f.label]
            
            if visible_fields:
                st.markdown('<div class="sf-field-grid">', unsafe_allow_html=True)
                
                cols = st.columns(2)
                for i, field in enumerate(visible_fields):
                    col_idx = i % 2
                    with cols[col_idx]:
                        self.render_field(field, section)
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="padding: 2rem; text-align: center; color: #666;">
                    <p>All fields in this section are hidden</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_field(self, field: LayoutField, section: LayoutSection):
        """Render a single field with drag handle and hide button"""
        # Format value
        display_value = field.value if field.value else "--"
        if field.field_type == "url" and field.value:
            display_value = f'<a href="{field.value}" target="_blank">{field.value}</a>'
        elif field.field_type == "phone" and field.value:
            display_value = f'<a href="tel:{field.value}">{field.value}</a>'
        
        # Determine field styling
        field_class = "sf-field"
        is_selected = (st.session_state.selected_field and 
                      st.session_state.selected_field[0] == section.name and 
                      st.session_state.selected_field[2] == field.id)
        
        if is_selected:
            field_class += " sf-field-selected"
        
        # Create columns for field and hide button
        col_field, col_hide = st.columns([5, 1])
        
        with col_field:
            # Drag handle button
            drag_key = f"drag_{section.name}_{field.id}"
            if st.button("⋮⋮", key=drag_key, help=f"Click to select {field.label} for swapping"):
                if (st.session_state.selected_field and 
                    st.session_state.selected_field[0] == section.name and
                    st.session_state.selected_field[2] != field.id):
                    # Swap with selected field
                    self.swap_fields(section.name, st.session_state.selected_field[2], field.id)
                    st.session_state.selected_field = None
                    st.success(f"Swapped fields!")
                    st.rerun()
                else:
                    # Select this field
                    st.session_state.selected_field = (section.name, field.label, field.id)
                    st.rerun()
            
            # Field display
            st.markdown(f"""
            <div class="{field_class}">
                <div class="sf-field-label">{field.label}</div>
                <div class="sf-field-value">{display_value}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_hide:
            if st.button("👁️‍🗨️", key=f"hide_{section.name}_{field.id}", help=f"Hide {field.label}"):
                field.visible = False
                # Clear selection if hiding selected field
                if (st.session_state.selected_field and 
                    st.session_state.selected_field[2] == field.id):
                    st.session_state.selected_field = None
                st.rerun()
    
    def render_export_tools(self):
        """Render export tools"""
        st.markdown("### 🛠️ Export & Save")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 Export Layout"):
                layout_data = [asdict(section) for section in st.session_state.sections]
                layout_json = json.dumps(layout_data, indent=2)
                st.download_button(
                    "📋 Download JSON",
                    layout_json,
                    "salesforce_layout.json",
                    "application/json"
                )
        
        with col2:
            if st.button("💾 Save Layout"):
                st.success("Layout saved! (Demo)")
    
    def run(self):
        """Main app runner"""
        self.render_instructions()
        self.render_controls()
        self.render_hidden_panel()
        self.render_main_layout()
        st.markdown("---")
        self.render_export_tools()

# Run the application
if __name__ == "__main__":
    app = SimpleDragEditor()
    app.run()
