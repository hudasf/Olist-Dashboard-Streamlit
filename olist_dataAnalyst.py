import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
import streamlit as st
import zipfile,os 
from babel.numbers import format_currency
from datetime import datetime

sns.set(style='dark')

# load dataframe
main_dir = 'https://raw.githubusercontent.com/hudasf/Olist-Dashboard-Streamlit/main/olist/' # ganti dengan alamat dataframe
cust_df = pd.read_csv(os.path.join(main_dir,'olist_customers_dataset.csv'))
# geo_df = pd.read_csv(os.path.join(main_dir,'olist_geolocation_dataset.csv'))
orderItems_df = pd.read_csv(os.path.join(main_dir,'olist_order_items_dataset.csv'))
orderPay_df = pd.read_csv(os.path.join(main_dir,'olist_order_payments_dataset.csv'))
orderRev_df = pd.read_csv(os.path.join(main_dir,'olist_order_reviews_dataset.csv'))
order_df = pd.read_csv(os.path.join(main_dir,'olist_orders_dataset.csv'))
product_df = pd.read_csv(os.path.join(main_dir,'olist_products_dataset.csv'))
seller_df = pd.read_csv(os.path.join(main_dir,'olist_sellers_dataset.csv'))
prodCat_df = pd.read_csv(os.path.join(main_dir,'product_category_name_translation.csv'))

print(order_df.describe(include="all"))

# Analisis terkait : Apa 10 produk terlaris sepanjang tahun 2018 ?

# gabungkan data frame untuk analisis
allorder_df = order_df.merge(
    orderItems_df,how="left",on="order_id").merge(
        product_df,how="left",on="product_id").merge(
            prodCat_df,how="left",on="product_category_name"
        )
# check isi df
print(allorder_df.head())
print(allorder_df.info())

# ubah kolom 'order_purchase_timestamp' ke datetime untuk ambil tahun 2018 saja
allorder_df['order_purchase_timestamp'] = pd.to_datetime(allorder_df['order_purchase_timestamp'])
allorder_df_2018 = allorder_df[allorder_df['order_purchase_timestamp'].dt.year == 2018]

# buat tabel pivot menampilkan 10 kategori produk terlaris & tidak diminati di 2018
mostSellingProd = allorder_df_2018.groupby(by="product_category_name_english").agg(Total_Order=('order_id', 'count'))
mostSellingProd = mostSellingProd.sort_values(by='Total_Order', ascending=False).head(10)
mostSellingProd = mostSellingProd.reset_index()
leastSellingProd = mostSellingProd.sort_values(by='Total_Order', ascending=True).head(10)
leastSellingProd = leastSellingProd.reset_index()

# Tambahkan Row Count
mostSellingProd.insert(0, 'No.', range(1, len(mostSellingProd) + 1))
leastSellingProd.insert(0, 'No.', range(1, len(leastSellingProd) + 1))
mostSellingProd = mostSellingProd.rename(columns={'product_category_name_english': 'Product Category Name'})
leastSellingProd = leastSellingProd.rename(columns={'product_category_name_english': 'Product Category Name'})


print("-=Most Selling Product Category in 2018=-\n",mostSellingProd.to_string(index=False))
print("-=Least Selling Product Category in 2018=-\n",leastSellingProd.to_string(index=False))

# Siapa customers yang paling banyak melakukan pembelian sepanjang tahun 2018 dan berapa jumlah transaksinya ?

# abungkan data frame untuk analisis
allorderCust_df = allorder_df_2018.merge(
    cust_df,how="left",on="customer_id").merge(
        orderPay_df,how="left",on="order_id"
    )

# check isi df
print(allorderCust_df.head())
print(allorderCust_df.info())

# buat tabel pivot
prominentCust = allorderCust_df.groupby(by="customer_id").agg(
    Total_Order = ('order_id', 'count'),
    Total_Spent = ('payment_value', 'sum')
)

# sorting berdasarkan pengeluaran
prominentCust = prominentCust.reset_index()
prominentCust = prominentCust.sort_values(by='Total_Spent', ascending=False)

# Tambahkan Row Count
prominentCust['No.'] = range(1, len(prominentCust) + 1)
prominentCust = prominentCust[['No.', 'customer_id', 'Total_Order', 'Total_Spent']]
prominentCust = prominentCust.head(10)

print(prominentCust.to_string(index=False))


# streamlit Dashboard

# set page title, icon serta layout
st.set_page_config(page_title="Olist Dashboard", page_icon=":bar_chart:", layout="centered")

# Buat Header halaman utama
current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
h1_content = "Dashboard OLIST E-Commerce"
h2_content = f"Time : {current_datetime}"
centered_content1 = f"<div style='text-align: center;'><h1>{h1_content}</h1></div>"
centered_content2 = f"<div style='text-align: center;'>{h2_content}</div>"
st.write(centered_content1, unsafe_allow_html=True)
st.write(centered_content2, unsafe_allow_html=True)
st.write(" ")

# Sidebar filter for date range dan logo perusahaan
st.sidebar.image("https://s3-us-west-2.amazonaws.com/cbi-image-service-prd/original/4b74afb1-5a08-411d-a791-5cee8af6be67.png?w=96")
date_range = st.sidebar.date_input("Filter Date Range", [allorderCust_df ['order_purchase_timestamp'].min(), allorderCust_df ['order_purchase_timestamp'].max()])
start_date, end_date = np.datetime64(date_range[0]), np.datetime64(date_range[1])

# Layout Segment 1 dengan 2 columns
col1, col2 = st.columns(2)
allorderCust_df = allorder_df.merge(
    cust_df,how="left",on="customer_id").merge(
        orderPay_df,how="left",on="order_id"
    )

# segment 1 column 1
with col1:
    # convert ke datetime pandas untuk ambil data berdasarkan filter sidebar
    allorderCust_df["order_purchase_timestamp"] = pd.to_datetime(allorderCust_df["order_purchase_timestamp"])
    filtered_df= allorderCust_df[(allorderCust_df['order_purchase_timestamp'] >= start_date) & (allorderCust_df['order_purchase_timestamp'] <= end_date)]
    
    # hitung order id unique pada dataframe
    totOrder = filtered_df['order_id'].nunique()
    st.write("### **Total Order :**")
    st.write(f"##        {totOrder}")

    #hitung payment_value pada dataframe
    totPayment = filtered_df.groupby('order_id')['payment_value'].sum().reset_index()
    totPaymentSum = totPayment['payment_value'].sum()
    totPaymentSum = '{:,.3f}'.format(totPaymentSum)
    st.write("### **Total Revenue :**")
    st.write(f"###      R$ {totPaymentSum}")

# segment 1 column 2
with col2:
    st.write("### **High Value Customer**")
    
    # convert ke datetime pandas untuk ambil data berdasarkan filter sidebar
    allorderCust_df["order_purchase_timestamp"] = pd.to_datetime(allorderCust_df["order_purchase_timestamp"])
    filteredPC_df= allorderCust_df[(allorderCust_df['order_purchase_timestamp'] >= start_date) & (allorderCust_df['order_purchase_timestamp'] <= end_date)]
    
    # grouping by customer_id atau nama_pelanggan jika ada
    filteredPC_df = filteredPC_df.groupby(by="customer_id").agg(
        Total_Order = ('order_id', 'count'),
        Total_Spent = ('payment_value', 'sum')
    )
    filteredPC_df = filteredPC_df.reset_index()
    filteredPC_df = filteredPC_df.sort_values(by='Total_Spent', ascending=False)

    # Tambahkan Row Count
    filteredPC_df['No.'] = range(1, len(filteredPC_df) + 1)
    filteredPC_df = filteredPC_df[['No.', 'customer_id', 'Total_Order', 'Total_Spent']]
    filteredPC_df.set_index('No.', inplace=True)  # Setting 'No' column as the index

    # tampilkan isi data frame ke table streamlit
    st.table(filteredPC_df.head())

# Segment 2 dengan 1 column
st.header("Olist Revenue Graph")

# Business Question : Perkembangan Revenue Olist perbulan
monthly_orders_df = allorderCust_df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id": "nunique",
    "payment_value": "sum"
})

# format ulang penamaan tanggal serta bulan lalu rename nama beberapa kolom
monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')
monthly_orders_df = monthly_orders_df.reset_index()
monthly_orders_df.rename(columns={
    "order_id": "order_count",
    "payment_value": "revenue"
}, inplace=True)

# buat plot line chart
fig, ax = plt.subplots(figsize=(15, 6))

monthly_orders_df["order_purchase_timestamp"] = pd.to_datetime(monthly_orders_df["order_purchase_timestamp"])
# Filter DataFrame berdasarkan selected date range
fmonthly_orders_df= monthly_orders_df[(monthly_orders_df['order_purchase_timestamp'] >= start_date) & 
                                      (monthly_orders_df['order_purchase_timestamp'] <= end_date)]

# buat plot diagram garis untuk grafik perkembangan revenue olist
ax.plot(
    fmonthly_orders_df["order_purchase_timestamp"],
    fmonthly_orders_df["revenue"],
    marker='o', 
    linewidth=2,
    color="#72BCD4"
)

# Format x axis untuk tampilkan nama bulan dan tahun saja
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

# Rotasi label x axis sebanyak 45 derajat agar terbaca dan tidak tabrakan
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)

# Set judul title dan label x axis
plt.title("Total Revenue per Month Olist", loc="center", fontsize=20)
plt.xlabel("Order Purchase Timestamp")

# tampilkan plot pada streamlit
st.pyplot(fig)


# Segment 3 dengan  1 column
st.header("Most and Least Selling Product")

# Filter DataFrame berdasarkan selected date range
allorder_df["order_purchase_timestamp"] = pd.to_datetime(allorder_df["order_purchase_timestamp"])
filteredProd_df= allorder_df[(allorder_df['order_purchase_timestamp'] >= start_date) & (allorder_df['order_purchase_timestamp'] <= end_date)]

# buat tabel pivot menampilkan 10 kategori produk terlaris sesuai filter
mostSellingProd = filteredProd_df.groupby(by="product_category_name_english").agg(Total_Order=('order_id', 'count'))
mostSellingProd = mostSellingProd.sort_values(by='Total_Order', ascending=False)
mostSellingProd = mostSellingProd.reset_index()
leastSellingProd = mostSellingProd.sort_values(by='Total_Order', ascending=True)
leastSellingProd = leastSellingProd.reset_index()

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(15, 6))
 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
# buat grafik bar chart
sns.barplot(x="Total_Order", y="product_category_name_english", data=mostSellingProd.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)
 
sns.barplot(x="Total_Order", y="product_category_name_english", data=leastSellingProd.sort_values(by="Total_Order", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)

# buat judul cetak plot ke streamlit
plt.suptitle("Most and Least Selling Product by Number of Order", fontsize=20)
st.pyplot(fig)

# Segment 4 dengan 1 column
st.header("Data Detail")
# Filter DataFrame berdasarkan selected date range
filtered_df= allorderCust_df[(allorderCust_df['order_purchase_timestamp'] >= start_date) & (allorderCust_df ['order_purchase_timestamp'] <= end_date)]
# buatkan multi select untuk memilih kolom apa saja yang ditampilkan
selected_columns = st.multiselect("Select columns to display", filtered_df.columns)
# buat settingan page dan jumlah paging hasil filter
page_size = 250 # tampilkan jumlah data pada tabel
num_pages = len(filtered_df) // page_size + 1

current_page = st.empty()
paginated_df = st.empty()

# Mengambil inputan halaman yang ingin ditampilkan
current_page_number = st.text_input("Go to Page", "1")
try:
    current_page_number = int(current_page_number) - 1
    current_page_number = max(0, min(current_page_number, num_pages - 1))  # Memastikan tetap pada jumlah halaman yang ada
except ValueError:
    current_page_number = 0  # Jika error, pasang default ke halaman awal

# Tampilkan textbox berisi halaman saat ini
start_idx = current_page_number * page_size
end_idx = min(start_idx + page_size, len(filtered_df))

# Menampilkan dataframe yang berisi data hasil pagination
paginated_df.table(filtered_df.iloc[start_idx:end_idx][selected_columns])
current_page.text(f"Displaying page {current_page_number + 1}/{num_pages}")

# Download button untuk filtered DataFrame
csv_data = filtered_df[selected_columns].to_csv(index=False).encode('utf-8')
st.download_button("Download Filtered Data", csv_data, "filtered_data.csv", "text/csv")

# menampilkan jumlah data yang berhasil difilter
st.info(f"Total data filtered: {len(filtered_df)} rows.")
