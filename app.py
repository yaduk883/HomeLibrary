import streamlit as st
import pandas as pd
import requests
from io import StringIO
from difflib import get_close_matches

# -------------------------------
# Google Sheet CSV Link
# -------------------------------
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

# ---------------------------------
# Main App Layout
# ---------------------------------
st.set_page_config(page_title="📚 Yadu's Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

book_data = load_data()

# Drop unwanted columns
if 'Sl No' in book_data.columns:
    book_data.drop(columns=['Sl No'], inplace=True)

# --------------------------
# Search Input
# --------------------------
query = st.text_input("🔍 Search for Book or Author (live fuzzy):", placeholder="Start typing...")

def fuzzy_filter(df, query):
    if not query:
        return pd.DataFrame()

    # Combine Book Name and Author for matching
    combined = df['Name of Book'].astype(str) + " " + df['Author'].astype(str)
    matches = get_close_matches(query, combined, n=10, cutoff=0.4)  # fuzzy match threshold

    # Filter matching rows
    return df[combined.isin(matches)]

# Filtered results
filtered = fuzzy_filter(book_data, query)

if not filtered.empty:
    st.success(f"🔍 {len(filtered)} match(es) found.")

    # Display only selected columns (hide Description)
    display_cols = ['Name of Book', 'Author', 'Language']
    show_df = filtered[display_cols] if all(col in filtered.columns for col in display_cols) else filtered
    st.dataframe(show_df, use_container_width=True)

    # Select book to view description
    selected = st.selectbox("📘 Select a book to view details", filtered['Name of Book'].dropna().unique())

    if selected:
        row = filtered[filtered['Name of Book'].str.strip() == selected.strip()]
        if not row.empty and 'Description' in row.columns:
            desc = row.iloc[0]['Description']
            st.markdown(f"### 📝 Description for *{selected}*")
            st.write(desc if pd.notna(desc) and str(desc).strip() else "No description available.")
else:
    if query:
        st.warning("❌ No close matches found.")
    else:
        st.info("Start typing to search by Book Name or Author.")
