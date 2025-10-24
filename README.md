# 🏡 Real Estate App (Streamlit + MySQL + ML)

## 🚀 Setup
1. Create a MySQL DB called `real_estate`
2. Import `real_estate/listings.sql` into phpMyAdmin
3. Place your trained model in `models/model.pkl`

4. SQL query:

   ```bash
   CREATE TABLE IF NOT EXISTS listings (
    id INT NOT NULL PRIMARY KEY,
    price DOUBLE NOT NULL DEFAULT 0,
    area DOUBLE NOT NULL,
    bedrooms INT NOT NULL,
    bathrooms INT NOT NULL,
    stories INT NOT NULL,
    mainroad ENUM('Yes','No') NOT NULL,
    guestroom ENUM('Yes','No') NOT NULL,
    basement ENUM('Yes','No') NOT NULL,
    hotwaterheating ENUM('Yes','No') NOT NULL,
    airconditioning ENUM('Yes','No') NOT NULL,
    parking INT NOT NULL,
    prefarea ENUM('Yes','No') NOT NULL,
    furnishingstatus ENUM('furnished','semi-furnished','unfurnished') NOT NULL,
    year_built INT NOT NULL,
    description TEXT,
    image_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );

5. Run:

   ```bash
      pip install -r requirements.txt
      streamlit run app.py