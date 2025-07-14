import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ------------------------------------------
# Google Sheets CSV links (Make sure "Anyone with the link" can view)
# ------------------------------------------
GOOGLE_SHEET_CSV_MAIN = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?tqx=out:csv"
GOOGLE_SHEET_CSV_DETAILS = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?gid=0&format=csv"  # Replace gid=0 with the actual sheet/tab ID for details

# ------------------------------------------
# Load Data with Caching
# ------------------------------------------
@st.cache_data
def load_data():
    try:
        # Load main book list
        main_response = requests.get(GOOGLE_SHEET_CSV_MAIN)
        book_data = pd.read_csv(StringIO(main_response.text))
        book_data.columns = book_data.columns.str.strip()

        # Load book details
        details_response = requests.get(GOOGLE_SHEET_CSV_DETAILS)
        book_details = pd.read_csv(StringIO(details_response.text))
        book_details.columns = book_details.columns.str.strip()

        return book_data, book_details

    except Exception as e:
        st.error(f"⚠️ Failed to load book data: {e}")
        return pd.DataFrame(), pd.DataFrame()

# ------------------------------------------
# Main App
# ------------------------------------------
st.set_page_config(page_title="📚 Yadu's Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

# Load data
book_data, book_details = load_data()

# Debug: Show column names (optional)
# st.write("Book Data Columns:", book_data.columns.tolist())
# st.write("Book Details Columns:", book_details.columns.tolist())

# Search bar
query = st.text_input("🔍 Search for a book:")

if not book_data.empty and query:
    # Filter matching rows
    results = book_data[
        book_data.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    ]
    st.write(f"🔎 Found {len(results)} result(s)")
    st.dataframe(results)

    if not results.empty:
        # Make sure column exists
        name_col = "Name of Book"
        if name_col in results.columns:
            selected_book = st.selectbox("📘 Select a book to view details", results[name_col].dropna().unique())

            if selected_book:
                # Try to display description from details sheet
                if name_col in book_details.columns and 'Description' in book_details.columns:
                    match = book_details[
                        book_details[name_col].str.strip() == selected_book.strip()
                    ]['Description'].values

                    st.markdown(f"### 📝 Description for *{selected_book}*")
                    st.write(match[0] if len(match) > 0 else "No description available.")
                else:
                    st.warning("⚠️ Could not find description column in book details.")
        else:
            st.warning("⚠️ 'Name of Book' column not found in search results.")
else:
    st.info("Type in the search box above to find books.")
