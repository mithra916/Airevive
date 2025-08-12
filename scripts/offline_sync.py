import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import time

class OfflineSync:
    """Handle offline data storage and synchronization"""
    
    def __init__(self):
        self.db_file = "offline_data.db"
        self.sync_status_file = "sync_status.json"
        self.is_online = True
        self.sync_thread = None
        self.sync_interval = 300  # 5 minutes
        
        # Initialize database
        self._init_database()
        
        # Start background sync thread
        self._start_sync_thread()
    
    def _init_database(self):
        """Initialize SQLite database for offline storage"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pollution_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    co2 REAL,
                    no2 REAL,
                    so2 REAL,
                    synced INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    gas TEXT NOT NULL,
                    level REAL NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT,
                    duration_minutes REAL,
                    synced INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    description TEXT,
                    user_id TEXT,
                    synced INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    content TEXT,
                    recipients TEXT,
                    sent INTEGER DEFAULT 0,
                    synced INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def store_pollution_reading(self, reading: Dict) -> bool:
        """Store pollution reading locally"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO pollution_readings (timestamp, co2, no2, so2, synced)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                reading.get('timestamp', datetime.now().isoformat()),
                reading.get('co2', 0),
                reading.get('no2', 0),
                reading.get('so2', 0),
                1 if self.is_online else 0
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing pollution reading: {e}")
            return False
    
    def store_alert(self, alert: Dict) -> bool:
        """Store alert locally"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (timestamp, gas, level, severity, message, duration_minutes, synced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.get('timestamp', datetime.now().isoformat()),
                alert.get('gas', ''),
                alert.get('level', 0),
                alert.get('severity', ''),
                alert.get('message', ''),
                alert.get('duration_minutes', 0),
                1 if self.is_online else 0
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing alert: {e}")
            return False
    
    def store_action(self, action_type: str, description: str, user_id: str = "system") -> bool:
        """Store user action locally"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO actions (timestamp, action_type, description, user_id, synced)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                action_type,
                description,
                user_id,
                1 if self.is_online else 0
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing action: {e}")
            return False
    
    def store_report(self, report_type: str, content: str, recipients: List[str] = None) -> bool:
        """Store report locally"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            recipients_str = json.dumps(recipients) if recipients else "[]"
            
            cursor.execute('''
                INSERT INTO reports (timestamp, report_type, content, recipients, sent, synced)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                report_type,
                content,
                recipients_str,
                0,  # Not sent yet
                1 if self.is_online else 0
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing report: {e}")
            return False
    
    def get_unsynced_data(self) -> Dict[str, List[Dict]]:
        """Get all unsynced data"""
        unsynced_data = {
            'pollution_readings': [],
            'alerts': [],
            'actions': [],
            'reports': []
        }
        
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Get unsynced pollution readings
            cursor.execute('SELECT * FROM pollution_readings WHERE synced = 0')
            unsynced_data['pollution_readings'] = [dict(row) for row in cursor.fetchall()]
            
            # Get unsynced alerts
            cursor.execute('SELECT * FROM alerts WHERE synced = 0')
            unsynced_data['alerts'] = [dict(row) for row in cursor.fetchall()]
            
            # Get unsynced actions
            cursor.execute('SELECT * FROM actions WHERE synced = 0')
            unsynced_data['actions'] = [dict(row) for row in cursor.fetchall()]
            
            # Get unsynced reports
            cursor.execute('SELECT * FROM reports WHERE synced = 0')
            unsynced_data['reports'] = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
        except Exception as e:
            print(f"Error getting unsynced data: {e}")
        
        return unsynced_data
    
    def mark_as_synced(self, table: str, record_ids: List[int]) -> bool:
        """Mark records as synced"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            placeholders = ','.join(['?' for _ in record_ids])
            query = f'UPDATE {table} SET synced = 1 WHERE id IN ({placeholders})'
            
            cursor.execute(query, record_ids)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error marking records as synced: {e}")
            return False
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        try:
            # Check if we can connect to external services (simulated)
            self.is_online = self._check_connectivity()
            
            # Count pending records
            unsynced_data = self.get_unsynced_data()
            pending_count = sum(len(records) for records in unsynced_data.values())
            
            # Load last sync time
            last_sync = self._get_last_sync_time()
            
            status = {
                'online': self.is_online,
                'pending_records': pending_count,
                'last_sync': last_sync,
                'sync_interval': self.sync_interval
            }
            
            # Save status
            with open(self.sync_status_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            return status
            
        except Exception as e:
            print(f"Error getting sync status: {e}")
            return {
                'online': False,
                'pending_records': 0,
                'last_sync': None,
                'sync_interval': self.sync_interval
            }
    
    def _check_connectivity(self) -> bool:
        """Check if we have internet connectivity (simulated)"""
        # In a real implementation, this would ping external services
        # For simulation, we'll randomly simulate connectivity issues
        import random
        return random.random() > 0.1  # 90% uptime simulation
    
    def _get_last_sync_time(self) -> Optional[str]:
        """Get timestamp of last successful sync"""
        try:
            if os.path.exists(self.sync_status_file):
                with open(self.sync_status_file, 'r') as f:
                    status = json.load(f)
                    return status.get('last_sync')
        except:
            pass
        return None
    
    def _start_sync_thread(self):
        """Start background sync thread"""
        def sync_worker():
            while True:
                try:
                    if self.is_online:
                        self._perform_sync()
                    time.sleep(self.sync_interval)
                except Exception as e:
                    print(f"Sync thread error: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        self.sync_thread = threading.Thread(target=sync_worker, daemon=True)
        self.sync_thread.start()
    
    def _perform_sync(self) -> bool:
        """Perform synchronization with remote servers"""
        try:
            unsynced_data = self.get_unsynced_data()
            
            # Simulate syncing each type of data
            for data_type, records in unsynced_data.items():
                if records:
                    print(f"🔄 Syncing {len(records)} {data_type} records...")
                    
                    # Simulate API calls to remote server
                    success = self._sync_to_remote_server(data_type, records)
                    
                    if success:
                        # Mark records as synced
                        record_ids = [record['id'] for record in records]
                        self.mark_as_synced(data_type, record_ids)
                        print(f"✅ Synced {len(records)} {data_type} records")
                    else:
                        print(f"❌ Failed to sync {data_type} records")
            
            # Update last sync time
            self._update_last_sync_time()
            return True
            
        except Exception as e:
            print(f"Error during sync: {e}")
            return False
    
    def _sync_to_remote_server(self, data_type: str, records: List[Dict]) -> bool:
        """Simulate syncing data to remote server"""
        # In a real implementation, this would make HTTP requests to your backend
        # For simulation, we'll just pretend it works most of the time
        import random
        time.sleep(0.1)  # Simulate network delay
        return random.random() > 0.05  # 95% success rate
    
    def _update_last_sync_time(self):
        """Update last sync timestamp"""
        try:
            status = self.get_sync_status()
            status['last_sync'] = datetime.now().isoformat()
            
            with open(self.sync_status_file, 'w') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            print(f"Error updating sync time: {e}")
    
    def force_sync(self) -> bool:
        """Force immediate synchronization"""
        print("🔄 Forcing immediate sync...")
        return self._perform_sync()
    
    def get_action_log(self, hours: int = 24) -> List[Dict]:
        """Get action log for specified hours"""
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            cursor.execute('''
                SELECT * FROM actions 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_time,))
            
            actions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return actions
            
        except Exception as e:
            print(f"Error getting action log: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data to save space"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Delete old synced records
            tables = ['pollution_readings', 'alerts', 'actions', 'reports']
            
            for table in tables:
                cursor.execute(f'''
                    DELETE FROM {table} 
                    WHERE synced = 1 AND created_at < ?
                ''', (cutoff_time,))
            
            conn.commit()
            conn.close()
            
            print(f"🧹 Cleaned up data older than {days} days")
            
        except Exception as e:
            print(f"Error cleaning up old data: {e}")
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            stats = {}
            tables = ['pollution_readings', 'alerts', 'actions', 'reports']
            
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) as total, COUNT(*) FILTER (WHERE synced = 0) as unsynced FROM {table}')
                result = cursor.fetchone()
                stats[table] = {
                    'total': result[0],
                    'unsynced': result[1]
                }
            
            # Get database file size
            db_size = os.path.getsize(self.db_file) if os.path.exists(self.db_file) else 0
            stats['database_size_mb'] = db_size / (1024 * 1024)
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {}
