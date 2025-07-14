import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# ------------------------------------------
# Google Sheet CSV Link (must be public)
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
        st.error(f"⚠️ Failed to load data: {e}")
        return pd.DataFrame()

# ------------------------------------------
# App Start
# ------------------------------------------
st.set_page_config(page_title="📚 Yadu's Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

book_data = load_data()

# Columns to show in the table
display_columns = [
    'Name of Book', 'Author', 'Language', 'N.o of Copies',
    'Date', 'BAR CODE', 'Available/Not', 'Checked Out By'
]

# Drop irrelevant columns (e.g., Sl No)
for col in ['Sl No']:
    if col in book_data.columns:
        book_data.drop(columns=col, inplace=True)

# ------------------------------------------
# Live Fuzzy Search
# ------------------------------------------
query = st.text_input("🔍 Search by Book Name or Author:", placeholder="Start typing...")

def fuzzy_filter(df, query):
    if not query:
        return pd.DataFrame()

    combined = df['Name of Book'].astype(str) + " " + df['Author'].astype(str)
    matches = get_close_matches(query, combined, n=15, cutoff=0.4)
    return df[combined.isin(matches)]

filtered = fuzzy_filter(book_data, query)

if not filtered.empty:
    st.success(f"🔎 {len(filtered)} match(es) found.")

    # Show only the required columns
    available_cols = [col for col in display_columns if col in filtered.columns]
    st.dataframe(filtered[available_cols], use_container_width=True)

    # Select a book to show its description
    selected_book = st.selectbox("📘 Select a book to view description", filtered['Name of Book'].dropna().unique())

    if selected_book and 'Description' in filtered.columns:
        desc = filtered.loc[filtered['Name of Book'].str.strip() == selected_book.strip(), 'Description'].values
        st.markdown(f"### 📝 Description for *{selected_book}*")
        st.write(desc[0] if len(desc) > 0 and pd.notna(desc[0]) else "No description available.")
else:
    if query:
        st.warning("❌ No close matches found.")
    else:
        st.info("Start typing to search the book library.")
