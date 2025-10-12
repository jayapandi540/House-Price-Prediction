import streamlit as st
import pandas as pd
import os
from db_utils import create_listing, read_listings

st.set_page_config(page_title="🏠 Real Estate Portal", layout="wide")
st.title("🏡 Real Estate Management System")

menu = st.sidebar.radio("Navigation", ["🧾 Seller Portal", "👀 Buyer Portal"])

# ================= SELLER PORTAL =================
if menu == "🧾 Seller Portal":
    st.header("🧾 Seller: Add Property & Predict Price")

    with st.form("seller_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            area = st.number_input("Area (sqft)", 500, 10000, 2000, step=100)
            bedrooms = st.number_input("Bedrooms", 1, 10, 3, step=1)
            bathrooms = st.number_input("Bathrooms", 1, 5, 2, step=1)
            stories = st.number_input("Stories", 1, 4, 2, step=1)
        with col2:
            mainroad = st.selectbox("Main Road Access", ["Yes", "No"])
            guestroom = st.selectbox("Guest Room", ["Yes", "No"])
            basement = st.selectbox("Basement", ["Yes", "No"])
            hotwaterheating = st.selectbox("Hot Water Heating", ["Yes", "No"])
        with col3:
            airconditioning = st.selectbox("Air Conditioning", ["Yes", "No"])
            parking = st.number_input("Parking Spaces", 0, 5, 1, step=1)
            prefarea = st.selectbox("Preferred Area", ["Yes", "No"])
            furnishingstatus = st.selectbox("Furnishing Status", ["furnished", "semi-furnished", "unfurnished"])

        year_built = st.number_input("Year Built", 1900, 2025, 2015, step=1)
        description = st.text_area("Property Description", "")
        image_file = st.file_uploader("Upload Property Image", type=["jpg", "jpeg", "png"])

        submit_btn = st.form_submit_button("💾 Save Property")

        if submit_btn:
            data = {
                "area": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "stories": stories,
                "mainroad": mainroad,
                "guestroom": guestroom,
                "basement": basement,
                "hotwaterheating": hotwaterheating,
                "airconditioning": airconditioning,
                "parking": parking,
                "prefarea": prefarea,
                "furnishingstatus": furnishingstatus,
                "year_built": year_built,
                "description": description,
            }

            property_id = create_listing(data, image_file)
            if property_id:
                if data.get("price"):
                    st.success(f"✅ Property saved! Estimated Price: ₹{data['price']/1e7:.2f} Cr")
                else:
                    st.warning("Property saved, but price prediction failed.")
            else:
                st.error("❌ Failed to save property.")

# ================= BUYER PORTAL =================
elif menu == "👀 Buyer Portal":
    st.header("👀 Browse Properties")
    df = read_listings()
    if df.empty:
        st.warning("No listings found. Sellers need to add some first!")
    else:
        # Price filter slider
        min_price = int(df["price"].min()) if df["price"].min() > 0 else 0
        max_price = int(df["price"].max()) if df["price"].max() > 0 else 10000000
        price_range = st.sidebar.slider("Filter by Price (₹)", min_price, max_price, (min_price, max_price))

        filtered_df = df[(df["price"] >= price_range[0]) & (df["price"] <= price_range[1])]

        if filtered_df.empty:
            st.warning("No properties in this price range.")
        else:
            for _, row in filtered_df.iterrows():
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        img_path = row["image_path"] if row["image_path"] and os.path.exists(row["image_path"]) else "static/images/default.jpg"
                        st.image(img_path, use_container_width=True)
                    with col2:
                        price_in_cr = row["price"]/1e7 if row["price"] else 0
                        st.subheader(f"💰 ₹ {price_in_cr:,.2f} Cr")
                        st.markdown(f"🏠 {row['bedrooms']} BHK | {row['area']} sqft")
                        st.markdown(f"🛁 Bathrooms: {row['bathrooms']} | 🚗 Parking: {row['parking']}")
                        st.markdown(f"🌳 Main Road: {row['mainroad']} | 🛋 Guest Room: {row['guestroom']}")
                        st.markdown(f"🏗 Basement: {row['basement']} | ♨️ Hot Water Heating: {row['hotwaterheating']}")
                        st.markdown(f"❄️ Air Conditioning: {row['airconditioning']} | 📍 Preferred Area: {row['prefarea']}")
                        st.markdown(f"🪑 Furnishing: {row['furnishingstatus']}")
                        st.markdown(f"📆 Year Built: {row['year_built']}")
                        st.markdown(f"📝 {row['description']}")
                        st.divider()
