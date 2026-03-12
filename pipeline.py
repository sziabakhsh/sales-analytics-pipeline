import pandas as pd
import json
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

sns.set(style="whitegrid")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 1️⃣ Configuration
def load_config():
    with open("config/config.json") as f:
        config = json.load(f)
    return config

# 2️⃣ Logging Setup
logger = None
def setup_logger(log_file):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# 3️⃣ Load Data
def load_data(path, logger):
    logger.info("Loading dataset")
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.to_period('M')
    return df

# 4️⃣ Data Validation
def check_data_quality(df, logger):
    logger.info(f"\n=== Data Info ===\n{df.info()}")
    logger.info(f"\n=== Statistical Summary ===\n{df.describe()}")
    logger.warning(f"\n=== Missing Values ===\n{df.isnull().sum()}")

# 5️⃣ Data Cleaning
def clean_data(df, logger):
    initial_rows = len(df)
    logger.info(f"Initial rows: {initial_rows}")

    df = df.dropna(subset=["amount", "city", "customer", "date"])
    df = df.drop_duplicates()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=["amount", "date"])
    df = df[df['amount'] > 0]
    df = df[df['city'].str.strip() != ""]
    df = df[df['customer'].str.strip() != ""]
    df = df.sort_values(by="date").reset_index(drop=True)

    logger.info(f"Rows after cleaning: {len(df)}")
    logger.info("Data cleaning completed successfully")
    return df

# 6️⃣ Shared Metrics
def compute_shared_metrics(df, logger):
    total_sales = df['amount'].sum()
    avg_order = df['amount'].mean()
    total_orders = len(df)
    unique_customers = df['customer'].nunique()
    unique_cities = df['city'].nunique()

    sales_by_city = (
        df.groupby('city', as_index=False)['amount']
        .sum()
        .rename(columns={'amount':'total_amount'})
        .sort_values(by='total_amount', ascending=False)
    )
    orders_by_customer = (
        df.groupby('customer', as_index=False)['amount']
        .sum()
        .rename(columns={'amount':'total_amount'})
        .sort_values(by='total_amount', ascending=False)
    )
    monthly_sales = (
        df.groupby('month', as_index=False)['amount']
        .sum()
        .rename(columns={'amount':'total_amount'})
        .sort_values(by='month', ascending=True)
    )

    metrics = {
        "total_sales": total_sales,
        "avg_order": avg_order,
        "total_orders": total_orders,
        "unique_customers": unique_customers,
        "unique_cities": unique_cities,
        "sales_by_city": sales_by_city,
        "orders_by_customer": orders_by_customer,
        "monthly_sales": monthly_sales
    }

    logger.info("Shared metrics computed successfully")
    return metrics

# 7️⃣ Visualization
def show_order_distribution(df, logger, figures_path):
    logger.info("Plotting order amount distribution")
    plt.figure(figsize=(8,5))
    sns.histplot(df['amount'], bins=30, kde=True, color='skyblue')
    plt.title("Order Amount Distribution")
    plt.xlabel("Order Amount")
    plt.ylabel("Count")
    plt.savefig(f"{figures_path}/AmountDistribution_{timestamp}.png")
    plt.show()
    logger.info("Amount Distribution chart saved")

def show_sales_by_city(df, logger, figures_path):
    plt.figure(figsize=(8,5))
    sns.barplot(data=df, x='city', y='total_amount', color="purple")
    plt.title("Sales by City")
    plt.xlabel("City")
    plt.ylabel("Total Sales")
    plt.savefig(f"{figures_path}/SalesByCity_{timestamp}.png")
    plt.show()
    logger.info("Sales by City chart saved")

def show_monthly_sales_trend(df, logger, figures_path):
    plt.figure(figsize=(8,5))
    df['month'] = df['month'].astype(str)
    sns.lineplot(data=df, x='month', y='total_amount', marker='o', color='orange')
    plt.title("Monthly Sales Trend")
    plt.xlabel("Month")
    plt.ylabel("Total Sales")
    plt.savefig(f"{figures_path}/MonthlySalesTrend_{timestamp}.png")
    plt.show()
    logger.info("Monthly Sales Trend chart saved")

def show_top_customers(df, logger, figures_path, top_n=5):
    plt.figure(figsize=(8,5))
    sns.barplot(data=df.head(top_n), x='customer', y='total_amount', color="green")
    plt.title(f"Top {top_n} Customers by Sales")
    plt.xlabel("Customer")
    plt.ylabel("Total Sales")
    plt.savefig(f"{figures_path}/TopCustomers_{timestamp}.png")
    plt.show()
    logger.info("Top Customers chart saved")

# 8️⃣ Main Pipeline
def main():
    config = load_config()
    global logger
    logger = setup_logger(config["log_file"])

    logger.info("Pipeline started")

    df = load_data(config["data_file"], logger)
    check_data_quality(df, logger)
    df_clean = clean_data(df, logger)

    metrics = compute_shared_metrics(df_clean, logger)

    # Create figures folder if not exists
    os.makedirs(config["figures_path"], exist_ok=True)

    show_order_distribution(df_clean, logger, config["figures_path"])
    show_sales_by_city(metrics['sales_by_city'], logger, config["figures_path"])
    show_monthly_sales_trend(metrics['monthly_sales'], logger, config["figures_path"])
    show_top_customers(metrics['orders_by_customer'], logger, config["figures_path"])

    logger.info("Pipeline finished")

if __name__ == "__main__":
    main()