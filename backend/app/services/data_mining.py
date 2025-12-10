import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, r2_score, silhouette_score
from scipy.stats import pearsonr, spearmanr
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import json


class DataMiningService:
    """Service for performing data mining and analytics operations"""

    def __init__(self, file_path: str):
        """Initialize with file path"""
        self.file_path = file_path
        self.df = None
        self._load_data()

    def _load_data(self):
        """Load data from file"""
        if self.file_path.endswith('.csv'):
            self.df = pd.read_csv(self.file_path)
        elif self.file_path.endswith(('.xlsx', '.xls')):
            self.df = pd.read_excel(self.file_path)
        else:
            raise ValueError("Unsupported file format")

    def get_columns_info(self) -> Dict[str, Any]:
        """Get information about columns in the dataset"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        return {
            "all_columns": self.df.columns.tolist(),
            "numeric_columns": numeric_cols,
            "categorical_columns": categorical_cols,
            "total_rows": len(self.df),
            "column_types": {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }

    def correlation_analysis(self, col1: str, col2: str) -> Dict[str, Any]:
        """Perform correlation analysis between two numeric columns"""
        # Remove missing values
        data = self.df[[col1, col2]].dropna()
        
        if len(data) < 2:
            raise ValueError("Not enough data points for correlation analysis")
        
        # Calculate Pearson correlation
        pearson_corr, pearson_p = pearsonr(data[col1], data[col2])
        
        # Calculate Spearman correlation
        spearman_corr, spearman_p = spearmanr(data[col1], data[col2])
        
        # Prepare scatter plot data
        scatter_data = [
            {"x": float(x), "y": float(y)} 
            for x, y in zip(data[col1].values[:1000], data[col2].values[:1000])  # Limit to 1000 points
        ]
        
        # Interpretation
        abs_corr = abs(pearson_corr)
        if abs_corr > 0.7:
            strength = "strong"
        elif abs_corr > 0.4:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if pearson_corr > 0 else "negative"
        
        return {
            "pearson_correlation": float(pearson_corr),
            "pearson_p_value": float(pearson_p),
            "spearman_correlation": float(spearman_corr),
            "spearman_p_value": float(spearman_p),
            "scatter_data": scatter_data,
            "interpretation": f"{strength.capitalize()} {direction} correlation",
            "sample_size": len(data)
        }

    def clustering_analysis(self, columns: List[str], n_clusters: int = 3) -> Dict[str, Any]:
        """Perform K-Means clustering"""
        # Prepare data
        data = self.df[columns].dropna()
        
        if len(data) < n_clusters:
            raise ValueError(f"Not enough data points for {n_clusters} clusters")
        
        # Standardize features
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_data)
        
        # Calculate silhouette score
        silhouette = silhouette_score(scaled_data, clusters)
        
        # Prepare visualization data (for 2D plot, use first 2 columns)
        if len(columns) >= 2:
            scatter_data = [
                {
                    "x": float(data.iloc[i, 0]),
                    "y": float(data.iloc[i, 1]),
                    "cluster": int(clusters[i])
                }
                for i in range(min(len(data), 1000))
            ]
        else:
            scatter_data = []
        
        # Cluster centers
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        
        return {
            "n_clusters": n_clusters,
            "cluster_labels": clusters.tolist()[:1000],  # Limit output
            "cluster_centers": centers.tolist(),
            "silhouette_score": float(silhouette),
            "scatter_data": scatter_data,
            "cluster_sizes": {int(i): int(np.sum(clusters == i)) for i in range(n_clusters)},
            "interpretation": f"Silhouette score: {silhouette:.2f} ({'good' if silhouette > 0.5 else 'fair' if silhouette > 0.25 else 'poor'} clustering)"
        }

    def classification_analysis(self, target_col: str, feature_cols: List[str], test_size: float = 0.2) -> Dict[str, Any]:
        """Perform classification analysis"""
        # Prepare data
        data = self.df[[target_col] + feature_cols].dropna()
        
        if len(data) < 10:
            raise ValueError("Not enough data for classification")
        
        X = data[feature_cols]
        y = data[target_col]
        
        # Encode target if categorical
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42
        )
        
        # Train model
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        return {
            "accuracy": float(accuracy),
            "confusion_matrix": conf_matrix.tolist(),
            "class_labels": le.classes_.tolist(),
            "feature_importance": {
                feature_cols[i]: float(abs(model.coef_[0][i])) 
                for i in range(len(feature_cols))
            } if len(model.coef_[0]) == len(feature_cols) else {},
            "test_size": len(y_test),
            "interpretation": f"Model accuracy: {accuracy:.2%}"
        }

    def regression_analysis(self, target_col: str, feature_cols: List[str], test_size: float = 0.2) -> Dict[str, Any]:
        """Perform linear regression analysis"""
        # Prepare data
        data = self.df[[target_col] + feature_cols].dropna()
        
        if len(data) < 10:
            raise ValueError("Not enough data for regression")
        
        X = data[feature_cols]
        y = data[target_col]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred = model.predict(X_test)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        
        # Prepare scatter data (actual vs predicted)
        scatter_data = [
            {"actual": float(y_test.iloc[i]), "predicted": float(y_pred[i])}
            for i in range(min(len(y_test), 500))
        ]
        
        return {
            "r2_score": float(r2),
            "coefficients": {
                feature_cols[i]: float(model.coef_[i]) 
                for i in range(len(feature_cols))
            },
            "intercept": float(model.intercept_),
            "scatter_data": scatter_data,
            "test_size": len(y_test),
            "interpretation": f"R² score: {r2:.2f} ({'good' if r2 > 0.7 else 'moderate' if r2 > 0.4 else 'poor'} fit)"
        }

    def descriptive_statistics(self, columns: List[str]) -> Dict[str, Any]:
        """Calculate descriptive statistics for columns"""
        results = {}
        
        for col in columns:
            col_data = self.df[col].dropna()
            
            if pd.api.types.is_numeric_dtype(col_data):
                # Numeric statistics
                results[col] = {
                    "type": "numeric",
                    "count": int(col_data.count()),
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "std": float(col_data.std()),
                    "min": float(col_data.min()),
                    "max": float(col_data.max()),
                    "q25": float(col_data.quantile(0.25)),
                    "q75": float(col_data.quantile(0.75)),
                    "histogram": self._get_histogram(col_data)
                }
            else:
                # Categorical statistics
                value_counts = col_data.value_counts()
                results[col] = {
                    "type": "categorical",
                    "count": int(col_data.count()),
                    "unique": int(col_data.nunique()),
                    "top": str(value_counts.index[0]) if len(value_counts) > 0 else None,
                    "freq": int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
                    "distribution": {
                        str(k): int(v) for k, v in value_counts.head(10).items()
                    }
                }
        
        return results

    def _get_histogram(self, data: pd.Series, bins: int = 20) -> List[Dict[str, float]]:
        """Generate histogram data"""
        counts, bin_edges = np.histogram(data, bins=bins)
        histogram = [
            {
                "bin_start": float(bin_edges[i]),
                "bin_end": float(bin_edges[i + 1]),
                "count": int(counts[i])
            }
            for i in range(len(counts))
        ]
        return histogram

    def association_rules_analysis(self, columns: List[str], min_support: float = 0.01) -> Dict[str, Any]:
        """Perform association rules mining (for categorical data)"""
        # Prepare transaction data
        data = self.df[columns].dropna()
        
        # Convert to transaction format
        transactions = []
        for _, row in data.iterrows():
            transaction = [f"{col}={val}" for col, val in row.items()]
            transactions.append(transaction)
        
        if len(transactions) < 10:
            raise ValueError("Not enough transactions for association rules")
        
        # Encode transactions
        te = TransactionEncoder()
        te_ary = te.fit(transactions).transform(transactions)
        df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        
        # Find frequent itemsets
        frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
        
        if len(frequent_itemsets) == 0:
            return {
                "frequent_itemsets": [],
                "rules": [],
                "interpretation": "No frequent patterns found. Try lowering min_support."
            }
        
        # Generate rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
        
        # Format results
        itemsets_list = [
            {
                "itemset": list(row['itemsets']),
                "support": float(row['support'])
            }
            for _, row in frequent_itemsets.head(20).iterrows()
        ]
        
        rules_list = [
            {
                "antecedent": list(row['antecedents']),
                "consequent": list(row['consequents']),
                "support": float(row['support']),
                "confidence": float(row['confidence']),
                "lift": float(row['lift'])
            }
            for _, row in rules.head(20).iterrows()
        ] if len(rules) > 0 else []
        
        return {
            "frequent_itemsets": itemsets_list,
            "rules": rules_list,
            "total_transactions": len(transactions),
            "interpretation": f"Found {len(frequent_itemsets)} frequent itemsets and {len(rules)} association rules"
        }
