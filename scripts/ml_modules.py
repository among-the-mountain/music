"""
Machine Learning Modules
Module 2: Song Clustering (Unsupervised)
Module 3: Completion Rate Prediction (Supervised)
Module 4: Anomaly Detection (Unsupervised)
"""

import os
import pandas as pd
import numpy as np
import sqlite3
import json
import pickle
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error


class SongClustering:
    """Module 2: Unsupervised Learning - Song Content Clustering"""
    
    def __init__(self, embeddings_df, multi_event_df=None):
        self.embeddings = embeddings_df.copy()
        self.multi_event = multi_event_df
        self.model = None
        self.pca = None
        self.n_clusters = None
        self.results = None
        
    def prepare_features(self, use_pca=True, n_components=10):
        """Extract and optionally reduce dimensionality of embeddings"""
        # Extract normalized embeddings
        embed_matrix = np.array(self.embeddings['normalized_embed'].tolist())
        
        if use_pca and embed_matrix.shape[1] > n_components:
            print(f"Applying PCA: {embed_matrix.shape[1]} -> {n_components} dimensions")
            self.pca = PCA(n_components=n_components, random_state=42)
            embed_matrix = self.pca.fit_transform(embed_matrix)
            print(f"Explained variance ratio: {self.pca.explained_variance_ratio_.sum():.3f}")
        
        return embed_matrix
    
    def find_optimal_k(self, features, k_range=range(3, 11)):
        """Find optimal number of clusters using silhouette score"""
        silhouette_scores = []
        
        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(features)
            score = silhouette_score(features, labels)
            silhouette_scores.append(score)
            print(f"k={k}: silhouette_score={score:.4f}")
        
        optimal_k = k_range[np.argmax(silhouette_scores)]
        best_score = max(silhouette_scores)
        print(f"\nOptimal k={optimal_k} with silhouette_score={best_score:.4f}")
        
        return optimal_k, silhouette_scores
    
    def train(self, features, n_clusters=None):
        """Train KMeans clustering model"""
        if n_clusters is None:
            n_clusters, _ = self.find_optimal_k(features)
        
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.model.fit_predict(features)
        
        # Calculate silhouette score
        silhouette = silhouette_score(features, cluster_labels)
        
        # Store results
        self.embeddings['cluster'] = cluster_labels
        
        print(f"\nClustering completed:")
        print(f"  Number of clusters: {n_clusters}")
        print(f"  Silhouette score: {silhouette:.4f}")
        
        return cluster_labels, silhouette
    
    def analyze_clusters(self):
        """Analyze clusters by completion rate and like ratio"""
        if self.multi_event is None:
            print("No multi_event data available for cluster analysis")
            return None
        
        # Join cluster labels with event data
        event_with_cluster = self.multi_event.merge(
            self.embeddings[['item_id', 'cluster']], 
            on='item_id', 
            how='inner'
        )
        
        # Analyze listen events
        listen_events = event_with_cluster[event_with_cluster['event_type'] == 'listen']
        cluster_completion = listen_events.groupby('cluster')['played_ratio_pct'].agg(['mean', 'std', 'count'])
        
        # Analyze like ratio
        event_counts = event_with_cluster.groupby('cluster')['event_type'].value_counts().unstack(fill_value=0)
        total_events = event_counts.sum(axis=1)
        like_ratio = event_counts.get('like', 0) / total_events.clip(lower=1)
        
        # Combine results
        cluster_analysis = pd.DataFrame({
            'cluster': cluster_completion.index,
            'avg_completion_rate': cluster_completion['mean'].values,
            'std_completion_rate': cluster_completion['std'].values,
            'listen_count': cluster_completion['count'].values,
            'like_ratio': like_ratio.reindex(cluster_completion.index, fill_value=0).values
        })
        
        print("\n=== Cluster Analysis ===")
        print(cluster_analysis.to_string())
        
        self.results = cluster_analysis
        return cluster_analysis
    
    def save_model(self, model_dir='models'):
        """Save clustering model and results"""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save KMeans model
        with open(os.path.join(model_dir, 'kmeans_model.pkl'), 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save PCA if used
        if self.pca is not None:
            with open(os.path.join(model_dir, 'pca_model.pkl'), 'wb') as f:
                pickle.dump(self.pca, f)
        
        # Save results
        if self.results is not None:
            self.results.to_csv(os.path.join(model_dir, 'cluster_analysis.csv'), index=False)
        
        print(f"Models saved to {model_dir}/")


class CompletionRatePredictor:
    """Module 3: Supervised Learning - Completion Rate Prediction"""
    
    def __init__(self, multi_event_df, user_features_df, track_features_df, embeddings_df=None):
        self.multi_event = multi_event_df
        self.user_features = user_features_df
        self.track_features = track_features_df
        self.embeddings = embeddings_df
        self.model = None
        self.feature_importance = None
        self.metrics = None
        
    def prepare_features(self, use_embeddings=True, n_pca_components=5):
        """Prepare feature matrix for prediction"""
        # Filter listen events only
        listen_events = self.multi_event[self.multi_event['event_type'] == 'listen'].copy()
        
        # Merge with user features
        data = listen_events.merge(
            self.user_features[['uid', 'avg_completion_rate', 'like_ratio', 'behavior_diversity']],
            on='uid',
            how='left',
            suffixes=('', '_user')
        )
        
        # Merge with track features
        data = data.merge(
            self.track_features[['item_id', 'avg_completion_rate', 'like_ratio']],
            on='item_id',
            how='left',
            suffixes=('', '_track')
        )
        
        # Basic features
        feature_columns = [
            'track_length_seconds',
            'avg_completion_rate_user',
            'like_ratio_user',
            'behavior_diversity',
            'avg_completion_rate_track',
            'like_ratio_track'
        ]
        
        # Add embedding features if available
        if use_embeddings and self.embeddings is not None:
            embed_matrix = np.array(self.embeddings['normalized_embed'].tolist())
            
            # Apply PCA to reduce dimensions
            pca = PCA(n_components=n_pca_components, random_state=42)
            embed_reduced = pca.fit_transform(embed_matrix)
            
            # Create embedding DataFrame
            embed_df = pd.DataFrame(
                embed_reduced,
                columns=[f'embed_{i}' for i in range(n_pca_components)]
            )
            embed_df['item_id'] = self.embeddings['item_id'].values
            
            # Merge embeddings
            data = data.merge(embed_df, on='item_id', how='left')
            feature_columns.extend([f'embed_{i}' for i in range(n_pca_components)])
        
        # Fill missing values
        data = data.fillna(0)
        
        # Prepare X and y
        X = data[feature_columns].values
        y = data['played_ratio_pct'].values
        
        print(f"Feature matrix shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        return X, y, feature_columns
    
    def train(self, X, y, test_size=0.2):
        """Train RandomForest regression model"""
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        print(f"Training set: {X_train.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        print("Training RandomForest model...")
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Calculate metrics
        mae_train = mean_absolute_error(y_train, y_pred_train)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        
        self.metrics = {
            'mae_train': mae_train,
            'mae_test': mae_test,
            'rmse_train': rmse_train,
            'rmse_test': rmse_test
        }
        
        print(f"\n=== Model Performance ===")
        print(f"Training MAE: {mae_train:.2f}")
        print(f"Test MAE: {mae_test:.2f}")
        print(f"Training RMSE: {rmse_train:.2f}")
        print(f"Test RMSE: {rmse_test:.2f}")
        
        return y_test, y_pred_test
    
    def get_feature_importance(self, feature_names):
        """Extract and display feature importance"""
        if self.model is None:
            return None
        
        importance = self.model.feature_importances_
        feature_importance = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        print("\n=== Feature Importance ===")
        print(feature_importance.to_string())
        
        self.feature_importance = feature_importance
        return feature_importance
    
    def save_model(self, model_dir='models'):
        """Save model and results"""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        with open(os.path.join(model_dir, 'rf_regressor.pkl'), 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save metrics
        with open(os.path.join(model_dir, 'regression_metrics.json'), 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save feature importance
        if self.feature_importance is not None:
            self.feature_importance.to_csv(os.path.join(model_dir, 'feature_importance.csv'), index=False)
        
        print(f"Model saved to {model_dir}/")


class AnomalyDetector:
    """Module 4: Unsupervised Anomaly Detection"""
    
    def __init__(self, multi_event_df, user_features_df):
        self.multi_event = multi_event_df
        self.user_features = user_features_df
        self.model = None
        self.anomaly_results = None
        
    def build_anomaly_features(self):
        """Build user behavior features for anomaly detection"""
        # Calculate time-based features
        user_time_stats = self.multi_event.groupby('uid').agg({
            'timestamp': ['min', 'max', 'count']
        })
        user_time_stats.columns = ['first_event', 'last_event', 'total_events']
        user_time_stats['time_span_hours'] = (
            (user_time_stats['last_event'] - user_time_stats['first_event']).dt.total_seconds() / 3600
        ).clip(lower=0.01)  # Avoid division by zero
        
        # Plays per hour
        user_time_stats['plays_per_hour'] = user_time_stats['total_events'] / user_time_stats['time_span_hours']
        
        # Calculate completion rate variance (for listen events)
        listen_events = self.multi_event[self.multi_event['event_type'] == 'listen']
        completion_variance = listen_events.groupby('uid')['played_ratio_pct'].var()
        
        # Calculate average time between plays
        def calc_avg_interval(group):
            if len(group) < 2:
                return 0
            sorted_times = group['timestamp'].sort_values()
            intervals = sorted_times.diff().dt.total_seconds().dropna()
            return intervals.mean() if len(intervals) > 0 else 0
        
        avg_intervals = self.multi_event.groupby('uid').apply(calc_avg_interval)
        
        # Merge features
        anomaly_features = pd.DataFrame({
            'uid': user_time_stats.index,
            'plays_per_hour': user_time_stats['plays_per_hour'].values,
            'total_events': user_time_stats['total_events'].values,
            'completion_variance': completion_variance.reindex(user_time_stats.index, fill_value=0).values,
            'avg_interval_seconds': avg_intervals.reindex(user_time_stats.index, fill_value=0).values
        })
        
        # Add user features
        anomaly_features = anomaly_features.merge(
            self.user_features[['uid', 'avg_completion_rate', 'behavior_diversity']],
            on='uid',
            how='left'
        )
        
        print(f"Built anomaly detection features for {len(anomaly_features)} users")
        return anomaly_features
    
    def train(self, features_df, contamination=0.05):
        """Train Isolation Forest model"""
        feature_columns = [
            'plays_per_hour', 'total_events', 'completion_variance',
            'avg_interval_seconds', 'avg_completion_rate', 'behavior_diversity'
        ]
        
        X = features_df[feature_columns].fillna(0).values
        
        print(f"Training Isolation Forest with contamination={contamination}")
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_jobs=-1
        )
        
        # Fit and predict (-1 for anomalies, 1 for normal)
        predictions = self.model.fit_predict(X)
        anomaly_scores = self.model.score_samples(X)
        
        # Store results
        features_df['is_anomaly'] = predictions == -1
        features_df['anomaly_score'] = anomaly_scores
        
        anomaly_count = (predictions == -1).sum()
        anomaly_ratio = anomaly_count / len(predictions)
        
        print(f"\n=== Anomaly Detection Results ===")
        print(f"Total users: {len(predictions)}")
        print(f"Anomalous users: {anomaly_count} ({anomaly_ratio:.2%})")
        
        self.anomaly_results = features_df
        return features_df
    
    def analyze_anomalies(self):
        """Analyze characteristics of anomalous users"""
        if self.anomaly_results is None:
            return None
        
        normal_users = self.anomaly_results[~self.anomaly_results['is_anomaly']]
        anomaly_users = self.anomaly_results[self.anomaly_results['is_anomaly']]
        
        comparison = pd.DataFrame({
            'metric': ['plays_per_hour', 'total_events', 'completion_variance', 
                      'avg_completion_rate', 'behavior_diversity'],
            'normal_mean': [
                normal_users['plays_per_hour'].mean(),
                normal_users['total_events'].mean(),
                normal_users['completion_variance'].mean(),
                normal_users['avg_completion_rate'].mean(),
                normal_users['behavior_diversity'].mean()
            ],
            'anomaly_mean': [
                anomaly_users['plays_per_hour'].mean(),
                anomaly_users['total_events'].mean(),
                anomaly_users['completion_variance'].mean(),
                anomaly_users['avg_completion_rate'].mean(),
                anomaly_users['behavior_diversity'].mean()
            ]
        })
        
        print("\n=== Normal vs Anomaly Comparison ===")
        print(comparison.to_string())
        
        return comparison
    
    def save_model(self, model_dir='models'):
        """Save anomaly detection model and results"""
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        with open(os.path.join(model_dir, 'isolation_forest.pkl'), 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save results
        if self.anomaly_results is not None:
            self.anomaly_results.to_csv(os.path.join(model_dir, 'anomaly_results.csv'), index=False)
        
        print(f"Model saved to {model_dir}/")


if __name__ == '__main__':
    # Load data from database
    conn = sqlite3.connect('data/yambda.db')
    multi_event = pd.read_sql('SELECT * FROM multi_event', conn)
    user_features = pd.read_sql('SELECT * FROM user_features', conn)
    track_features = pd.read_sql('SELECT * FROM track_features', conn)
    conn.close()
    
    # Load embeddings
    embeddings = pd.read_parquet('data/embeddings.parquet')
    
    print("="*60)
    print("MODULE 2: SONG CLUSTERING")
    print("="*60)
    
    # Song Clustering
    clustering = SongClustering(embeddings, multi_event)
    features = clustering.prepare_features(use_pca=True, n_components=10)
    cluster_labels, silhouette = clustering.train(features, n_clusters=5)
    cluster_analysis = clustering.analyze_clusters()
    clustering.save_model()
    
    print("\n" + "="*60)
    print("MODULE 3: COMPLETION RATE PREDICTION")
    print("="*60)
    
    # Completion Rate Prediction
    predictor = CompletionRatePredictor(multi_event, user_features, track_features, embeddings)
    X, y, feature_names = predictor.prepare_features(use_embeddings=True, n_pca_components=5)
    y_test, y_pred = predictor.train(X, y)
    feature_importance = predictor.get_feature_importance(feature_names)
    predictor.save_model()
    
    print("\n" + "="*60)
    print("MODULE 4: ANOMALY DETECTION")
    print("="*60)
    
    # Anomaly Detection
    detector = AnomalyDetector(multi_event, user_features)
    anomaly_features = detector.build_anomaly_features()
    anomaly_results = detector.train(anomaly_features, contamination=0.05)
    comparison = detector.analyze_anomalies()
    detector.save_model()
    
    # Save results to database
    conn = sqlite3.connect('data/yambda.db')
    
    # Save clustering results
    embeddings_with_cluster = embeddings.merge(
        clustering.embeddings[['item_id', 'cluster']], 
        on='item_id', 
        how='left'
    )
    embeddings_with_cluster[['item_id', 'cluster']].to_sql(
        'song_clusters', conn, if_exists='replace', index=False
    )
    
    if cluster_analysis is not None:
        cluster_analysis.to_sql('cluster_analysis', conn, if_exists='replace', index=False)
    
    # Save anomaly results
    anomaly_results[['uid', 'is_anomaly', 'anomaly_score']].to_sql(
        'user_anomalies', conn, if_exists='replace', index=False
    )
    
    conn.close()
    
    print("\n✓ All ML modules completed successfully!")
