import streamlit as st
import pandas as pd
import os

BOOK_FILE = "books.csv"
ADMIN_USERNAME = "yaduk883"
ADMIN_PASSWORD = "Animas@123"

COLUMNS = ['Name of Book', 'Author', 'Language', 'N.o of Copies', 'Date',
           'BAR CODE', 'Available/Not', 'Checked Out By', 'Description']

# Load or initialize the CSV
def load_books():
    if not os.path.exists(BOOK_FILE):
        pd.DataFrame(columns=COLUMNS).to_csv(BOOK_FILE, index=False)
    df = pd.read_csv(BOOK_FILE)
    df.columns = df.columns.str.strip()
    return df

def add_book(entry):
    df = load_books()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(BOOK_FILE, index=False)

st.set_page_config("📚 Yadu's Library", layout="wide")
st.title("📚 Yadu's Book Library")

books = load_books()

# --- Admin Sidebar ---
with st.sidebar:
    st.header("🔐 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

is_admin = login and username == ADMIN_USERNAME and password == ADMIN_PASSWORD

if is_admin:
    st.success("✅ Logged in as Admin")
    st.subheader("➕ Add a New Book")

    with st.form("book_form"):
        name = st.text_input("Name of Book")
        author = st.text_input("Author")
        language = st.text_input("Language")
        copies = st.text_input("Number of Copies")
        date = st.date_input("Date")
        barcode = st.text_input("BAR CODE")
        available = st.selectbox("Available/Not", ["Available", "Not Available"])
        checked_out = st.text_input("Checked Out By")
        description = st.text_area("Description")

        submit = st.form_submit_button("Add Book")

        if submit:
            if name and author:
                entry = {
                    'Name of Book': name,
                    'Author': author,
                    'Language': language,
                    'N.o of Copies': copies,
                    'Date': date,
                    'BAR CODE': barcode,
                    'Available/Not': available,
                    'Checked Out By': checked_out,
                    'Description': description
                }
                add_book(entry)
                st.success(f"✅ Book '{name}' added successfully.")
            else:
                st.error("❌ Name and Author are required.")

# --- User Search ---
st.subheader("🔍 Search Library")
search = st.text_input("Enter book name or author:")

if search:
    search_lower = search.lower()
    results = books[
        books['Name of Book'].str.lower().str.contains(search_lower, na=False) |
        books['Author'].str.lower().str.contains(search_lower, na=False)
    ]

    if not results.empty:
        st.write(f"📚 Found {len(results)} match(es):")
        st.dataframe(results[COLUMNS[:-1]])  # exclude Description
        selected = st.selectbox("Select a book to see description", results['Name of Book'].dropna().unique())
        desc = results.loc[results['Name of Book'] == selected, 'Description'].values
        st.markdown("### 📝 Description")
        st.write(desc[0] if len(desc) > 0 and pd.notna(desc[0]) else "No description available.")
    else:
        st.warning("🔍 No results found.")
else:
    st.info("Type a book name or author to search.")

