import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os
import random

class AIHealthEstimator:
    """AI-powered health risk estimation and alert system"""
    
    def __init__(self):
        # WHO/CPCB health impact factors
        self.health_impact_factors = {
            'co2': {
                'low': 400,      # Normal outdoor levels
                'moderate': 800, # Drowsiness threshold
                'high': 1000,    # Immediate danger
                'critical': 5000 # Life threatening
            },
            'no2': {
                'low': 40,       # WHO annual guideline
                'moderate': 100, # Short-term exposure
                'high': 200,     # WHO 1-hour guideline
                'critical': 400  # Immediate health risk
            },
            'so2': {
                'low': 20,       # WHO 24-hour guideline
                'moderate': 125, # Sensitive groups affected
                'high': 500,     # WHO 10-minute guideline
                'critical': 1000 # Severe health effects
            }
        }
        
        # Health risk weights for different populations
        self.population_weights = {
            'general': 1.0,
            'children': 1.5,
            'elderly': 1.3,
            'respiratory_conditions': 2.0,
            'cardiovascular_conditions': 1.8
        }
        
        self.alert_persistence_threshold = 10  # minutes
        self.active_alerts = {}
        self.alert_history_file = "alert_history.json"
    
    def calculate_individual_gas_risk(self, gas: str, level: float) -> Dict:
        """Calculate health risk for individual gas"""
        thresholds = self.health_impact_factors[gas]
        
        if level <= thresholds['low']:
            risk_level = 'low'
            risk_score = (level / thresholds['low']) * 25
        elif level <= thresholds['moderate']:
            risk_level = 'moderate'
            risk_score = 25 + ((level - thresholds['low']) / (thresholds['moderate'] - thresholds['low'])) * 25
        elif level <= thresholds['high']:
            risk_level = 'high'
            risk_score = 50 + ((level - thresholds['moderate']) / (thresholds['high'] - thresholds['moderate'])) * 30
        else:
            risk_level = 'critical'
            risk_score = 80 + min(((level - thresholds['high']) / (thresholds['critical'] - thresholds['high'])) * 20, 20)
        
        # Health effects description
        health_effects = self._get_health_effects(gas, risk_level)
        
        return {
            'gas': gas,
            'level': level,
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'health_effects': health_effects,
            'recommended_actions': self._get_recommended_actions(gas, risk_level)
        }
    
    def calculate_overall_risk(self, readings: Dict) -> float:
        """Calculate overall health risk from all gas readings"""
        total_risk = 0
        gas_count = 0
        
        for gas in ['co2', 'no2', 'so2']:
            if gas in readings:
                individual_risk = self.calculate_individual_gas_risk(gas, readings[gas])
                total_risk += individual_risk['risk_score']
                gas_count += 1
        
        if gas_count == 0:
            return 0
        
        # Calculate weighted average with emphasis on highest risk
        average_risk = total_risk / gas_count
        
        # Apply population-specific multipliers (using general population as default)
        population_multiplier = self.population_weights['general']
        
        return min(average_risk * population_multiplier, 100)
    
    def _get_health_effects(self, gas: str, risk_level: str) -> List[str]:
        """Get health effects for specific gas and risk level"""
        effects = {
            'co2': {
                'low': ['Normal breathing', 'No immediate effects'],
                'moderate': ['Mild drowsiness', 'Reduced concentration'],
                'high': ['Drowsiness', 'Stuffiness', 'Poor air quality'],
                'critical': ['Immediate danger', 'Loss of consciousness', 'Asphyxiation risk']
            },
            'no2': {
                'low': ['No immediate effects'],
                'moderate': ['Mild respiratory irritation'],
                'high': ['Respiratory irritation', 'Reduced lung function', 'Increased infection risk'],
                'critical': ['Severe respiratory distress', 'Pulmonary edema', 'Death risk']
            },
            'so2': {
                'low': ['No immediate effects'],
                'moderate': ['Throat irritation', 'Coughing'],
                'high': ['Severe respiratory irritation', 'Breathing difficulties', 'Chest tightness'],
                'critical': ['Severe breathing problems', 'Pulmonary edema', 'Cardiovascular stress']
            }
        }
        
        return effects.get(gas, {}).get(risk_level, ['Unknown effects'])
    
    def _get_recommended_actions(self, gas: str, risk_level: str) -> List[str]:
        """Get recommended actions for specific gas and risk level"""
        actions = {
            'co2': {
                'low': ['Continue normal operations', 'Monitor levels'],
                'moderate': ['Increase ventilation', 'Monitor sensitive individuals'],
                'high': ['Improve ventilation immediately', 'Consider reducing occupancy'],
                'critical': ['Evacuate area immediately', 'Emergency ventilation', 'Medical attention']
            },
            'no2': {
                'low': ['Continue monitoring'],
                'moderate': ['Limit outdoor activities for sensitive groups'],
                'high': ['Avoid outdoor activities', 'Use air purifiers', 'Seek medical advice if symptoms'],
                'critical': ['Emergency evacuation', 'Immediate medical attention', 'Shut down emission sources']
            },
            'so2': {
                'low': ['Continue monitoring'],
                'moderate': ['Limit exposure for sensitive individuals'],
                'high': ['Avoid area', 'Use respiratory protection', 'Seek medical attention'],
                'critical': ['Emergency evacuation', 'Emergency medical care', 'Immediate source shutdown']
            }
        }
        
        return actions.get(gas, {}).get(risk_level, ['Consult environmental specialist'])
    
    def check_alerts(self, readings: Dict) -> List[Dict]:
        """Check for alert conditions and manage persistence"""
        current_time = datetime.now()
        alerts = []
        
        for gas in ['co2', 'no2', 'so2']:
            if gas in readings:
                risk_assessment = self.calculate_individual_gas_risk(gas, readings[gas])
                
                if risk_assessment['risk_level'] in ['high', 'critical']:
                    alert_key = f"{gas}_{risk_assessment['risk_level']}"
                    
                    if alert_key not in self.active_alerts:
                        # New alert
                        self.active_alerts[alert_key] = {
                            'start_time': current_time,
                            'gas': gas,
                            'level': readings[gas],
                            'risk_level': risk_assessment['risk_level'],
                            'risk_score': risk_assessment['risk_score']
                        }
                    
                    # Check if alert has persisted long enough
                    alert_duration = (current_time - self.active_alerts[alert_key]['start_time']).total_seconds() / 60
                    
                    if alert_duration >= self.alert_persistence_threshold:
                        alerts.append({
                            'gas': gas,
                            'level': readings[gas],
                            'risk_level': risk_assessment['risk_level'],
                            'risk_score': risk_assessment['risk_score'],
                            'duration_minutes': alert_duration,
                            'severity': 'critical' if risk_assessment['risk_level'] == 'critical' else 'warning',
                            'message': f'{gas.upper()} has been at {risk_assessment["risk_level"]} levels for {alert_duration:.1f} minutes',
                            'health_effects': risk_assessment['health_effects'],
                            'recommended_actions': risk_assessment['recommended_actions']
                        })
                else:
                    # Remove alert if levels have normalized
                    alert_keys_to_remove = [key for key in self.active_alerts.keys() if key.startswith(gas)]
                    for key in alert_keys_to_remove:
                        del self.active_alerts[key]
        
        # Save alerts to history
        if alerts:
            self._save_alerts_to_history(alerts)
        
        return alerts
    
    def _save_alerts_to_history(self, alerts: List[Dict]):
        """Save alerts to historical record"""
        try:
            # Load existing history
            history = []
            if os.path.exists(self.alert_history_file):
                with open(self.alert_history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new alerts
            for alert in alerts:
                alert['timestamp'] = datetime.now().isoformat()
                history.append(alert)
            
            # Keep only last 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            history = [alert for alert in history if datetime.fromisoformat(alert['timestamp']) > cutoff_date]
            
            # Save updated history
            with open(self.alert_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        
        except Exception as e:
            print(f"Error saving alert history: {e}")
    
    def get_risk_timeline(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """Generate risk timeline from historical data"""
        if historical_data.empty:
            return pd.DataFrame()
        
        risk_timeline = []
        
        for _, row in historical_data.iterrows():
            readings = {
                'co2': row.get('co2', 0),
                'no2': row.get('no2', 0),
                'so2': row.get('so2', 0)
            }
            
            overall_risk = self.calculate_overall_risk(readings)
            
            risk_timeline.append({
                'timestamp': row['timestamp'],
                'overall_risk': overall_risk,
                'co2_risk': self.calculate_individual_gas_risk('co2', readings['co2'])['risk_score'],
                'no2_risk': self.calculate_individual_gas_risk('no2', readings['no2'])['risk_score'],
                'so2_risk': self.calculate_individual_gas_risk('so2', readings['so2'])['risk_score']
            })
        
        return pd.DataFrame(risk_timeline)
    
    def calculate_audit_score(self, readings: Dict) -> float:
        """Calculate environmental audit score (0-100)"""
        # Base score starts at 100
        audit_score = 100
        
        for gas in ['co2', 'no2', 'so2']:
            if gas in readings:
                risk_assessment = self.calculate_individual_gas_risk(gas, readings[gas])
                
                # Deduct points based on risk level
                if risk_assessment['risk_level'] == 'moderate':
                    audit_score -= 10
                elif risk_assessment['risk_level'] == 'high':
                    audit_score -= 25
                elif risk_assessment['risk_level'] == 'critical':
                    audit_score -= 40
        
        return max(0, audit_score)

class AISuggestionEngine:
    """AI-powered suggestion engine for pollution reduction"""
    
    def __init__(self):
        self.suggestions_db = self._initialize_suggestions_db()
        self.feedback_file = "suggestion_feedback.json"
        self.learning_data = self._load_learning_data()
    
    def _initialize_suggestions_db(self) -> Dict:
        """Initialize database of pollution reduction suggestions"""
        return {
            'co2_reduction': [
                {
                    'id': 'co2_001',
                    'title': 'Optimize Combustion Efficiency',
                    'description': 'Improve air-fuel ratio and combustion temperature control to reduce CO₂ emissions.',
                    'factory_types': ['Coal Power Plant', 'Steel Mill', 'Cement Factory'],
                    'expected_impact': '15-25% CO₂ reduction',
                    'implementation_time': '2-4 weeks',
                    'cost': 'Medium',
                    'priority_base': 8
                },
                {
                    'id': 'co2_002',
                    'title': 'Install Carbon Capture System',
                    'description': 'Implement post-combustion carbon capture technology to trap CO₂ emissions.',
                    'factory_types': ['Coal Power Plant', 'Cement Factory'],
                    'expected_impact': '80-90% CO₂ reduction',
                    'implementation_time': '6-12 months',
                    'cost': 'High',
                    'priority_base': 9
                },
                {
                    'id': 'co2_003',
                    'title': 'Switch to Renewable Energy',
                    'description': 'Transition to solar, wind, or other renewable energy sources for operations.',
                    'factory_types': ['Textile Factory', 'Chemical Plant'],
                    'expected_impact': '70-95% CO₂ reduction',
                    'implementation_time': '3-6 months',
                    'cost': 'High',
                    'priority_base': 10
                }
            ],
            'no2_reduction': [
                {
                    'id': 'no2_001',
                    'title': 'Install Selective Catalytic Reduction (SCR)',
                    'description': 'Use SCR technology to convert NOx to nitrogen and water vapor.',
                    'factory_types': ['Coal Power Plant', 'Steel Mill'],
                    'expected_impact': '80-95% NOx reduction',
                    'implementation_time': '3-6 months',
                    'cost': 'High',
                    'priority_base': 9
                },
                {
                    'id': 'no2_002',
                    'title': 'Optimize Combustion Temperature',
                    'description': 'Lower combustion temperatures to reduce thermal NOx formation.',
                    'factory_types': ['Coal Power Plant', 'Steel Mill', 'Cement Factory'],
                    'expected_impact': '20-40% NOx reduction',
                    'implementation_time': '1-2 weeks',
                    'cost': 'Low',
                    'priority_base': 7
                },
                {
                    'id': 'no2_003',
                    'title': 'Implement Low-NOx Burners',
                    'description': 'Replace existing burners with low-NOx designs to reduce formation.',
                    'factory_types': ['Coal Power Plant', 'Chemical Plant'],
                    'expected_impact': '30-50% NOx reduction',
                    'implementation_time': '4-8 weeks',
                    'cost': 'Medium',
                    'priority_base': 8
                }
            ],
            'so2_reduction': [
                {
                    'id': 'so2_001',
                    'title': 'Install Flue Gas Desulfurization (FGD)',
                    'description': 'Use wet or dry scrubbing technology to remove SO₂ from flue gases.',
                    'factory_types': ['Coal Power Plant', 'Steel Mill'],
                    'expected_impact': '90-99% SO₂ reduction',
                    'implementation_time': '4-8 months',
                    'cost': 'High',
                    'priority_base': 10
                },
                {
                    'id': 'so2_002',
                    'title': 'Switch to Low-Sulfur Fuel',
                    'description': 'Use low-sulfur coal, oil, or natural gas to reduce SO₂ emissions.',
                    'factory_types': ['Coal Power Plant', 'Steel Mill', 'Cement Factory'],
                    'expected_impact': '50-80% SO₂ reduction',
                    'implementation_time': '1-4 weeks',
                    'cost': 'Medium',
                    'priority_base': 8
                },
                {
                    'id': 'so2_003',
                    'title': 'Implement Sorbent Injection',
                    'description': 'Inject limestone or other sorbents into the combustion process.',
                    'factory_types': ['Coal Power Plant', 'Cement Factory'],
                    'expected_impact': '60-80% SO₂ reduction',
                    'implementation_time': '2-6 weeks',
                    'cost': 'Medium',
                    'priority_base': 7
                }
            ],
            'general': [
                {
                    'id': 'gen_001',
                    'title': 'Implement Real-time Monitoring',
                    'description': 'Install continuous emission monitoring systems for better control.',
                    'factory_types': ['All'],
                    'expected_impact': '10-20% overall reduction through better control',
                    'implementation_time': '2-4 weeks',
                    'cost': 'Medium',
                    'priority_base': 6
                },
                {
                    'id': 'gen_002',
                    'title': 'Regular Equipment Maintenance',
                    'description': 'Implement preventive maintenance schedule for emission control equipment.',
                    'factory_types': ['All'],
                    'expected_impact': '5-15% improvement in control efficiency',
                    'implementation_time': '1 week',
                    'cost': 'Low',
                    'priority_base': 5
                }
            ]
        }
    
    def _load_learning_data(self) -> Dict:
        """Load learning data from feedback"""
        try:
            if os.path.exists(self.feedback_file):
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        
        return {
            'feedback_history': [],
            'suggestion_effectiveness': {},
            'implementation_success': {}
        }
    
    def get_suggestions(self, readings: Dict, factory_type: str) -> List[Dict]:
        """Get AI-powered suggestions based on current readings and factory type"""
        suggestions = []
        
        # Determine which gases need attention
        problem_gases = []
        for gas in ['co2', 'no2', 'so2']:
            if gas in readings:
                # Simple threshold check (could be more sophisticated)
                thresholds = {'co2': 600, 'no2': 80, 'so2': 50}
                if readings[gas] > thresholds[gas]:
                    problem_gases.append(gas)
        
        # Get relevant suggestions
        for gas in problem_gases:
            gas_suggestions = self.suggestions_db.get(f'{gas}_reduction', [])
            for suggestion in gas_suggestions:
                if factory_type in suggestion['factory_types'] or 'All' in suggestion['factory_types']:
                    # Calculate dynamic priority based on learning
                    dynamic_priority = self._calculate_dynamic_priority(suggestion['id'], readings[gas])
                    
                    suggestion_copy = suggestion.copy()
                    suggestion_copy['priority'] = dynamic_priority
                    suggestions.append(suggestion_copy)
        
        # Add general suggestions
        general_suggestions = self.suggestions_db.get('general', [])
        for suggestion in general_suggestions:
            if factory_type in suggestion['factory_types'] or 'All' in suggestion['factory_types']:
                dynamic_priority = self._calculate_dynamic_priority(suggestion['id'], 0)
                suggestion_copy = suggestion.copy()
                suggestion_copy['priority'] = dynamic_priority
                suggestions.append(suggestion_copy)
        
        # Sort by priority (highest first)
        suggestions.sort(key=lambda x: x['priority'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _calculate_dynamic_priority(self, suggestion_id: str, pollution_level: float) -> int:
        """Calculate dynamic priority based on learning and current conditions"""
        base_priority = 5  # Default priority
        
        # Get base priority from suggestion
        for category in self.suggestions_db.values():
            for suggestion in category:
                if suggestion['id'] == suggestion_id:
                    base_priority = suggestion['priority_base']
                    break
        
        # Adjust based on effectiveness learning
        effectiveness_bonus = 0
        if suggestion_id in self.learning_data['suggestion_effectiveness']:
            effectiveness = self.learning_data['suggestion_effectiveness'][suggestion_id]
            effectiveness_bonus = int(effectiveness * 2)  # 0-10 bonus
        
        # Adjust based on pollution severity
        severity_bonus = min(int(pollution_level / 100), 3)  # 0-3 bonus
        
        return min(base_priority + effectiveness_bonus + severity_bonus, 10)
    
    def record_feedback(self, suggestion_id: str, feedback_type: str):
        """Record feedback for learning"""
        feedback_entry = {
            'suggestion_id': suggestion_id,
            'feedback_type': feedback_type,  # 'helpful', 'not_helpful', 'implemented'
            'timestamp': datetime.now().isoformat()
        }
        
        self.learning_data['feedback_history'].append(feedback_entry)
        
        # Update effectiveness scores
        if suggestion_id not in self.learning_data['suggestion_effectiveness']:
            self.learning_data['suggestion_effectiveness'][suggestion_id] = 2.5  # Start at neutral
        
        current_score = self.learning_data['suggestion_effectiveness'][suggestion_id]
        
        if feedback_type == 'helpful':
            new_score = min(current_score + 0.5, 5.0)
        elif feedback_type == 'implemented':
            new_score = min(current_score + 1.0, 5.0)
        elif feedback_type == 'not_helpful':
            new_score = max(current_score - 0.3, 0.0)
        else:
            new_score = current_score
        
        self.learning_data['suggestion_effectiveness'][suggestion_id] = new_score
        
        # Save learning data
        self._save_learning_data()
    
    def _save_learning_data(self):
        """Save learning data to file"""
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2)
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about the learning system"""
        total_suggestions = len(self.learning_data['feedback_history'])
        
        if total_suggestions == 0:
            return {
                'total_suggestions': 0,
                'implementation_rate': 0,
                'avg_effectiveness': 0
            }
        
        implemented_count = len([f for f in self.learning_data['feedback_history'] if f['feedback_type'] == 'implemented'])
        implementation_rate = (implemented_count / total_suggestions) * 100
        
        effectiveness_scores = list(self.learning_data['suggestion_effectiveness'].values())
        avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores) if effectiveness_scores else 0
        
        return {
            'total_suggestions': total_suggestions,
            'implementation_rate': implementation_rate,
            'avg_effectiveness': avg_effectiveness
        }
