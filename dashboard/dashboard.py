import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

# create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_date").agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)

    return daily_orders_df







































































all_dataset = pd.read_csv("all_dataset.csv")

# Mengurutkan DataFrame berdasarkan order_purchase_timestamp
datetime_columns = ["order_purchase_timestamp"]
all_dataset.sort_values(by="order_purchase_timestamp", inplace=True)
all_dataset.reset_index(inplace=True)

for column in datetime_columns:
    all_dataset[column] = pd.to_datetime(all_dataset[column])

# Membuat filter dengan widget date input serta menambahkan logo
# perusahaan pada sidebar
min_date = all_dataset["order_purchase_timestamp"].min()
max_date = all_dataset["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://raw.githubusercontent.com/maragopan/Irvan-Achmad-Ashari/master/github-mark.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu", 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Membuat filter all_dataset
main_df = all_dataset[(all_dataset["order_purchase_timestamp"] >= str(start_date)) &
                          (all_dataset["order_purchase_timestamp"] <= str(end_date))]

# Menghasilkan berbagai DataFrame dari main_df untuk membuat visualisasi data
daily_orders_df = create_daily_orders_df(main_df)