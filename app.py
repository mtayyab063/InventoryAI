import streamlit as st
from inventory_engine import RestockRadarEngine

st.set_page_config(page_title="RestockRadar", layout="wide")

st.title("📡 RestockRadar: Inventory Optimizer")
st.markdown("Never lose revenue to stockouts again. Connect your Shopify store to see exactly what to order today.")

st.sidebar.header("Connect Your Store")
shop_url = st.sidebar.text_input("Shopify Store URL (e.g., mystore.myshopify.com)")
access_token = st.sidebar.text_input("Shopify Admin API Token", type="password")
lead_time = st.sidebar.slider("Supplier Lead Time (Days)", min_value=1, max_value=60, value=14)

if st.sidebar.button("Run Optimizer"):
    if not shop_url or not access_token:
        st.error("Please enter your Shopify URL and API Token.")
    else:
        with st.spinner("Syncing with Shopify and crunching data..."):
            engine = RestockRadarEngine(shop_url, access_token)
            
            # Fetch and process data
            raw_inventory = engine.fetch_products_and_inventory()
            
            if not raw_inventory.empty:
                optimized_data = engine.simulate_velocity_and_reorder(raw_inventory, lead_time_days=lead_time)
                
                # Split data for the UI
                action_required = optimized_data[optimized_data['Status'] == '🚨 ORDER NOW']
                healthy = optimized_data[optimized_data['Status'] == '✅ Healthy']
                
                st.subheader("⚠️ Urgent Reorder List")
                if not action_required.empty:
                    st.dataframe(action_required.style.highlight_max(axis=0))
                else:
                    st.success("All inventory is looking healthy! No urgent orders needed.")
                
                st.subheader("📦 Full Inventory Status")
                st.dataframe(optimized_data)
                
            else:
                st.error("Failed to fetch data. Please check your URL and Token.")