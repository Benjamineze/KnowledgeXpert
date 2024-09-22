import base64
import streamlit as st
from PyPDF2 import PdfReader
from docx import Document
import openai


OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
VALID_PASSWORDS = st.secrets["VALID_PASSWORDS"].split(",")

openai.api_key = OPENAI_API_KEY

def read_pdf(file):
    try:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to read content from DOCX
def read_docx(file):
    try:
        doc = Document(file)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        return f"Error reading DOCX: {e}"

# Function to handle file reading
def read_file(file):
    if file.type == 'application/pdf':
        return read_pdf(file)
    elif file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return read_docx(file)
    else:
        return 'Unsupported file type.'

# Function to query GPT-3/4 using OpenAI's API
def query_gpt(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{context}\n\nQ: {prompt}"}
            ]
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI

# Custom CSS to add the background image
def add_bg_from_local(image_file):
    with open(image_file, "rb") as file:
        data = file.read()
        encoded_image = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                image-rendering: optimizeQuality;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Call the function to add the background image
add_bg_from_local("vecteezy_teal-background-high-quality_30679827.jpg") 

def add_circle_image_to_bg(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    st.markdown(
        f"""
        <div style="display: flex; justify-content: flex-start; align-items: flex-start;">
            <img src="data:image/png;base64,{encoded_image}" 
                 style="border-radius: 100%; width: 40px; height: 40px; position: absolute; right: 28px; margin-right: 241px; top: 25px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )

# Call the function with the path to the image
add_circle_image_to_bg("Ke image.jfif")

st.title("My Knowledge Xpert")

# Initialize session state for login, uploaded content, user query, and response
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'uploaded_content' not in st.session_state:
    st.session_state.uploaded_content = ""
if 'user_query' not in st.session_state:
    st.session_state.user_query = ""
if 'response' not in st.session_state:
    st.session_state.response = ""

# Login Page
if not st.session_state.logged_in:
    password = st.text_input("Enter the password to access the system files:", type="password")
    if st.button("Login"):
        if password in VALID_PASSWORDS:
            st.session_state.logged_in = True
            st.success("Access granted! You can now upload files.")
            st.rerun()  # Refresh to show the upload page
        else:
            st.error("Access denied! Incorrect password.")

# File Upload Page
if st.session_state.logged_in:
    # Handle the Back button press before other actions to speed up rerun
    col1, col_spacer, col2 = st.columns([2, 8, 2])
    with col2:   # Back button
        if st.button("Back"):  
            st.session_state.uploaded_content = ""  
            st.session_state.user_query = ""  
            st.session_state.response = "" 
            st.rerun()  # Rerun to go back to the upload page

    # Show the file uploader only if no content has been uploaded
    if not st.session_state.uploaded_content:
        uploaded_files = st.file_uploader("Upload Files", type=['pdf', 'docx'], accept_multiple_files=True)

        # Handle file uploads
        if uploaded_files:
            document_text = ""
            for file in uploaded_files:
                doc_text = read_file(file)
                document_text += doc_text

            if document_text.strip():
                st.session_state.uploaded_content = document_text
                st.success("Connected....")
                st.rerun()  # Rerun the app to hide uploader
            else:
                st.error("No text could be extracted from the documents.")

    # Show "How may I help?" and response field only after file upload
    if st.session_state.uploaded_content:
        st.write("Connected....")  # Show "Connected" after successful upload
        
        # Text input for user query
        user_query = st.text_input("How may I help?:", value=st.session_state.user_query)

        if user_query:
            st.session_state.user_query = user_query  # Save the query in session state
            with st.spinner("Typing response..."):
                answer = query_gpt(st.session_state.user_query, st.session_state.uploaded_content)
                
                # Save and display the answer
                st.session_state.response = answer
                st.write("Response:")
                st.write(st.session_state.response)

       
        if st.button("Clear", key="clear_button"):
            st.session_state.response = ""  
            st.session_state.user_query = ""  
            st.rerun()  # Rerun the script to refresh the UI


