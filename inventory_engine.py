import requests
import pandas as pd
import datetime

class RestockRadarEngine:
    def __init__(self, shop_url, access_token):
        self.shop_url = shop_url
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }

    def fetch_products_and_inventory(self):
        """Pulls all active products and their current stock levels from Shopify."""
        endpoint = f"https://{self.shop_url}/admin/api/2023-10/products.json?fields=id,title,variants"
        response = requests.get(endpoint, headers=self.headers)
        
        inventory_data = []
        if response.status_code == 200:
            products = response.json().get('products', [])
            for product in products:
                for variant in product['variants']:
                    inventory_data.append({
                        "SKU": variant.get('sku', f"Unknown-{variant['id']}"),
                        "Product Name": f"{product['title']} - {variant.get('title', '')}",
                        "Current Stock": variant.get('inventory_quantity', 0),
                        "Variant_ID": variant['id']
                    })
            return pd.DataFrame(inventory_data)
        return pd.DataFrame()

    def simulate_velocity_and_reorder(self, df, lead_time_days=14):
        """
        In a production app, you pull historical orders to calculate this. 
        For this MVP, we simulate daily sales velocity to generate the dashboard.
        """
        # Simulating data: Let's assume items sell between 1 and 5 units a day
        import numpy as np
        np.random.seed(42) 
        
        df['Daily Sales Velocity'] = np.random.randint(1, 6, df.shape[0])
        df['Safety Stock'] = df['Daily Sales Velocity'] * 3 # 3 days buffer
        
        # Reorder Point Formula: (Daily Sales * Lead Time) + Safety Stock
        df['Reorder Point'] = (df['Daily Sales Velocity'] * lead_time_days) + df['Safety Stock']
        
        # Calculate days until they hit zero
        df['Days Until Stockout'] = (df['Current Stock'] / df['Daily Sales Velocity']).round(1)
        
        # Action Flag
        df['Status'] = df.apply(lambda x: '🚨 ORDER NOW' if x['Current Stock'] <= x['Reorder Point'] else '✅ Healthy', axis=1)
        
        return df[['SKU', 'Product Name', 'Current Stock', 'Daily Sales Velocity', 'Reorder Point', 'Days Until Stockout', 'Status']]