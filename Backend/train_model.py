from ucimlrepo import fetch_ucirepo
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
import joblib
import numpy as np

print("Loading dataset...")
forest_fires = fetch_ucirepo(id=162)
X = forest_fires.data.features
y = forest_fires.data.targets

# Use ALL relevant features including FWI indices
# FWI indices are designed specifically for fire prediction
all_features = ['FFMC', 'DMC', 'DC', 'ISI', 'temp', 'RH', 'wind', 'rain']
X_all = X[all_features]

# Binary classification: Fire Risk or No Risk
y_binary = (y['area'] > 0).astype(int)

print(f"Total samples: {len(y_binary)}")
print(f"Fire events: {y_binary.sum()} ({y_binary.sum()/len(y_binary)*100:.1f}%)")
print(f"No fire events: {(1-y_binary).sum()} ({(1-y_binary).sum()/len(y_binary)*100:.1f}%)")

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X_all, y_binary, test_size=0.2, random_state=42, stratify=y_binary
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\n" + "="*60)
print("Testing Multiple Models...")
print("="*60)

models = {
    'Random Forest': RandomForestClassifier(
        n_estimators=300,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight='balanced',
        random_state=42
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    ),
    'XGBoost': XGBClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=6,
        scale_pos_weight=2,
        random_state=42
    )
}

best_model = None
best_score = 0
best_name = ""

for name, model in models.items():
    print(f"\nTraining {name}...")
    model.fit(X_train_scaled, y_train)
    
    # Test accuracy
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    cv_mean = cv_scores.mean()
    
    print(f"  Train Accuracy: {train_score:.2%}")
    print(f"  Test Accuracy: {test_score:.2%}")
    print(f"  Cross-Val Accuracy: {cv_mean:.2%} (+/- {cv_scores.std():.2%})")
    
    if test_score > best_score:
        best_score = test_score
        best_model = model
        best_name = name

print("\n" + "="*60)
print(f"Best Model: {best_name} with {best_score:.2%} accuracy")
print("="*60)

# Feature importance
if hasattr(best_model, 'feature_importances_'):
    feature_importance = pd.DataFrame({
        'feature': all_features,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance.to_string(index=False))

# Save best model
print("\nSaving model...")
joblib.dump(best_model, 'models/fire_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')

# Save feature list for API
with open('models/features.txt', 'w') as f:
    f.write(','.join(all_features))

print("\n✅ Model trained and saved successfully!")
print(f"Model expects input: {all_features}")
