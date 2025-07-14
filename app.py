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
# Streamlit App Setup
# ------------------------------------------
st.set_page_config(page_title="📚 Yadu's Book Library", layout="wide")
st.title("📚 Yadu's Book Library")

book_data = load_data()

# Drop "Sl No" if exists
if 'Sl No' in book_data.columns:
    book_data.drop(columns=['Sl No'], inplace=True)

# Columns to display in table
display_columns = [
    'Name of Book', 'Author', 'Language', 'N.o of Copies',
    'Date', 'BAR CODE', 'Available/Not', 'Checked Out By'
]

# ------------------------------------------
# Admin Login
# ------------------------------------------
st.sidebar.header("🔐 Admin Login")
with st.sidebar:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

is_admin = False
if login:
    if username == "admin" and password == "admin123":
        st.sidebar.success("✅ Logged in as admin")
        is_admin = True
    else:
        st.sidebar.error("❌ Invalid credentials")

# ------------------------------------------
# Book Search Section
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

# ------------------------------------------
# Admin Controls - Add New Book (just form, not connected to sheet yet)
# ------------------------------------------
if is_admin:
    st.markdown("---")
    st.subheader("➕ Add a New Book")

    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Book Name")
        new_author = st.text_input("Author")
        new_lang = st.text_input("Language")
        new_date = st.date_input("Date")
    with col2:
        new_copies = st.number_input("No. of Copies", min_value=1, value=1)
        new_barcode = st.text_input("BAR CODE")
        new_avail = st.selectbox("Available/Not", ["Available", "Not Available"])
        new_user = st.text_input("Checked Out By (if any)")

    new_desc = st.text_area("Description")

    if st.button("✅ Add Book"):
        st.success(f"📚 Book '{new_name}' added successfully (functionality placeholder only).")

        # NOTE: To actually append to Google Sheet, you'd need gspread + service account setup
