import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import json
import os
from typing import Dict, List, Tuple

class PollutionDataSimulator:
    """Simulates real-time pollution data for CO₂, NO₂, and SO₂"""
    
    def __init__(self):
        self.base_levels = {
            'co2': 400,  # ppm
            'no2': 40,   # µg/m³
            'so2': 20    # µg/m³
        }
        
        # WHO/CPCB guidelines for dangerous levels
        self.danger_thresholds = {
            'co2': 1000,   # ppm
            'no2': 200,    # µg/m³ (1-hour average)
            'so2': 500     # µg/m³ (10-minute average)
        }
        
        self.warning_thresholds = {
            'co2': 800,
            'no2': 100,
            'so2': 250
        }
        
        # Initialize data storage
        self.data_file = "pollution_data.json"
        self.historical_data = self._load_historical_data()
    
    def _load_historical_data(self) -> pd.DataFrame:
        """Load historical data from file or create initial dataset"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            except:
                pass
        
        # Generate initial 24 hours of data
        return self._generate_initial_data()
    
    def _generate_initial_data(self) -> pd.DataFrame:
        """Generate initial 24 hours of historical data"""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        timestamps = pd.date_range(start_time, end_time, freq='5min')
        data = []
        
        for timestamp in timestamps:
            reading = self._generate_realistic_reading(timestamp)
            reading['timestamp'] = timestamp.isoformat()
            data.append(reading)
        
        return pd.DataFrame(data)
    
    def _generate_realistic_reading(self, timestamp: datetime) -> Dict:
        """Generate realistic pollution readings based on time and patterns"""
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Simulate daily patterns (higher during work hours)
        work_hour_multiplier = 1.5 if 8 <= hour <= 18 else 0.8
        weekend_multiplier = 0.7 if day_of_week >= 5 else 1.0
        
        # Add some randomness and trends
        noise_factor = random.uniform(0.8, 1.2)
        
        # Simulate different factory types having different base emissions
        factory_multipliers = {
            'co2': work_hour_multiplier * weekend_multiplier * noise_factor,
            'no2': work_hour_multiplier * weekend_multiplier * noise_factor * 1.2,
            'so2': work_hour_multiplier * weekend_multiplier * noise_factor * 0.9
        }
        
        reading = {}
        for gas, base_level in self.base_levels.items():
            # Add seasonal and random variations
            seasonal_variation = np.sin(timestamp.timetuple().tm_yday / 365 * 2 * np.pi) * 0.1
            random_variation = np.random.normal(0, 0.15)
            
            level = base_level * factory_multipliers[gas] * (1 + seasonal_variation + random_variation)
            
            # Ensure non-negative values
            reading[gas] = max(0, level)
        
        # Add weather influence (simplified)
        weather_factor = random.uniform(0.9, 1.1)
        for gas in reading:
            reading[gas] *= weather_factor
        
        return reading
    
    def get_current_readings(self) -> Dict:
        """Get current pollution readings"""
        current_reading = self._generate_realistic_reading(datetime.now())
        
        # Store the reading
        self._store_reading(current_reading)
        
        return current_reading
    
    def _store_reading(self, reading: Dict):
        """Store reading in historical data"""
        reading['timestamp'] = datetime.now().isoformat()
        
        # Add to historical data
        new_row = pd.DataFrame([reading])
        self.historical_data = pd.concat([self.historical_data, new_row], ignore_index=True)
        
        # Keep only last 7 days of data
        cutoff_time = datetime.now() - timedelta(days=7)
        self.historical_data['timestamp'] = pd.to_datetime(self.historical_data['timestamp'])
        self.historical_data = self.historical_data[self.historical_data['timestamp'] > cutoff_time]
        
        # Save to file
        self._save_historical_data()
    
    def _save_historical_data(self):
        """Save historical data to file"""
        try:
            data_to_save = self.historical_data.copy()
            data_to_save['timestamp'] = data_to_save['timestamp'].dt.isoformat()
            
            with open(self.data_file, 'w') as f:
                json.dump(data_to_save.to_dict('records'), f)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_historical_data(self, hours: int = 24) -> pd.DataFrame:
        """Get historical data for specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Ensure timestamp column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.historical_data['timestamp']):
            self.historical_data['timestamp'] = pd.to_datetime(self.historical_data['timestamp'])
        
        filtered_data = self.historical_data[self.historical_data['timestamp'] > cutoff_time].copy()
        return filtered_data.sort_values('timestamp')
    
    def simulate_emergency_scenario(self, gas: str, duration_minutes: int = 15):
        """Simulate an emergency scenario with high pollution levels"""
        emergency_levels = {
            'co2': 1500,
            'no2': 300,
            'so2': 600
        }
        
        # This would be used for testing alert systems
        emergency_reading = self.get_current_readings()
        emergency_reading[gas] = emergency_levels[gas] * random.uniform(1.0, 1.5)
        
        return emergency_reading
    
    def get_satellite_comparison_data(self) -> Dict:
        """Simulate satellite data for comparison"""
        # This would normally come from satellite APIs
        current = self.get_current_readings()
        
        # Simulate regional averages (usually lower than point sources)
        satellite_data = {
            'co2_regional': current['co2'] * 0.7,
            'no2_regional': current['no2'] * 0.6,
            'so2_regional': current['so2'] * 0.5,
            'co2_factory': current['co2'],
            'no2_factory': current['no2'],
            'so2_factory': current['so2']
        }
        
        return satellite_data
    
    def get_pollution_statistics(self, hours: int = 24) -> Dict:
        """Get statistical summary of pollution data"""
        data = self.get_historical_data(hours)
        
        if data.empty:
            return {}
        
        stats = {}
        for gas in ['co2', 'no2', 'so2']:
            if gas in data.columns:
                stats[gas] = {
                    'mean': float(data[gas].mean()),
                    'max': float(data[gas].max()),
                    'min': float(data[gas].min()),
                    'std': float(data[gas].std()),
                    'current': float(data[gas].iloc[-1]) if len(data) > 0 else 0
                }
        
        return stats
    
    def check_threshold_violations(self, reading: Dict) -> List[Dict]:
        """Check if current readings violate safety thresholds"""
        violations = []
        
        for gas, level in reading.items():
            if gas in self.danger_thresholds:
                if level > self.danger_thresholds[gas]:
                    violations.append({
                        'gas': gas,
                        'level': level,
                        'threshold': self.danger_thresholds[gas],
                        'severity': 'critical',
                        'message': f'{gas.upper()} level ({level:.1f}) exceeds danger threshold ({self.danger_thresholds[gas]})'
                    })
                elif level > self.warning_thresholds[gas]:
                    violations.append({
                        'gas': gas,
                        'level': level,
                        'threshold': self.warning_thresholds[gas],
                        'severity': 'warning',
                        'message': f'{gas.upper()} level ({level:.1f}) exceeds warning threshold ({self.warning_thresholds[gas]})'
                    })
        
        return violations
