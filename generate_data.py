import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Configuration
num_rows = 200
start_date = datetime(2023, 10, 1)

# Base Data
categories = ['Tops', 'Bottoms', 'Ethnic Wear', 'Footwear', 'Accessories']
sizes = ['XS', 'S', 'M', 'L', 'XL']
colors = ['Navy Blue', 'White', 'Red', 'Black', 'Olive', 'Neon Green']
payment_methods = ['Cash', 'UPI', 'Card']
genders = ['Male', 'Female', 'Other']
age_groups = ['Teen (13-19)', 'Young Adult (20-30)', 'Adult (31-45)', 'Senior (46+)']
sections = ['Men', 'Women', 'Kids', 'Accessories']

# Products with base prices
products = {
    'Slim Fit Jeans': {'cat': 'Bottoms', 'price': 999, 'sec': 'Men'},
    'Floral Kurti': {'cat': 'Ethnic Wear', 'price': 799, 'sec': 'Women'},
    'Basic White T-Shirt': {'cat': 'Tops', 'price': 399, 'sec': 'Men'},
    'Running Shoes': {'cat': 'Footwear', 'price': 1499, 'sec': 'Men'},
    'Leather Belt': {'cat': 'Accessories', 'price': 299, 'sec': 'Accessories'},
    'Neon Green Cargo Pants': {'cat': 'Bottoms', 'price': 1899, 'sec': 'Men'}, # Slow seller
    'Party Wear Gown': {'cat': 'Ethnic Wear', 'price': 2499, 'sec': 'Women'},
    'Kids Denim Jacket': {'cat': 'Tops', 'price': 899, 'sec': 'Kids'},
    'Winter Beanie': {'cat': 'Accessories', 'price': 199, 'sec': 'Accessories'},
    'Oversized Hoodie': {'cat': 'Tops', 'price': 1199, 'sec': 'Women'},
}

def generate_sale(sale_id, current_date):
    day_of_week = current_date.strftime('%A')
    
    # Introduce problems:
    # 1. Tuesday is very slow (low probability of generating a row, but we enforce this by adjusting dates)
    # This logic just assigns dates. We'll make Tuesdays less frequent when assigning dates.
    
    # Select product
    # Make some products popular and others slow
    product_weights = [15, 15, 20, 10, 8, 1, 5, 8, 2, 16] # Neon Green Cargo Pants has weight 1 (slow)
    prod_name = random.choices(list(products.keys()), weights=product_weights)[0]
    prod_info = products[prod_name]
    
    # Select size
    # Size M keeps running out (sells a lot), XS barely moves
    size_weights = [1, 10, 40, 30, 19] # XS, S, M, L, XL
    size = random.choices(sizes, weights=size_weights)[0]
    
    color = random.choice(colors)
    if prod_name == 'Neon Green Cargo Pants':
        color = 'Neon Green'
    
    # Quantity
    quantity = random.choices([1, 2, 3], weights=[80, 15, 5])[0]
    
    # Discount
    # Discount section that barely makes money: high discount on cheap items
    discount = 0
    if prod_name in ['Winter Beanie', 'Leather Belt']:
        discount = random.choices([30, 50], weights=[20, 80])[0]
    else:
        discount = random.choices([0, 10, 20], weights=[70, 20, 10])[0]
    
    price = prod_info['price']
    total_amount = round((price * quantity) * (1 - discount/100))
    
    payment = random.choice(payment_methods)
    gender = random.choices(genders, weights=[45, 50, 5])[0]
    
    # Interesting pattern: Teenage girls buying mostly accessories
    if prod_info['sec'] == 'Accessories' and gender == 'Female':
        age_group = 'Teen (13-19)'
    else:
        age_group = random.choice(age_groups)
    
    # Interesting pattern: Adult men buying plain-coloured bottoms
    if prod_info['cat'] == 'Bottoms' and prod_info['sec'] == 'Men' and color in ['Navy Blue', 'Black']:
        age_group = 'Adult (31-45)'
        gender = 'Male'
        
    return {
        'sale_id': f'S{sale_id:03d}',
        'date': current_date.strftime('%Y-%m-%d'),
        'day_of_week': day_of_week,
        'product_name': prod_name,
        'category': prod_info['cat'],
        'size': size,
        'color': color,
        'quantity_sold': quantity,
        'price (Rs.)': price,
        'discount (%)': discount,
        'total_amount (Rs.)': total_amount,
        'payment_method': payment,
        'customer_gender': gender,
        'age_group': age_group,
        'store_section': prod_info['sec']
    }

data = []
current_date = start_date

# Generate 200 rows with specific day distributions
for i in range(1, num_rows + 1):
    # Skip some Tuesdays to make it slow
    while True:
        if current_date.strftime('%A') == 'Tuesday' and random.random() > 0.1:
            current_date += timedelta(days=1)
            continue
        break
        
    data.append(generate_sale(i, current_date))
    
    # Randomly advance the date to simulate days passing, clustering sales on weekends
    if current_date.strftime('%A') in ['Saturday', 'Sunday']:
        if random.random() > 0.6:
            current_date += timedelta(days=1)
    else:
        if random.random() > 0.3:
            current_date += timedelta(days=1)

with open('sales_data.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print("sales_data.csv created successfully with", len(data), "rows.")
