import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import os
from typing import Dict, List, Any
import asyncio
import threading

# Import our custom modules
from data_simulator import PollutionDataSimulator
from ai_estimator import AIHealthEstimator, AISuggestionEngine
from report_generator import ReportGenerator
from offline_sync import OfflineSync
from ui_components import UIComponents

# Configure Streamlit page
st.set_page_config(
    page_title="ToxicGas AI Monitor",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

class ToxicGasMonitor:
    def __init__(self):
        self.data_simulator = PollutionDataSimulator()
        self.health_estimator = AIHealthEstimator()
        self.suggestion_engine = AISuggestionEngine()
        self.report_generator = ReportGenerator()
        self.offline_sync = OfflineSync()
        self.ui_components = UIComponents()
        
        # Initialize session state
        if 'monitoring_active' not in st.session_state:
            st.session_state.monitoring_active = False
        if 'alert_history' not in st.session_state:
            st.session_state.alert_history = []
        if 'suggestion_feedback' not in st.session_state:
            st.session_state.suggestion_feedback = {}
        if 'factory_type' not in st.session_state:
            st.session_state.factory_type = "Coal Power Plant"
    
    def run(self):
        """Main application runner"""
        st.title("🏭 ToxicGas AI Monitor")
        st.markdown("Real-time Industrial Pollution Monitoring & AI-Powered Recommendations")
        
        # Sidebar configuration
        self.render_sidebar()
        
        # Main dashboard
        if st.session_state.monitoring_active:
            self.render_main_dashboard()
        else:
            self.render_welcome_screen()
    
    def render_sidebar(self):
        """Render sidebar controls"""
        with st.sidebar:
            st.header("⚙️ Control Panel")
            
            # Factory configuration
            st.subheader("Factory Settings")
            factory_types = ["Coal Power Plant", "Textile Factory", "Chemical Plant", "Steel Mill", "Cement Factory"]
            st.session_state.factory_type = st.selectbox("Factory Type", factory_types)
            
            # Monitoring controls
            st.subheader("Monitoring Controls")
            if st.button("🟢 Start Monitoring" if not st.session_state.monitoring_active else "🔴 Stop Monitoring"):
                st.session_state.monitoring_active = not st.session_state.monitoring_active
                if st.session_state.monitoring_active:
                    st.success("Monitoring started!")
                else:
                    st.info("Monitoring stopped!")
                st.rerun()
            
            # Alert settings
            st.subheader("Alert Settings")
            alert_threshold = st.slider("Alert Persistence (minutes)", 5, 30, 10)
            
            # Offline sync status
            st.subheader("Sync Status")
            sync_status = self.offline_sync.get_sync_status()
            if sync_status['online']:
                st.success("🟢 Online - Data syncing")
            else:
                st.warning(f"🟡 Offline - {sync_status['pending_records']} records pending")
                if st.button("Force Sync"):
                    self.offline_sync.force_sync()
    
    def render_welcome_screen(self):
        """Render welcome screen when monitoring is inactive"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            ## Welcome to ToxicGas AI Monitor
            
            ### Features:
            - 📊 Real-time pollution monitoring (CO₂, NO₂, SO₂)
            - 🧠 AI-powered health risk assessment
            - 🛰️ Satellite data comparison
            - 💡 Smart pollution reduction suggestions
            - 📧 Automated daily reports
            - 🔄 Offline capability with sync
            - 🚨 Intelligent alert system
            
            **Click 'Start Monitoring' in the sidebar to begin!**
            """)
    
    def render_main_dashboard(self):
        """Render main monitoring dashboard"""
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Live Dashboard", 
            "🚨 Alerts", 
            "💡 AI Suggestions", 
            "📈 Audit Tracker", 
            "📧 Reports"
        ])
        
        with tab1:
            self.render_live_dashboard()
        
        with tab2:
            self.render_alerts_panel()
        
        with tab3:
            self.render_ai_suggestions()
        
        with tab4:
            self.render_audit_tracker()
        
        with tab5:
            self.render_reports_panel()
    
    def render_live_dashboard(self):
        """Render live pollution monitoring dashboard"""
        # Get current data
        current_data = self.data_simulator.get_current_readings()
        
        # Display current readings
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "CO₂ Level", 
                f"{current_data['co2']:.1f} ppm",
                delta=f"{current_data['co2'] - 400:.1f}"
            )
        
        with col2:
            st.metric(
                "NO₂ Level", 
                f"{current_data['no2']:.1f} µg/m³",
                delta=f"{current_data['no2'] - 40:.1f}"
            )
        
        with col3:
            st.metric(
                "SO₂ Level", 
                f"{current_data['so2']:.1f} µg/m³",
                delta=f"{current_data['so2'] - 20:.1f}"
            )
        
        with col4:
            health_risk = self.health_estimator.calculate_overall_risk(current_data)
            risk_color = "🟢" if health_risk < 30 else "🟡" if health_risk < 70 else "🔴"
            st.metric(
                "Health Risk", 
                f"{risk_color} {health_risk:.1f}%"
            )
        
        # Historical charts
        st.subheader("📈 Real-time Trends")
        historical_data = self.data_simulator.get_historical_data(hours=24)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pollution levels chart
            fig = self.ui_components.create_pollution_chart(historical_data)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Satellite comparison
            satellite_fig = self.ui_components.create_satellite_comparison()
            st.plotly_chart(satellite_fig, use_container_width=True)
        
        # Health risk timeline
        st.subheader("🏥 Health Risk Assessment")
        health_timeline = self.health_estimator.get_risk_timeline(historical_data)
        health_fig = self.ui_components.create_health_risk_chart(health_timeline)
        st.plotly_chart(health_fig, use_container_width=True)
    
    def render_alerts_panel(self):
        """Render alerts and notifications panel"""
        st.subheader("🚨 Active Alerts")
        
        # Check for current alerts
        current_data = self.data_simulator.get_current_readings()
        active_alerts = self.health_estimator.check_alerts(current_data)
        
        if active_alerts:
            for alert in active_alerts:
                alert_type = "error" if alert['severity'] == 'critical' else "warning"
                st.alert(f"**{alert['gas'].upper()}**: {alert['message']}", icon="🚨")
        else:
            st.success("No active alerts")
        
        # Alert history
        st.subheader("📋 Alert History")
        if st.session_state.alert_history:
            alert_df = pd.DataFrame(st.session_state.alert_history)
            st.dataframe(alert_df, use_container_width=True)
        else:
            st.info("No alerts in history")
        
        # Auto-justification report
        if active_alerts:
            st.subheader("📄 Auto-Justification Report")
            if st.button("Generate Shutdown Recommendation"):
                report = self.report_generator.generate_shutdown_report(current_data, active_alerts)
                st.markdown(report)
                
                # Download button
                st.download_button(
                    "Download Report",
                    report,
                    file_name=f"shutdown_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
    
    def render_ai_suggestions(self):
        """Render AI-powered suggestions panel"""
        st.subheader("💡 AI-Powered Pollution Reduction Suggestions")
        
        current_data = self.data_simulator.get_current_readings()
        suggestions = self.suggestion_engine.get_suggestions(
            current_data, 
            st.session_state.factory_type
        )
        
        for i, suggestion in enumerate(suggestions):
            with st.expander(f"💡 {suggestion['title']} (Priority: {suggestion['priority']})"):
                st.markdown(suggestion['description'])
                st.markdown(f"**Expected Impact:** {suggestion['expected_impact']}")
                st.markdown(f"**Implementation Time:** {suggestion['implementation_time']}")
                
                # Feedback buttons
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"👍 Helpful", key=f"helpful_{i}"):
                        self.suggestion_engine.record_feedback(suggestion['id'], 'helpful')
                        st.success("Feedback recorded!")
                
                with col2:
                    if st.button(f"👎 Not Helpful", key=f"not_helpful_{i}"):
                        self.suggestion_engine.record_feedback(suggestion['id'], 'not_helpful')
                        st.success("Feedback recorded!")
                
                with col3:
                    if st.button(f"✅ Implemented", key=f"implemented_{i}"):
                        self.suggestion_engine.record_feedback(suggestion['id'], 'implemented')
                        st.success("Implementation recorded!")
        
        # Learning insights
        st.subheader("🧠 AI Learning Insights")
        learning_stats = self.suggestion_engine.get_learning_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Suggestions Given", learning_stats['total_suggestions'])
        with col2:
            st.metric("Implementation Rate", f"{learning_stats['implementation_rate']:.1f}%")
        with col3:
            st.metric("Avg Effectiveness", f"{learning_stats['avg_effectiveness']:.1f}/5")
    
    def render_audit_tracker(self):
        """Render audit tracking panel"""
        st.subheader("📈 Environmental Audit Tracker")
        
        # Generate audit score
        current_data = self.data_simulator.get_current_readings()
        audit_score = self.health_estimator.calculate_audit_score(current_data)
        
        # Display audit score
        col1, col2, col3 = st.columns(3)
        with col1:
            score_color = "🟢" if audit_score >= 80 else "🟡" if audit_score >= 60 else "🔴"
            st.metric("Current Audit Score", f"{score_color} {audit_score}/100")
        
        with col2:
            compliance_status = "Compliant" if audit_score >= 70 else "Non-Compliant"
            st.metric("Compliance Status", compliance_status)
        
        with col3:
            historical_data = self.data_simulator.get_historical_data(hours=168)  # 1 week
            avg_score = np.mean([self.health_estimator.calculate_audit_score(row) for _, row in historical_data.iterrows()])
            st.metric("Weekly Average", f"{avg_score:.1f}/100")
        
        # Audit timeline
        st.subheader("📊 Audit Score Timeline")
        audit_timeline = []
        for _, row in historical_data.iterrows():
            audit_timeline.append({
                'timestamp': row['timestamp'],
                'score': self.health_estimator.calculate_audit_score(row)
            })
        
        audit_df = pd.DataFrame(audit_timeline)
        fig = px.line(audit_df, x='timestamp', y='score', title='Audit Score Over Time')
        fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Compliance Threshold")
        st.plotly_chart(fig, use_container_width=True)
        
        # Action log
        st.subheader("📝 Action Log")
        action_log = self.offline_sync.get_action_log()
        if action_log:
            st.dataframe(pd.DataFrame(action_log), use_container_width=True)
        else:
            st.info("No actions logged yet")
    
    def render_reports_panel(self):
        """Render reports generation panel"""
        st.subheader("📧 Automated Reports")
        
        # Daily report preview
        st.subheader("📊 Daily Report Preview")
        current_data = self.data_simulator.get_current_readings()
        historical_data = self.data_simulator.get_historical_data(hours=24)
        
        daily_report = self.report_generator.generate_daily_report(
            current_data, 
            historical_data, 
            st.session_state.alert_history
        )
        
        st.markdown(daily_report)
        
        # Email settings
        st.subheader("✉️ Email Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            email_recipients = st.text_area(
                "Email Recipients (one per line)",
                value="manager@factory.com\nenvironmental@factory.com"
            )
        
        with col2:
            report_frequency = st.selectbox(
                "Report Frequency",
                ["Daily", "Weekly", "Monthly"]
            )
            
            auto_send = st.checkbox("Auto-send reports", value=True)
        
        # Manual report generation
        if st.button("📧 Send Report Now"):
            recipients = [email.strip() for email in email_recipients.split('\n') if email.strip()]
            success = self.report_generator.send_email_report(daily_report, recipients)
            
            if success:
                st.success("Report sent successfully!")
            else:
                st.error("Failed to send report (using placeholder email system)")
        
        # Report history
        st.subheader("📋 Report History")
        report_history = self.report_generator.get_report_history()
        if report_history:
            st.dataframe(pd.DataFrame(report_history), use_container_width=True)
        else:
            st.info("No reports sent yet")

# Auto-refresh functionality
def auto_refresh():
    """Auto-refresh the app every 30 seconds when monitoring is active"""
    if st.session_state.get('monitoring_active', False):
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    # Initialize and run the app
    monitor = ToxicGasMonitor()
    monitor.run()
    
    # Auto-refresh for real-time updates
    if st.session_state.get('monitoring_active', False):
        # Use a placeholder for auto-refresh
        placeholder = st.empty()
        with placeholder.container():
            st.info("🔄 Auto-refreshing every 30 seconds...")
            time.sleep(30)
            st.rerun()
