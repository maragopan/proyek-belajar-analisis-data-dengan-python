import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style="dark")

# create_daily_orders_df() digunakan untuk menyiapkan daily_orders_df


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_purchase_timestamp").agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)

    return daily_orders_df

# create_sum_order_items_df() bertanggung jawab untuk menyiapkan
# sum_orders_items_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_id").quantity.sum().sort_values(
        ascending=False).reset_index()
    return sum_order_items_df

# create_byzipcode_df() digunakan untuk menyiapkan byzipcode_df


def create_byzipcode_df(df):
    byzipcode_df = df.groupby(by="customer_zip_code_prefix").customer_unique_id.nunique().reset_index()
    byzipcode_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return byzipcode_df

# create_bycity_df() digunakan untuk menyiapkan bycity_df


def create_bycity_df(df):
    bycity_df = df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    bycity_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return bycity_df

# create_bystate_df() digunakan untuk menyiapkan bystate_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_unique_id": "customer_count"
    }, inplace=True)

    return bystate_df

# create_rfm_df(df) bertanggung jawab untuk menghaislkan rfm_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = [
        "customer_unique_id",
        "max_order_timestamp",
        "frequency",
        "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


dashboard_dataset3 = pd.read_csv("dashboard_dataset3.csv")

# Mengurutkan DataFrame berdasarkan order_purchase_timestamp
datetime_columns = ["order_purchase_timestamp"]
dashboard_dataset3.sort_values(by="order_purchase_timestamp", inplace=True)
dashboard_dataset3.reset_index(inplace=True)

for column in datetime_columns:
    dashboard_dataset3[column] = pd.to_datetime(dashboard_dataset3[column])

# Membuat filter dengan widget date input serta menambahkan logo
# perusahaan pada sidebar
min_date = dashboard_dataset3["order_purchase_timestamp"].min()
max_date = dashboard_dataset3["order_purchase_timestamp"].max()

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

# Membuat filter dashboard_dataset3
main_df = dashboard_dataset3[(dashboard_dataset3["order_purchase_timestamp"] >= str(start_date)) &
                          (dashboard_dataset3["order_purchase_timestamp"] <= str(end_date))]

# Menghasilkan berbagai DataFrame dari main_df untuk membuat visualisasi data
daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
byzipcode_df = create_byzipcode_df(main_df)
bycity_df = create_bycity_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

# Menambahkan header pada dashboard
st.header(":sparkles: Gopanpedia Dashboard :sparkles:")

# Menampilkan infomrasi terkait daily orders, yaitu jumlah order harian
# serta total order dan revenue dalam range waktu tertentu
st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "BRL ", locale="es_CO")
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)

# Menampilkan informasi tentang performa penjualan dari setiap produk
# (menampilkan 5 produk paling laris dan paling sedikit terjual)
st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35,15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="quantity", y="product_id", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

sns.barplot(x="quantity", y="product_id", data=sum_order_items_df.sort_values("quantity", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=35)
ax[1].tick_params(axis="x", labelsize=30)

st.pyplot(fig)

# Menampilkan demografi pelanggan
st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    data=byzipcode_df.sort_values(by="customer_count", ascending=False).head(5)

    sns.barplot(
        y="customer_count",
        x="customer_zip_code_prefix",
        data=data,
        palette=colors,
        ax=ax,
        order=data["customer_zip_code_prefix"]
    )
    ax.set_title("Number of Customer by Zip Code", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(20, 10))

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="customer_count",
        x="customer_city",
        data=bycity_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Number of Customer by City", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis="x", labelsize=35)
    ax.tick_params(axis="y", labelsize=30)
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", 
          "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",
          "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",
          "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",
          "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3",
          "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=15)
st.pyplot(fig)

# Menampilkan parameter RFM (Recency, Frequency, dan Monetary)
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3, = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL ", locale="es_CO")
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_unique_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis="y", labelsize=30)
ax[0].tick_params(axis="x", labelsize=35)

sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_unique_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)

sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_unique_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis="y", labelsize=30)
ax[2].tick_params(axis="x", labelsize=35)

st.pyplot(fig)

st.caption("Copyright (c) Gopanpedia 2023")