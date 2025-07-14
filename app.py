import streamlit as st
import pandas as pd
import requests
from io import StringIO

# ------------------------------------------
# Google Sheet CSV Link
# ------------------------------------------
GOOGLE_SHEET_CSV = "https://docs.google.com/spreadsheets/d/10foSwd8HyCbltVFYT5HpuiiQMk9FFIkn-aVhH93_A78/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=600)
def load_data():
    try:
        response = requests.get(GOOGLE_SHEET_CSV)
        df = pd.read_csv(StringIO(response.text))
        df.columns = df.columns.str.strip()
        df = df[df['Name of Book'].notna()]
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

# Columns to display
display_columns = [
    'Name of Book', 'Author', 'Language', 'N.o of Copies',
    'Date', 'BAR CODE', 'Available/Not', 'Checked Out By'
]

# Remove unwanted columns like "Sl No"
if 'Sl No' in book_data.columns:
    book_data.drop(columns=['Sl No'], inplace=True)

# ------------------------------------------
# Live Substring Search (NOT fuzzy)
# ------------------------------------------
query = st.text_input("🔍 Search by Book Name or Author:", placeholder="Type to search...")

if query:
    query_lower = query.lower()
    filtered = book_data[
        book_data['Name of Book'].str.lower().str.contains(query_lower, na=False) |
        book_data['Author'].str.lower().str.contains(query_lower, na=False)
    ]
else:
    filtered = pd.DataFrame()

# ------------------------------------------
# Display Results
# ------------------------------------------
if not filtered.empty:
    st.success(f"🔎 {len(filtered)} match(es) found.")
    show_cols = [col for col in display_columns if col in filtered.columns]
    st.dataframe(filtered[show_cols], use_container_width=True)

    selected_book = st.selectbox("📘 Select a book to view description", filtered['Name of Book'].dropna().unique())

    if selected_book and 'Description' in filtered.columns:
        desc = filtered.loc[filtered['Name of Book'].str.strip() == selected_book.strip(), 'Description'].values
        st.markdown(f"### 📝 Description for *{selected_book}*")
        st.write(desc[0] if len(desc) > 0 and pd.notna(desc[0]) else "No description available.")
else:
    if query:
        st.warning("❌ No matches found.")
    else:
        st.info("Start typing above to search by Book Name or Author.")
