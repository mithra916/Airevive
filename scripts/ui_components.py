import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import streamlit as st

class UIComponents:
    """UI components for Streamlit dashboard"""
    
    def __init__(self):
        self.color_scheme = {
            'co2': '#FF6B6B',
            'no2': '#4ECDC4', 
            'so2': '#45B7D1',
            'background': '#F8F9FA',
            'danger': '#FF4757',
            'warning': '#FFA502',
            'safe': '#2ED573'
        }
    
    def create_pollution_chart(self, historical_data: pd.DataFrame) -> go.Figure:
        """Create real-time pollution levels chart"""
        fig = go.Figure()
        
        if not historical_data.empty:
            # Ensure timestamp is datetime
            if not pd.api.types.is_datetime64_any_dtype(historical_data['timestamp']):
                historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
            
            # Add traces for each gas
            fig.add_trace(go.Scatter(
                x=historical_data['timestamp'],
                y=historical_data['co2'],
                mode='lines+markers',
                name='CO₂ (ppm)',
                line=dict(color=self.color_scheme['co2'], width=2),
                marker=dict(size=4),
                hovertemplate='<b>CO₂</b><br>%{y:.1f} ppm<br>%{x}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=historical_data['timestamp'],
                y=historical_data['no2'],
                mode='lines+markers',
                name='NO₂ (µg/m³)',
                line=dict(color=self.color_scheme['no2'], width=2),
                marker=dict(size=4),
                yaxis='y2',
                hovertemplate='<b>NO₂</b><br>%{y:.1f} µg/m³<br>%{x}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=historical_data['timestamp'],
                y=historical_data['so2'],
                mode='lines+markers',
                name='SO₂ (µg/m³)',
                line=dict(color=self.color_scheme['so2'], width=2),
                marker=dict(size=4),
                yaxis='y3',
                hovertemplate='<b>SO₂</b><br>%{y:.1f} µg/m³<br>%{x}<extra></extra>'
            ))
        
        # Add threshold lines
        fig.add_hline(y=1000, line_dash="dash", line_color=self.color_scheme['danger'], 
                     annotation_text="CO₂ Danger (1000 ppm)", annotation_position="top right")
        fig.add_hline(y=800, line_dash="dot", line_color=self.color_scheme['warning'], 
                     annotation_text="CO₂ Warning (800 ppm)", annotation_position="top right")
        
        # Update layout
        fig.update_layout(
            title='Real-time Pollution Levels',
            xaxis_title='Time',
            yaxis=dict(
                title='CO₂ (ppm)',
                titlefont=dict(color=self.color_scheme['co2']),
                tickfont=dict(color=self.color_scheme['co2']),
                side='left'
            ),
            yaxis2=dict(
                title='NO₂ (µg/m³)',
                titlefont=dict(color=self.color_scheme['no2']),
                tickfont=dict(color=self.color_scheme['no2']),
                anchor='free',
                overlaying='y',
                side='right',
                position=0.85
            ),
            yaxis3=dict(
                title='SO₂ (µg/m³)',
                titlefont=dict(color=self.color_scheme['so2']),
                tickfont=dict(color=self.color_scheme['so2']),
                anchor='free',
                overlaying='y',
                side='right',
                position=1.0
            ),
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_satellite_comparison(self) -> go.Figure:
        """Create satellite vs factory emission comparison"""
        # Simulate satellite data
        categories = ['CO₂', 'NO₂', 'SO₂']
        factory_levels = [650, 85, 45]  # Current factory levels
        regional_avg = [420, 35, 15]   # Regional averages from satellite
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Factory Emissions',
            x=categories,
            y=factory_levels,
            marker_color=self.color_scheme['danger'],
            text=[f'{val}' for val in factory_levels],
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            name='Regional Average (Satellite)',
            x=categories,
            y=regional_avg,
            marker_color=self.color_scheme['safe'],
            text=[f'{val}' for val in regional_avg],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='Factory vs Regional Emissions Comparison',
            xaxis_title='Pollutant',
            yaxis_title='Concentration',
            barmode='group',
            template='plotly_white',
            height=400,
            annotations=[
                dict(
                    text="Data from satellite monitoring",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.5, y=-0.15, xanchor='center', yanchor='top',
                    font=dict(size=10, color="gray")
                )
            ]
        )
        
        return fig
    
    def create_health_risk_chart(self, health_timeline: pd.DataFrame) -> go.Figure:
        """Create health risk assessment timeline"""
        fig = go.Figure()
        
        if not health_timeline.empty:
            # Ensure timestamp is datetime
            if not pd.api.types.is_datetime64_any_dtype(health_timeline['timestamp']):
                health_timeline['timestamp'] = pd.to_datetime(health_timeline['timestamp'])
            
            # Overall risk
            fig.add_trace(go.Scatter(
                x=health_timeline['timestamp'],
                y=health_timeline['overall_risk'],
                mode='lines+markers',
                name='Overall Risk',
                line=dict(color='#2C3E50', width=3),
                fill='tonexty',
                fillcolor='rgba(44, 62, 80, 0.1)',
                hovertemplate='<b>Overall Risk</b><br>%{y:.1f}%<br>%{x}<extra></extra>'
            ))
            
            # Individual gas risks
            fig.add_trace(go.Scatter(
                x=health_timeline['timestamp'],
                y=health_timeline['co2_risk'],
                mode='lines',
                name='CO₂ Risk',
                line=dict(color=self.color_scheme['co2'], width=1, dash='dot'),
                hovertemplate='<b>CO₂ Risk</b><br>%{y:.1f}%<br>%{x}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=health_timeline['timestamp'],
                y=health_timeline['no2_risk'],
                mode='lines',
                name='NO₂ Risk',
                line=dict(color=self.color_scheme['no2'], width=1, dash='dot'),
                hovertemplate='<b>NO₂ Risk</b><br>%{y:.1f}%<br>%{x}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=health_timeline['timestamp'],
                y=health_timeline['so2_risk'],
                mode='lines',
                name='SO₂ Risk',
                line=dict(color=self.color_scheme['so2'], width=1, dash='dot'),
                hovertemplate='<b>SO₂ Risk</b><br>%{y:.1f}%<br>%{x}<extra></extra>'
            ))
        
        # Add risk level zones
        fig.add_hrect(y0=0, y1=25, fillcolor=self.color_scheme['safe'], opacity=0.1, 
                     annotation_text="Low Risk", annotation_position="top left")
        fig.add_hrect(y0=25, y1=50, fillcolor=self.color_scheme['warning'], opacity=0.1,
                     annotation_text="Moderate Risk", annotation_position="top left")
        fig.add_hrect(y0=50, y1=75, fillcolor=self.color_scheme['danger'], opacity=0.1,
                     annotation_text="High Risk", annotation_position="top left")
        fig.add_hrect(y0=75, y1=100, fillcolor='#8B0000', opacity=0.1,
                     annotation_text="Critical Risk", annotation_position="top left")
        
        fig.update_layout(
            title='Health Risk Assessment Timeline',
            xaxis_title='Time',
            yaxis_title='Risk Level (%)',
            yaxis=dict(range=[0, 100]),
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_gauge_chart(self, value: float, title: str, max_value: float = 100) -> go.Figure:
        """Create gauge chart for metrics"""
        # Determine color based on value
        if value < 30:
            color = self.color_scheme['safe']
        elif value < 70:
            color = self.color_scheme['warning']
        else:
            color = self.color_scheme['danger']
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': title},
            delta = {'reference': max_value * 0.5},
            gauge = {
                'axis': {'range': [None, max_value]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, max_value * 0.3], 'color': "lightgray"},
                    {'range': [max_value * 0.3, max_value * 0.7], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(height=300, template='plotly_white')
        return fig
    
    def create_alert_timeline(self, alerts: List[Dict]) -> go.Figure:
        """Create timeline of alerts"""
        if not alerts:
            # Empty chart
            fig = go.Figure()
            fig.add_annotation(
                text="No alerts to display",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title='Alert Timeline',
                template='plotly_white',
                height=300
            )
            return fig
        
        # Convert alerts to DataFrame
        alert_df = pd.DataFrame(alerts)
        alert_df['timestamp'] = pd.to_datetime(alert_df['timestamp'])
        
        # Create scatter plot
        fig = go.Figure()
        
        # Color mapping for severity
        severity_colors = {
            'critical': self.color_scheme['danger'],
            'warning': self.color_scheme['warning'],
            'info': self.color_scheme['safe']
        }
        
        for severity in alert_df['severity'].unique():
            severity_data = alert_df[alert_df['severity'] == severity]
            
            fig.add_trace(go.Scatter(
                x=severity_data['timestamp'],
                y=severity_data['gas'],
                mode='markers',
                name=severity.title(),
                marker=dict(
                    color=severity_colors.get(severity, 'blue'),
                    size=12,
                    symbol='diamond' if severity == 'critical' else 'circle'
                ),
                text=severity_data['message'],
                hovertemplate='<b>%{y}</b><br>%{text}<br>%{x}<extra></extra>'
            ))
        
        fig.update_layout(
            title='Alert Timeline',
            xaxis_title='Time',
            yaxis_title='Gas Type',
            template='plotly_white',
            height=300,
            hovermode='closest'
        )
        
        return fig
    
    def create_compliance_dashboard(self, compliance_data: Dict) -> go.Figure:
        """Create compliance status dashboard"""
        # Create subplots for different compliance metrics
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Overall Score', 'CO₂ Compliance', 'NO₂ Compliance', 'SO₂ Compliance'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}],
                   [{"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Overall compliance score
        overall_score = compliance_data.get('overall_score', 0)
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            title={'text': "Overall"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': self._get_compliance_color(overall_score)},
                   'steps': [{'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 100], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 90}}
        ), row=1, col=1)
        
        # Individual gas compliance
        gases = ['co2', 'no2', 'so2']
        positions = [(1, 2), (2, 1), (2, 2)]
        
        for gas, (row, col) in zip(gases, positions):
            score = compliance_data.get(f'{gas}_score', 0)
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=score,
                title={'text': gas.upper()},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': self._get_compliance_color(score)}}
            ), row=row, col=col)
        
        fig.update_layout(height=500, template='plotly_white')
        return fig
    
    def _get_compliance_color(self, score: float) -> str:
        """Get color based on compliance score"""
        if score >= 90:
            return self.color_scheme['safe']
        elif score >= 70:
            return self.color_scheme['warning']
        else:
            return self.color_scheme['danger']
    
    def create_trend_analysis(self, historical_data: pd.DataFrame, days: int = 7) -> go.Figure:
        """Create trend analysis chart"""
        if historical_data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for trend analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle'
            )
            return fig
        
        # Resample data to daily averages
        historical_data['timestamp'] = pd.to_datetime(historical_data['timestamp'])
        daily_data = historical_data.set_index('timestamp').resample('D').mean()
        
        fig = go.Figure()
        
        # Add trend lines for each gas
        for gas, color in [('co2', self.color_scheme['co2']), 
                          ('no2', self.color_scheme['no2']), 
                          ('so2', self.color_scheme['so2'])]:
            if gas in daily_data.columns:
                # Calculate trend line
                x_numeric = np.arange(len(daily_data))
                z = np.polyfit(x_numeric, daily_data[gas].fillna(0), 1)
                trend_line = np.poly1d(z)(x_numeric)
                
                # Add actual data
                fig.add_trace(go.Scatter(
                    x=daily_data.index,
                    y=daily_data[gas],
                    mode='markers+lines',
                    name=f'{gas.upper()} Actual',
                    line=dict(color=color, width=2),
                    marker=dict(size=6)
                ))
                
                # Add trend line
                fig.add_trace(go.Scatter(
                    x=daily_data.index,
                    y=trend_line,
                    mode='lines',
                    name=f'{gas.upper()} Trend',
                    line=dict(color=color, width=3, dash='dash'),
                    opacity=0.7
                ))
        
        fig.update_layout(
            title=f'Pollution Trends - Last {days} Days',
            xaxis_title='Date',
            yaxis_title='Concentration',
            template='plotly_white',
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def display_alert_card(self, alert: Dict):
        """Display alert as a card component"""
        severity_colors = {
            'critical': '🔴',
            'warning': '🟡',
            'info': '🟢'
        }
        
        severity_icon = severity_colors.get(alert.get('severity', 'info'), '🔵')
        
        with st.container():
            st.markdown(f"""
            <div style="
                border-left: 4px solid {'#FF4757' if alert.get('severity') == 'critical' else '#FFA502'};
                padding: 1rem;
                margin: 0.5rem 0;
                background-color: {'#FFE5E5' if alert.get('severity') == 'critical' else '#FFF5E5'};
                border-radius: 0.25rem;
            ">
                <h4>{severity_icon} {alert.get('gas', 'Unknown').upper()} Alert</h4>
                <p><strong>Level:</strong> {alert.get('level', 0):.1f}</p>
                <p><strong>Duration:</strong> {alert.get('duration_minutes', 0):.1f} minutes</p>
                <p><strong>Message:</strong> {alert.get('message', 'No message')}</p>
            </div>
            """, unsafe_allow_html=True)
