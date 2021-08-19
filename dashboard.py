import streamlit as st
import pandas as pd
import base64
import matplotlib
from matplotlib.figure import Figure
import seaborn as sns
import altair as alt
import datetime as dt
from streamlit_lottie import st_lottie
import requests

STARTING_BALANCE = 90754.08
CSV_TITLE = '2021-08-18_transaction_download.csv'
MONTHS_DONE = ['January', 'February', 'March', 'April','May', 'June','July','August']
st.set_page_config(page_title='Finance Dashboard', page_icon='💰')
st.sidebar.header('Display options')
month_dict = {'All' : 0, 'January': 1, 'February': 2, 'March' : 3, 'April' : 4, 'May': 5,'June': 6,'July' : 7, 'August' : 8, 'September' : 9 , 'October' : 10 , 'November' : 11, 'December' : 12}
months = list(month_dict.keys())
selected_month = st.sidebar.selectbox('Month', months)

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://assets10.lottiefiles.com/temporary_files/EGBZKv.json"
lottie_json = load_lottieurl(lottie_url)

col1, col2, col3 = st.beta_columns([8,1,2])

with col1:
    st.title('Technica Finance Dashboard')

with col2:
    st.write("")

with col3:
    st_lottie(lottie_json, speed=1, height=100)


def create_df():
    df = pd.read_csv(CSV_TITLE)
    df[['Debit', 'Credit']] = df[['Debit', 'Credit']].apply(pd.to_numeric)
    df = df.fillna(0)
    df['Credit/Debit'] = df['Credit'] - df['Debit']
    df = df.iloc[::-1]
    df['Resulting Balance'] = STARTING_BALANCE + df['Credit/Debit'].cumsum()
    df['Date'] = pd.to_datetime(df['Posted Date'])
    return df


def get_data(df, month):
    current_balance = df['Resulting Balance'].iloc[-1]
    last_updated = df['Date'].iloc[-1]
    if selected_month != "All":
        df = df[df['Date'].dt.month == month_dict[month]]
    df['Date'] = df['Date'].dt.date
    return df, current_balance, last_updated

df = create_df()
data, current_balance, last_updated = get_data(df, selected_month)
formatted_balance = "${:,.2f}".format(current_balance)
st.markdown(f"""
Use the pullout menu on the left to view our 2021 bank statements by month.
* **Foundation account balance:** $5,729.11
* **C1 account balance:** {formatted_balance}
* **Dashboard last updated:** {last_updated}
""")
st.header('Bank Account Transactions')
data.drop(['Account Number', 'Credit', 'Debit', 'Posted Date'], axis=1, inplace=True)
st.write(data)

st.header('Account History')
account_history = alt.Chart(df).mark_line().encode(
    x='Date',
    y='Resulting Balance'
).properties(width=600, height=400)
st.altair_chart(account_history)

st.header('Monthly Spending')
df = create_df()
df2 = df.groupby(df['Date'].dt.strftime('%B'))['Debit'].sum().sort_values().reset_index()
df3 = df.groupby(df['Date'].dt.strftime('%B'))['Credit'].sum().reset_index()
df2.columns = ['Month', 'Spending']
df3.columns = ['Month', 'Incoming']
df_combined = df2.merge(df3, on='Month')
fig = Figure()
ax = fig.subplots()
sns.barplot(x=df2['Month'],
            y=df2['Spending'], palette='Set3', order=MONTHS_DONE, ax=ax)
ax.set_xlabel('Month')
ax.set_ylabel('Total Spending')
st.pyplot(fig)
st.table(df_combined)


