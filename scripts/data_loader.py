"""
Yambda Dataset Loader and Preprocessor
Module 0 & 1: Data Overview and Feature Engineering
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime
import sqlite3
import json

class YambdaDataLoader:
    """Load and preprocess Yambda music recommendation dataset"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, 'yambda.db')
        
    def load_dataset_from_hf(self):
        """Load dataset from HuggingFace (for initial setup)"""
        try:
            from datasets import load_dataset
            print("Loading Yambda dataset from HuggingFace...")
            # Note: Requires HuggingFace login
            ds = load_dataset("yandex/yambda", "flat-multievent-50m")
            
            # Save to parquet files
            for key in ds.keys():
                df = ds[key].to_pandas()
                output_path = os.path.join(self.data_dir, f"{key}.parquet")
                df.to_parquet(output_path, index=False)
                print(f"Saved {key} to {output_path}")
                
        except Exception as e:
            print(f"Error loading from HuggingFace: {e}")
            print("Please ensure you are logged in with: huggingface-cli login")
            
    def load_parquet_files(self):
        """Load data from local parquet files"""
        data = {}
        
        # Check for multi_event.parquet (main analysis table)
        multi_event_path = os.path.join(self.data_dir, 'multi_event.parquet')
        if os.path.exists(multi_event_path):
            data['multi_event'] = pd.read_parquet(multi_event_path)
            print(f"Loaded multi_event: {len(data['multi_event'])} rows")
        
        # Load embeddings if available
        embeddings_path = os.path.join(self.data_dir, 'embeddings.parquet')
        if os.path.exists(embeddings_path):
            data['embeddings'] = pd.read_parquet(embeddings_path)
            print(f"Loaded embeddings: {len(data['embeddings'])} rows")
            
        return data
    
    def generate_sample_data(self):
        """Generate sample data for testing and demonstration"""
        print("Generating sample data for demonstration...")
        
        np.random.seed(42)
        n_users = 1000
        n_items = 500
        n_events = 50000
        
        # Generate multi_event data
        event_types = ['listen', 'like', 'dislike', 'unlike', 'undislike']
        
        multi_event = pd.DataFrame({
            'uid': np.random.randint(1, n_users + 1, n_events),
            'item_id': np.random.randint(1, n_items + 1, n_events),
            'timestamp': pd.date_range('2023-01-01', periods=n_events, freq='30s'),
            'is_organic': np.random.choice([True, False], n_events, p=[0.8, 0.2]),
            'event_type': np.random.choice(event_types, n_events, p=[0.7, 0.15, 0.05, 0.05, 0.05]),
            'played_ratio_pct': np.random.beta(3, 2, n_events) * 100,  # Skewed towards higher completion
            'track_length_seconds': np.random.normal(200, 50, n_events).clip(60, 600)
        })
        
        # Generate embeddings (64-dimensional)
        embed_dim = 64
        embeddings_data = []
        for item_id in range(1, n_items + 1):
            # Generate random embedding
            embed = np.random.randn(embed_dim)
            normalized_embed = embed / np.linalg.norm(embed)
            
            embeddings_data.append({
                'item_id': item_id,
                'embed': embed.tolist(),
                'normalized_embed': normalized_embed.tolist()
            })
        
        embeddings = pd.DataFrame(embeddings_data)
        
        # Save to parquet
        multi_event.to_parquet(os.path.join(self.data_dir, 'multi_event.parquet'), index=False)
        embeddings.to_parquet(os.path.join(self.data_dir, 'embeddings.parquet'), index=False)
        
        print(f"Generated {len(multi_event)} events for {n_users} users and {n_items} items")
        print(f"Generated embeddings for {len(embeddings)} items")
        
        return {'multi_event': multi_event, 'embeddings': embeddings}


class DataPreprocessor:
    """Preprocess data and build features"""
    
    def __init__(self, multi_event_df, embeddings_df=None):
        self.multi_event = multi_event_df.copy()
        self.embeddings = embeddings_df.copy() if embeddings_df is not None else None
        
    def clean_data(self):
        """Module 1: Data cleaning"""
        initial_count = len(self.multi_event)
        
        # Remove listens with played_ratio_pct < 10%
        listen_mask = self.multi_event['event_type'] == 'listen'
        valid_plays = (self.multi_event['played_ratio_pct'] >= 10.0) | (~listen_mask)
        self.multi_event = self.multi_event[valid_plays].copy()
        
        print(f"Removed {initial_count - len(self.multi_event)} low-quality listens (< 10% completion)")
        
        # Normalize timestamps to UTC (already in UTC format, but ensure datetime type)
        self.multi_event['timestamp'] = pd.to_datetime(self.multi_event['timestamp'], utc=True)
        
        return self.multi_event
    
    def build_user_features(self):
        """Module 1: Build user-level features"""
        listen_events = self.multi_event[self.multi_event['event_type'] == 'listen'].copy()
        
        # Average played completion rate
        user_avg_completion = listen_events.groupby('uid')['played_ratio_pct'].mean()
        
        # Like ratio (likes / total events)
        user_event_counts = self.multi_event.groupby('uid')['event_type'].value_counts().unstack(fill_value=0)
        total_events = user_event_counts.sum(axis=1)
        like_ratio = user_event_counts.get('like', 0) / total_events.clip(lower=1)
        
        # Behavior diversity (number of unique event types)
        behavior_diversity = self.multi_event.groupby('uid')['event_type'].nunique()
        
        # Number of unique items interacted
        unique_items = self.multi_event.groupby('uid')['item_id'].nunique()
        
        # Total events
        total_events_per_user = self.multi_event.groupby('uid').size()
        
        user_features = pd.DataFrame({
            'uid': user_avg_completion.index,
            'avg_completion_rate': user_avg_completion.values,
            'like_ratio': like_ratio.reindex(user_avg_completion.index, fill_value=0).values,
            'behavior_diversity': behavior_diversity.reindex(user_avg_completion.index, fill_value=1).values,
            'unique_items_count': unique_items.reindex(user_avg_completion.index, fill_value=0).values,
            'total_events': total_events_per_user.reindex(user_avg_completion.index, fill_value=0).values
        })
        
        print(f"Built features for {len(user_features)} users")
        return user_features
    
    def build_track_features(self):
        """Module 1: Build track-level features"""
        listen_events = self.multi_event[self.multi_event['event_type'] == 'listen'].copy()
        
        # Average played completion rate per track
        track_avg_completion = listen_events.groupby('item_id')['played_ratio_pct'].mean()
        
        # Number of times played
        play_count = listen_events.groupby('item_id').size()
        
        # Average track length
        avg_track_length = listen_events.groupby('item_id')['track_length_seconds'].mean()
        
        # Like/dislike ratio
        track_event_counts = self.multi_event.groupby('item_id')['event_type'].value_counts().unstack(fill_value=0)
        total_interactions = track_event_counts.sum(axis=1)
        like_ratio = track_event_counts.get('like', 0) / total_interactions.clip(lower=1)
        
        track_features = pd.DataFrame({
            'item_id': track_avg_completion.index,
            'avg_completion_rate': track_avg_completion.values,
            'play_count': play_count.reindex(track_avg_completion.index, fill_value=0).values,
            'avg_track_length': avg_track_length.reindex(track_avg_completion.index, fill_value=0).values,
            'like_ratio': like_ratio.reindex(track_avg_completion.index, fill_value=0).values
        })
        
        print(f"Built features for {len(track_features)} tracks")
        return track_features
    
    def get_data_overview(self):
        """Module 0: Generate descriptive statistics"""
        overview = {
            'total_events': len(self.multi_event),
            'unique_users': self.multi_event['uid'].nunique(),
            'unique_tracks': self.multi_event['item_id'].nunique(),
            'event_type_distribution': self.multi_event['event_type'].value_counts().to_dict(),
            'avg_played_ratio': self.multi_event[self.multi_event['event_type'] == 'listen']['played_ratio_pct'].mean(),
            'organic_ratio': self.multi_event['is_organic'].sum() / len(self.multi_event),
            'date_range': {
                'start': str(self.multi_event['timestamp'].min()),
                'end': str(self.multi_event['timestamp'].max())
            }
        }
        
        # Completion rate distribution
        listen_events = self.multi_event[self.multi_event['event_type'] == 'listen']
        completion_bins = [0, 25, 50, 75, 100]
        completion_dist = pd.cut(listen_events['played_ratio_pct'], bins=completion_bins).value_counts().sort_index()
        overview['completion_rate_distribution'] = {str(k): v for k, v in completion_dist.items()}
        
        return overview


def setup_database(db_path, multi_event_df, user_features_df, track_features_df, overview):
    """Create SQLite database and store preprocessed data"""
    conn = sqlite3.connect(db_path)
    
    # Store main tables
    multi_event_df.to_sql('multi_event', conn, if_exists='replace', index=False)
    user_features_df.to_sql('user_features', conn, if_exists='replace', index=False)
    track_features_df.to_sql('track_features', conn, if_exists='replace', index=False)
    
    # Store overview as JSON in metadata table
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    cursor.execute('INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)',
                   ('overview', json.dumps(overview)))
    
    conn.commit()
    conn.close()
    print(f"Database created at {db_path}")


if __name__ == '__main__':
    # Initialize loader
    loader = YambdaDataLoader()
    
    # Try to load existing data, or generate sample data
    if not os.path.exists('data'):
        os.makedirs('data')
    
    try:
        data = loader.load_parquet_files()
        if not data:
            print("No parquet files found. Generating sample data...")
            data = loader.generate_sample_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        print("Generating sample data...")
        data = loader.generate_sample_data()
    
    # Preprocess data
    preprocessor = DataPreprocessor(data['multi_event'], data.get('embeddings'))
    
    # Clean data
    cleaned_data = preprocessor.clean_data()
    
    # Build features
    user_features = preprocessor.build_user_features()
    track_features = preprocessor.build_track_features()
    
    # Get overview
    overview = preprocessor.get_data_overview()
    print("\n=== Data Overview ===")
    print(json.dumps(overview, indent=2, default=str))
    
    # Setup database
    setup_database('data/yambda.db', cleaned_data, user_features, track_features, overview)
    
    print("\n✓ Data preprocessing completed successfully!")
