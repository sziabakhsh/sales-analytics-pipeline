import pandas as pd
import random
from datetime import datetime,timedelta

rec_no = 1000
cities = [
    "Vancouver", "Toronto", "Calgary",
    "Montreal", "Ottawa", "Edmonton",
    "Winnipeg", "Halifax"
]
customers = [f"Customer_{i}" for i in range(1, 101)]

start_date = datetime(2024,1,1)
data=[]

for i in range(1,rec_no+1):
    order_date = start_date + timedelta(days=random.randint(1,365))
    
    row = {
        "order_id": i,
        "date": order_date.strftime("%Y-%m-%d"),
        "customer": random.choice(customers),
        "city": random.choice(cities),
        "amount": round(random.uniform(20, 500), 2)
    }

    data.append(row)

df=pd.DataFrame(data)

df.to_csv('orders.csv',index=False)


print("Dataset with 1000 records created successfully!")