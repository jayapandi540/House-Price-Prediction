# model_utils.py
import os
import joblib
import pandas as pd
from config import MODEL_PATH

# Load model once
MODEL = None
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)

def prepare_features(data):
    """Prepare features for ML prediction"""
    df = pd.DataFrame([data])

    # Convert Yes/No to 1/0
    for col in ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']:
        df[col] = df[col].apply(lambda x: 1 if x in [1, 'Yes', True] else 0)

    # One-hot encoding for furnishingstatus
    df = pd.concat([df, pd.get_dummies(df['furnishingstatus'], prefix='furnishingstatus')], axis=1)
    df.drop('furnishingstatus', axis=1, inplace=True)

    # Engineered features expected by the model
    df['luxury_index'] = df.get('area', 0) * df.get('bedrooms', 0)
    df['price_per_sqft'] = 0
    df['rooms_total'] = df.get('bedrooms', 0) + df.get('bathrooms', 0)
    df['parking_ratio'] = df.get('parking', 0) / max(df.get('area', 1), 1)

    # Ensure all required columns exist
    model_columns = ['area', 'bedrooms', 'bathrooms', 'stories', 'parking',
                     'mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning',
                     'prefarea', 'furnishingstatus_furnished', 'furnishingstatus_semi-furnished',
                     'furnishingstatus_unfurnished', 'luxury_index', 'price_per_sqft', 'rooms_total', 'parking_ratio']
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[model_columns]
    return df

def predict_price(data):
    if MODEL is None:
        return None
    try:
        df_features = prepare_features(data)
        return float(MODEL.predict(df_features)[0])
    except Exception as e:
        print(f"Prediction failed: {e}")
        return None
