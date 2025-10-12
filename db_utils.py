import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import joblib
from config import DB_CONFIG, IMAGE_DIR

# Ensure image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)

# Load ML model once
MODEL = None
MODEL_PATH = "models/voting_regression.joblib"
if os.path.exists(MODEL_PATH):
    MODEL = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded from {MODEL_PATH}")
else:
    print("⚠️ Model not found. Price predictions will be skipped.")

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Database connection failed: {e}")
        return None

def prepare_features(data):
    """Preprocess input for model prediction."""
    df = pd.DataFrame([data])

    # Yes/No → 1/0
    for col in ['mainroad', 'guestroom', 'basement', 'hotwaterheating', 'airconditioning', 'prefarea']:
        df[col] = df[col].apply(lambda x: 1 if x == 'Yes' else 0)

    # One-hot furnishing status
    df = pd.concat([df, pd.get_dummies(df['furnishingstatus'], prefix='furnishingstatus')], axis=1)
    df.drop('furnishingstatus', axis=1, inplace=True)

    # Engineered features
    df['luxury_index'] = df.get('area', 0) * df.get('bedrooms', 0)
    df['price_per_sqft'] = df.get('area', 1)
    df['rooms_total'] = df.get('bedrooms', 0) + df.get('bathrooms', 0)
    df['parking_ratio'] = df.get('parking', 0) / df.get('area', 1)

    # Ensure all model columns exist and match order
    model_columns = MODEL.feature_names_in_.tolist() if MODEL else []
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[model_columns] if model_columns else df
    return df

def create_listing(data, image_file=None):
    """Insert property into DB with predicted price."""
    conn = get_db_connection()
    if conn is None:
        return None

    # Handle image
    image_path = None
    if image_file:
        ext = image_file.name.split('.')[-1].lower()
        filename = f"{int(pd.Timestamp.now().timestamp())}.{ext}"
        image_path = os.path.join(IMAGE_DIR, filename)
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())
    data['image_path'] = image_path

    # Predict price
    try:
        if MODEL:
            df_features = prepare_features(data)
            predicted_price = float(MODEL.predict(df_features)[0])
            print(f"DEBUG: Predicted price = {predicted_price}")
            data['price'] = predicted_price
        else:
            data['price'] = None
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        data['price'] = None

    sql = """INSERT INTO listings
        (price, area, bedrooms, bathrooms, stories, mainroad, guestroom, basement,
         hotwaterheating, airconditioning, parking, prefarea, furnishingstatus, year_built,
         description, image_path)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    vals = (
        data.get('price'), data.get('area'), data.get('bedrooms'), data.get('bathrooms'),
        data.get('stories'), data.get('mainroad'), data.get('guestroom'), data.get('basement'),
        data.get('hotwaterheating'), data.get('airconditioning'), data.get('parking'),
        data.get('prefarea'), data.get('furnishingstatus'), data.get('year_built'),
        data.get('description'), image_path
    )

    try:
        cursor = conn.cursor()
        print(f"DEBUG: Inserting property with price = {data['price']}")
        cursor.execute(sql, vals)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Insert failed: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def read_listings():
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        df = pd.read_sql("SELECT * FROM listings ORDER BY id DESC", conn)
        return df
    except Error as e:
        print(f"Read failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
