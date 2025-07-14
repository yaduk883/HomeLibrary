import streamlit as st
import pandas as pd
import os

BOOK_FILE = "books.csv"
ADMIN_USERNAME = "yaduk883"
ADMIN_PASSWORD = "Animas@123"

# Columns for display
DISPLAY_COLUMNS = ['Name of Book', 'Author', 'Language', 'N.o of Copies', 'Date', 'BAR CODE', 'Available/Not', 'Checked Out By']

# -------------------------------
# Load or Create Data
# -------------------------------
@st.cache_data(ttl=600)
def load_data():
    if os.path.exists(BOOK_FILE):
        df = pd.read_csv(BOOK_FILE)
        df.columns = df.columns.str.strip()
    else:
        df = pd.DataFrame(columns=DISPLAY_COLUMNS + ['Description'])
        df.to_csv(BOOK_FILE, index=False)
    return df

def save_book(row):
    df = pd.read_csv(BOOK_FILE)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(BOOK_FILE, index=False)

# -------------------------------
# App Start
# -------------------------------
st.set_page_config("📚 Yadu's Library", layout="wide")
st.title("📚 Yadu's Book Library")

book_data = load_data()

# -------------------------------
# Admin Section
# -------------------------------
with st.sidebar:
    st.header("🔐 Admin Login")
    with st.form("admin_login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    is_admin = (username == ADMIN_USERNAME and password == ADMIN_PASSWORD)

if is_admin:
    st.success("Logged in as Admin ✅")

    st.header("➕ Add New Book")
    with st.form("add_book"):
        name = st.text_input("Name of Book")
        author = st.text_input("Author")
        lang = st.text_input("Language")
        copies = st.text_input("N.o of Copies")
        date = st.date_input("Date")
        barcode = st.text_input("BAR CODE")
        available = st.selectbox("Available/Not", ["Available", "Not Available"])
        checked_out = st.text_input("Checked Out By")
        description = st.text_area("Description")

        submit_book = st.form_submit_button("➕ Add Book")
        if submit_book:
            if name and author:
                row = {
                    'Name of Book': name,
                    'Author': author,
                    'Language': lang,
                    'N.o of Copies': copies,
                    'Date': date,
                    'BAR CODE': barcode,
                    'Available/Not': available,
                    'Checked Out By': checked_out,
                    'Description': description
                }
                save_book(row)
                st.success(f"✅ Book '{name}' added successfully!")
            else:
                st.error("Book Name and Author are required.")
else:
    st.info("Login as admin to add books.")

# -------------------------------
# Search + Filter Section
# -------------------------------
search = st.text_input("🔍 Search by Book Name or Author:")
filtered = book_data.copy()

if search:
    search_lower = search.lower()
    filtered = book_data[
        book_data['Name of Book'].str.lower().str.contains(search_lower, na=False) |
        book_data['Author'].str.lower().str.contains(search_lower, na=False)
    ]

# -------------------------------
# Display Results
# -------------------------------
if not filtered.empty:
    st.subheader("📖 Search Results")
    st.dataframe(filtered[DISPLAY_COLUMNS], use_container_width=True)

    selected = st.selectbox("📘 Select a book to view description", filtered['Name of Book'].dropna().unique())
    desc = filtered.loc[filtered['Name of Book'].str.strip() == selected.strip(), 'Description'].values
    st.markdown(f"### 📝 Description for *{selected}*")
    st.write(desc[0] if len(desc) > 0 and pd.notna(desc[0]) else "No description available.")

    # Download
    csv = filtered[DISPLAY_COLUMNS].to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Results as CSV", csv, "search_results.csv", "text/csv")
else:
    if search:
        st.warning("❌ No matching books found.")
    else:
        st.info("Type above to search your library.")
