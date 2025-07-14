import streamlit as st
import pandas as pd
import os

# ----------------- CONFIG -----------------
BOOK_FILE = "books.csv"
ADMIN_USERNAME = "yaduk883"
ADMIN_PASSWORD = "Animas@123"
DISPLAY_COLUMNS = ['Name of Book', 'Author', 'Language', 'N.o of Copies', 'Date', 'BAR CODE', 'Available/Not', 'Checked Out By']

# ----------------- HELPERS -----------------
def load_data():
    if os.path.exists(BOOK_FILE):
        df = pd.read_csv(BOOK_FILE)
        df.columns = df.columns.str.strip()
    else:
        df = pd.DataFrame(columns=DISPLAY_COLUMNS + ['Description'])
        df.to_csv(BOOK_FILE, index=False)
    return df

def save_book(row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(BOOK_FILE, index=False)

# ----------------- STREAMLIT UI -----------------
st.set_page_config("📚 Yadu's Library", layout="wide")
st.title("📚 Yadu's Book Library")

# ----------------- LOGIN SIDEBAR -----------------
with st.sidebar:
    st.header("🔐 Admin Login")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    login = st.button("Login", key="login_btn")

# ----------------- BOOK DATA -----------------
book_data = load_data()

# ----------------- ADMIN SECTION -----------------
is_admin = username == ADMIN_USERNAME and password == ADMIN_PASSWORD and login

if is_admin:
    st.success("✅ Logged in as Admin")

    st.subheader("➕ Add New Book")
    with st.form("add_book"):
        name = st.text_input("Name of Book")
        author = st.text_input("Author")
        lang = st.text_input("Language")
        copies = st.text_input("No. of Copies")
        date = st.date_input("Date")
        barcode = st.text_input("BAR CODE")
        available = st.selectbox("Available/Not", ["Available", "Not Available"])
        checked_out = st.text_input("Checked Out By")
        description = st.text_area("Description")

        submit = st.form_submit_button("➕ Add Book")
        if submit:
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
                st.error("❌ Book Name and Author are required.")

# ----------------- SEARCH SECTION -----------------
st.subheader("🔍 Search Library")
search_query = st.text_input("Type book name or author")

if search_query:
    query = search_query.lower()
    filtered = book_data[
        book_data['Name of Book'].str.lower().str.contains(query, na=False) |
        book_data['Author'].str.lower().str.contains(query, na=False)
    ]
    if not filtered.empty:
        st.write(f"🔎 Found {len(filtered)} result(s)")
        st.dataframe(filtered[DISPLAY_COLUMNS], use_container_width=True)

        selected_book = st.selectbox("📘 Select a book to view description", filtered['Name of Book'].dropna().unique())
        desc = filtered.loc[filtered['Name of Book'].str.strip() == selected_book.strip(), 'Description'].values
        st.markdown(f"### 📝 Description for *{selected_book}*")
        st.write(desc[0] if len(desc) > 0 and pd.notna(desc[0]) else "No description available.")
    else:
        st.warning("❌ No matches found.")
else:
    st.info("Start typing to search for books.")

