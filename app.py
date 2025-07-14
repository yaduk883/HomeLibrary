import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Your published Google Sheet (CSV export link)
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/gviz/tq?tqx=out:csv"

# Refresh button
refresh = st.button("🔄 Refresh Data")

@st.cache_data(ttl=600)
def load_data():
    try:
        response = requests.get(GOOGLE_SHEET_CSV)
        data = pd.read_csv(StringIO(response.text))
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

if refresh:
    st.cache_data.clear()

data = load_data()

# -----------------------------
# UI Starts Here
# -----------------------------
st.set_page_config(page_title="📚 Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

query = st.text_input("🔍 Search for a book:")

if not data.empty and query:
    # Filter results by any column
    results = data[data.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]

    st.write(f"🔎 Found {len(results)} result(s)")

    if not results.empty:
        # Hide Description column in main table
        display_columns = [col for col in results.columns if 'description' not in col.lower()]
        st.dataframe(results[display_columns])

        # Show each book's description below
        for _, row in results.iterrows():
            book_name = row.get('Name of Book', 'Unknown')
            description = row.get('Description', 'No description available.')
            st.markdown(f"### 📝 Description for *{book_name}*")
            st.write(description)
            st.markdown("---")
    else:
        st.warning("No matching books found.")
elif query:
    st.warning("No results found.")
elif not data.empty:
    st.info("Type in the search box above to search through the books.")
else:
    st.error("❌ Failed to load book data.")
