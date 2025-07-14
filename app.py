import streamlit as st
import pandas as pd
import requests
from io import StringIO

# Google Sheets CSV links
GOOGLE_SHEET_CSV_MAIN = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?tqx=out:csv"
GOOGLE_SHEET_CSV_DETAILS = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?gid=123456789&format=csv"

@st.cache_data
def load_data():
    try:
        # Load main book list
        main_response = requests.get(GOOGLE_SHEET_CSV_MAIN)
        book_data = pd.read_csv(StringIO(main_response.text))
        book_data.columns = book_data.columns.str.strip()

        # Load book details (like descriptions)
        details_response = requests.get(GOOGLE_SHEET_CSV_DETAILS)
        book_details = pd.read_csv(StringIO(details_response.text))
        book_details.columns = book_details.columns.str.strip()

        return book_data, book_details

    except Exception as e:
        st.error(f"Failed to load book data: {e}")
        return pd.DataFrame(), pd.DataFrame()

book_data, book_details = load_data()

st.title("📚 Yadu's Book Library")

# Search bar
query = st.text_input("🔍 Search for a book:")

# Filter and display
if not book_data.empty and query:
    results = book_data[
        book_data.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)
    ]
    st.write(f"🔎 Found {len(results)} result(s)")
    st.dataframe(results)

    if not results.empty and "Name of Book" in results.columns:
        selected_book = st.selectbox("📘 Select a book to view details", results["Name of Book"].dropna().unique())

        if selected_book and 'Name of Book' in book_details.columns and 'Description' in book_details.columns:
            desc_match = book_details.loc[
                book_details['Name of Book'].str.strip() == selected_book.strip(), 'Description'
            ].values

            st.markdown(f"### 📝 Description for *{selected_book}*")
            st.write(desc_match[0] if len(desc_match) > 0 else "No description available.")
        else:
            st.warning("Could not find book description.")
else:
    st.info("Type in the search box above to find books.")
