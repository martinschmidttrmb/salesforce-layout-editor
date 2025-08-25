"""
Real Drag & Drop Salesforce Layout Editor
=========================================
True drag-and-drop with visual feedback:
- Click and hold drag handle (⋮⋮)
- Drag over another field (green highlight)
- Release to swap positions
- Visual drag preview follows cursor
- Hide/show buttons for each field

Author: Assistant for Vibe Coder
"""

import streamlit as st
from streamlit_sortables import sort_items
import json
from typing import Dict, List
from dataclasses import dataclass, asdict

# Page configuration
st.set_page_config(
    page_title="Real Drag & Drop Editor",
    page_icon="🎯",
    layout="wide"
)

# Salesforce styling with enhanced drag effects
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
    
    .instructions {
        background-color: #E3F2FD;
        border-left: 4px solid #1B96FF;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.25rem;
    }
    
    .hidden-panel {
        background-color: #FFF3CD;
        border: 1px solid #FFEAA7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Enhanced sortable styling */
    .sortable-item {
        border: 1px solid #E5E5E5 !important;
        border-radius: 0.25rem !important;
        padding: 0.75rem !important;
        background-color: #FAFAF9 !important;
        margin: 0.5rem 0 !important;
        cursor: grab !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    .sortable-item:hover {
        border-color: #1B96FF !important;
        box-shadow: 0 4px 8px rgba(27, 150, 255, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    .sortable-item:active {
        cursor: grabbing !important;
    }
    
    /* Dragging state */
    .sortable-item.sortable-ghost {
        opacity: 0.4 !important;
        background-color: #E3F2FD !important;
        border: 2px dashed #1B96FF !important;
        transform: rotate(1deg) scale(1.05) !important;
    }
    
    /* Drop target styling */
    .sortable-item.sortable-chosen {
        border-color: #28a745 !important;
        background-color: #F8FFF9 !important;
        box-shadow: 0 0 15px rgba(40, 167, 69, 0.4) !important;
        transform: scale(1.02) !important;
    }
    
    .field-label {
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
    
    .field-value {
        color: #080707;
        font-size: 0.875rem;
        padding: 0.25rem 0;
        border-bottom: 1px solid #E5E5E5;
        word-break: break-word;
    }
    
    .drag-handle {
        color: #1B96FF;
        font-size: 1.1rem;
        margin-right: 0.5rem;
        user-select: none;
    }
    
    .hide-button {
        background: none;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 0.2rem 0.4rem;
        font-size: 0.7rem;
        color: #6c757d;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .hide-button:hover {
        background-color: #e9ecef;
        color: #495057;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class LayoutField:
    """A draggable field"""
    id: str
    label: str
    value: str = "--"
    field_type: str = "text"
    visible: bool = True
    position: int = 0

@dataclass
class LayoutSection:
    """A section with draggable fields"""
    name: str
    title: str
    fields: List[LayoutField]
    expanded: bool = True

class RealDragDropEditor:
    """Real drag and drop editor using sortables"""
    
    def __init__(self):
        self.init_session_state()
        self.load_original_layout()
    
    def init_session_state(self):
        """Initialize session state"""
        if 'sections' not in st.session_state:
            st.session_state.sections = []
        if 'show_hidden_panel' not in st.session_state:
            st.session_state.show_hidden_panel = False
    
    def load_original_layout(self):
        """Load exact layout from screenshot"""
        if not st.session_state.sections:
            # Account Information - exact positions
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

    def create_field_item(self, field: LayoutField, section_name: str) -> str:
        """Create sortable field item with hide button"""
        display_value = field.value if field.value else "--"
        if field.field_type == "url" and field.value:
            display_value = f'<a href="{field.value}" target="_blank">{field.value}</a>'
        elif field.field_type == "phone" and field.value:
            display_value = f'<a href="tel:{field.value}">{field.value}</a>'
        
        return f"""
        <div data-field-id="{field.id}">
            <div class="field-label">
                <span><span class="drag-handle">⋮⋮</span> {field.label}</span>
            </div>
            <div class="field-value">{display_value}</div>
        </div>
        """

    def update_field_order(self, section: LayoutSection, sorted_items: List[str]):
        """Update field order based on drag and drop result"""
        # Extract field IDs from sorted items  
        new_order = []
        for item_html in sorted_items:
            # Parse field ID from HTML
            if 'data-field-id="' in item_html:
                start = item_html.find('data-field-id="') + 15
                end = item_html.find('"', start)
                field_id = item_html[start:end]
                new_order.append(field_id)
        
        # Update positions based on new order
        for i, field_id in enumerate(new_order):
            field = next(f for f in section.fields if f.id == field_id)
            field.position = i
        
        section.fields.sort(key=lambda x: x.position)

    def render_instructions(self):
        """Render instructions"""
        st.markdown("""
        <div class="instructions">
            <h4>🎯 Real Drag & Drop Layout Editor</h4>
            <p><strong>🖱️ Drag & Drop:</strong> Click and hold any field by the ⋮⋮ handle, drag to desired position, release to drop</p>
            <p><strong>👁️‍🗨️ Hide/Show:</strong> Click hide buttons below • Use "Show Hidden" panel to restore</p>
            <p><strong>✨ Visual Feedback:</strong> Dragging fields get ghost effect, drop targets turn green</p>
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
        """Render main layout with drag and drop"""
        st.markdown("""
        <div class="sf-header">
            <h1>🎯 Real Drag & Drop Salesforce Editor</h1>
            <p>Click and hold ⋮⋮ handles • Drag fields to reorder • Visual feedback shows drop zones</p>
        </div>
        """, unsafe_allow_html=True)
        
        for section in st.session_state.sections:
            self.render_section(section)

    def render_section(self, section: LayoutSection):
        """Render section with draggable fields"""
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
            # Get visible fields sorted by position
            sorted_fields = sorted(section.fields, key=lambda x: x.position)
            visible_fields = [f for f in sorted_fields if f.visible and f.label]
            
            if visible_fields:
                # Create items for sortable interface
                sortable_items = [self.create_field_item(field, section.name) for field in visible_fields]
                
                # Render sortable fields
                sorted_items = sort_items(
                    sortable_items,
                    direction="vertical",
                    key=f"sort_{section.name}"
                )
                
                # Update field order if changed
                if sorted_items != sortable_items:
                    self.update_field_order(section, sorted_items)
                    st.rerun()
                
                # Render hide buttons for visible fields
                st.markdown("**Field Controls:**")
                cols = st.columns(min(4, len(visible_fields)))
                for i, field in enumerate(visible_fields):
                    with cols[i % len(cols)]:
                        if st.button(f"👁️‍🗨️ {field.label}", key=f"hide_{section.name}_{field.id}"):
                            field.visible = False
                            st.rerun()
                            
            else:
                st.markdown("""
                <div style="padding: 2rem; text-align: center; color: #666;">
                    <p>All fields in this section are hidden</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

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
                    "salesforce_real_drag_layout.json",
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
    app = RealDragDropEditor()
    app.run()
