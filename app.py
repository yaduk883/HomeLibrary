import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ------------------------------------------
# Google Sheet CSV link (only one sheet)
# ------------------------------------------
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?tqx=out:csv"

# ------------------------------------------
# Load Data with Caching
# ------------------------------------------
@st.cache_data(ttl=600)
def load_data():
    try:
        response = requests.get(GOOGLE_SHEET_CSV)
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()  # Clean column names
        return df
    except Exception as e:
        st.error(f"⚠️ Failed to load book data: {e}")
        return pd.DataFrame()

# ------------------------------------------
# Streamlit App
# ------------------------------------------
st.set_page_config(page_title="📚 Yadu's Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

book_data = load_data()

# ------------------------------------------
# Search Interface
# ------------------------------------------
query = st.text_input("🔍 Search for a book:")

if not book_data.empty and query:
    # Remove "Sl No" column if exists
    if 'Sl No' in book_data.columns:
        book_data = book_data.drop(columns=['Sl No'])

    # Filter rows that match or closely match
    results = book_data[
        book_data.apply(lambda row: row.astype(str).str.contains(query, case=False, na=False), axis=1)
    ]

    if not results.empty:
        st.write(f"🔎 Found {len(results)} matching result(s)")

        # Don't show Description column in table
        columns_to_show = [col for col in results.columns if col.lower() != 'description']
        st.dataframe(results[columns_to_show])

        # Show description separately
        name_col = "Name of Book"
        if name_col in results.columns:
            selected_book = st.selectbox("📘 Select a book to view description", results[name_col].dropna().unique())
            if selected_book:
                match = results[results[name_col].str.strip() == selected_book.strip()]
                if not match.empty and 'Description' in match.columns:
                    description = match.iloc[0]['Description']
                    st.markdown(f"### 📝 Description for *{selected_book}*")
                    st.write(description if pd.notna(description) and str(description).strip() else "No description available.")
                else:
                    st.warning("⚠️ Description not found.")
    else:
        st.warning("❌ No matching results found.")
else:
    st.info("Start typing above to search your library.")
