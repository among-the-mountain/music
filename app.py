"""
Flask Backend API
Module 5: REST API for Data and ML Results
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os
import pandas as pd
import numpy as np

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DB_PATH = 'data/yambda.db'


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Serve main dashboard"""
    return app.send_static_file('index.html')


@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get data overview and descriptive statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get overview from metadata
        cursor.execute('SELECT value FROM metadata WHERE key = ?', ('overview',))
        result = cursor.fetchone()
        
        if result:
            overview = json.loads(result[0])
        else:
            # Calculate on-the-fly if not stored
            overview = {
                'total_events': 0,
                'unique_users': 0,
                'unique_tracks': 0
            }
        
        conn.close()
        return jsonify(overview)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/event-distribution', methods=['GET'])
def get_event_distribution():
    """Get event type distribution"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT event_type, COUNT(*) as count
            FROM multi_event
            GROUP BY event_type
            ORDER BY count DESC
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        result = {
            'labels': df['event_type'].tolist(),
            'values': df['count'].tolist()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/completion-distribution', methods=['GET'])
def get_completion_distribution():
    """Get completion rate distribution"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT played_ratio_pct
            FROM multi_event
            WHERE event_type = 'listen'
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Create bins
        bins = [0, 25, 50, 75, 100]
        labels = ['0-25%', '25-50%', '50-75%', '75-100%']
        df['bin'] = pd.cut(df['played_ratio_pct'], bins=bins, labels=labels, include_lowest=True)
        
        counts = df['bin'].value_counts().sort_index()
        
        result = {
            'labels': labels,
            'values': [int(counts.get(label, 0)) for label in labels]
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clustering/results', methods=['GET'])
def get_clustering_results():
    """Get song clustering results"""
    try:
        conn = get_db_connection()
        
        # Get cluster analysis
        query = '''
            SELECT cluster, avg_completion_rate, like_ratio, listen_count
            FROM cluster_analysis
            ORDER BY cluster
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        result = {
            'clusters': df['cluster'].tolist(),
            'avg_completion_rate': df['avg_completion_rate'].tolist(),
            'like_ratio': df['like_ratio'].tolist(),
            'listen_count': df['listen_count'].tolist()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clustering/distribution', methods=['GET'])
def get_cluster_distribution():
    """Get cluster size distribution"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT cluster, COUNT(*) as count
            FROM song_clusters
            GROUP BY cluster
            ORDER BY cluster
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        result = {
            'labels': [f'Cluster {c}' for c in df['cluster'].tolist()],
            'values': df['count'].tolist()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/prediction/metrics', methods=['GET'])
def get_prediction_metrics():
    """Get completion rate prediction metrics"""
    try:
        metrics_path = 'models/regression_metrics.json'
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
            return jsonify(metrics)
        else:
            return jsonify({'error': 'Metrics not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/prediction/feature-importance', methods=['GET'])
def get_feature_importance():
    """Get feature importance from prediction model"""
    try:
        importance_path = 'models/feature_importance.csv'
        
        if os.path.exists(importance_path):
            df = pd.read_csv(importance_path)
            
            # Get top 10 features
            top_features = df.head(10)
            
            result = {
                'features': top_features['feature'].tolist(),
                'importance': top_features['importance'].tolist()
            }
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Feature importance not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/anomaly/summary', methods=['GET'])
def get_anomaly_summary():
    """Get anomaly detection summary"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomaly_count
            FROM user_anomalies
        '''
        
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        
        total = row[0] if row else 0
        anomaly = row[1] if row else 0
        
        conn.close()
        
        result = {
            'total_users': total,
            'anomaly_count': anomaly,
            'anomaly_ratio': anomaly / total if total > 0 else 0,
            'normal_count': total - anomaly
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/anomaly/distribution', methods=['GET'])
def get_anomaly_distribution():
    """Get anomaly score distribution"""
    try:
        anomaly_path = 'models/anomaly_results.csv'
        
        if os.path.exists(anomaly_path):
            df = pd.read_csv(anomaly_path)
            
            # Create histogram bins
            normal = df[~df['is_anomaly']]['anomaly_score'].values
            anomaly = df[df['is_anomaly']]['anomaly_score'].values
            
            result = {
                'normal_scores': normal.tolist()[:1000],  # Limit for performance
                'anomaly_scores': anomaly.tolist()[:1000]
            }
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Anomaly results not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-behavior/profile', methods=['GET'])
def get_user_behavior_profile():
    """Get aggregated user behavior profile"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT 
                AVG(avg_completion_rate) as avg_completion,
                AVG(like_ratio) as avg_like_ratio,
                AVG(behavior_diversity) as avg_diversity,
                AVG(unique_items_count) as avg_unique_items,
                AVG(total_events) as avg_total_events
            FROM user_features
        '''
        
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        
        conn.close()
        
        result = {
            'avg_completion_rate': row[0] if row else 0,
            'avg_like_ratio': row[1] if row else 0,
            'avg_behavior_diversity': row[2] if row else 0,
            'avg_unique_items': row[3] if row else 0,
            'avg_total_events': row[4] if row else 0
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user-behavior/diversity-distribution', methods=['GET'])
def get_diversity_distribution():
    """Get behavior diversity distribution"""
    try:
        conn = get_db_connection()
        
        query = '''
            SELECT behavior_diversity, COUNT(*) as count
            FROM user_features
            GROUP BY behavior_diversity
            ORDER BY behavior_diversity
        '''
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        result = {
            'labels': df['behavior_diversity'].tolist(),
            'values': df['count'].tolist()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get quick statistics for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic counts
        cursor.execute('SELECT COUNT(*) FROM multi_event')
        total_events = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT uid) FROM multi_event')
        unique_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT item_id) FROM multi_event')
        unique_tracks = cursor.fetchone()[0]
        
        # Get average completion rate
        cursor.execute('''
            SELECT AVG(played_ratio_pct) 
            FROM multi_event 
            WHERE event_type = 'listen'
        ''')
        avg_completion = cursor.fetchone()[0] or 0
        
        conn.close()
        
        result = {
            'total_events': total_events,
            'unique_users': unique_users,
            'unique_tracks': unique_tracks,
            'avg_completion_rate': avg_completion
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Please run data_loader.py first.")
        exit(1)
    
    print("Starting Flask server...")
    print("Dashboard available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
