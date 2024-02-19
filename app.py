import os
import openai
import streamlit as st
from tavily import TavilyClient
from reportlab.lib.pagesizes import letter
from reportlab.lib import pagesizes
from reportlab.pdfgen import canvas
from io import BytesIO
import requests
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session
import yaml
from yaml.loader import SafeLoader


# This must be the first command in your app, and must be set only once
# Page configuration
st.set_page_config(
    layout="wide",
    page_title="🔍 SyncThree Researcher",
    page_icon=":memo:",
    menu_items={
        'Get Help': 'https://syncthree.ca',
        'Report a bug': "https://syncthree.ca",
        'About': "🙂 Hope this researcher is helpful. This is a *SyncThree* app. Learn more at [syncthree.ca](https://syncthree.ca)"
    }
)

# # Logo and Title
# col1, col2 = st.columns([1, 4])
# col1.image('https://syncthree.ca/wp-content/uploads/2023/07/SyncThree-Technologies-Logo-1-modified.png', width=100)  # Adjust the path and width as needed
# col2.title('SyncThree Researcher')
# Load environment variables from .env file
load_dotenv()

# # Constants for Google OAuth
# GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
# GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
# REDIRECT_URI = "http://localhost:8501"  # Adjust this as per your setup
# AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
# TOKEN_URL = "https://accounts.google.com/o/oauth2/token"

# def get_google_oauth_session():
#     return OAuth2Session(client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET,
#                          scope='openid email profile', redirect_uri=REDIRECT_URI)

# def handle_google_auth():
#     google = get_google_oauth_session()

#     if 'code' not in st.experimental_get_query_params():
#         # Redirect user to Google for authentication
#         # The authorization URL is created here
#         authorization_url = google.create_authorization_url(AUTHORIZE_URL)
#         st.experimental_set_query_params(state=authorization_url['state'])
#         st.write(f"Please go to {authorization_url['url']} and authorize access.")
#         return False
#     else:
#         # Handle callback from Google, get the authorization code
#         code = st.experimental_get_query_params()['code'][0]
#         google.fetch_token(TOKEN_URL, authorization_response=f"{REDIRECT_URI}?code={code}")
        
#         # Fetch user details using the token
#         user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        
#         st.session_state['logged_in'] = True
#         st.session_state['username'] = user_info.get('email')
#         return True

hide_streamlit_style = """
            <style>
            # MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# ... rest of your code
sidebar = st.sidebar

# # Sidebar modifications
# sidebar.header(" Please Log In")
sidebar.image('https://syncthree.ca/wp-content/uploads/2023/07/SyncThree-Technologies-Logo-1-modified.png', width=100)

# ... rest of your code
with open('config.yaml', 'r') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None



sidebar = st.sidebar  # Assign the sidebar to a variable


# Display login form if not logged in
if not st.session_state['logged_in']:
    sidebar.header("Please Log In 🔑")
    username = sidebar.text_input("Username", key="login_username")
    password = sidebar.text_input("Password", type="password", key="login_password")
    if sidebar.button('🔓 Login'):
        # Iterate over the list of credentials
        for credential in config['credentials']:
            if username == credential['username'] and password == credential['password']:
                # User successfully authenticated
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()  # Immediately rerun the app script
                break  # Exit the loop once a match is found
        else:  # This else clause executes when the for loop completes normally (no break statement encountered)
            sidebar.error('Username/password is incorrect')
     # Add a signup form
    if sidebar.button('🌟 Sign Up'):

        st.session_state['signup'] = True
        st.rerun()

if 'signup' in st.session_state and st.session_state['signup']:
    sidebar.header("Please Sign Up")
    new_email = sidebar.text_input("Email Address", key="signup_email")
    new_username = sidebar.text_input("New Username", key="signup_username")
    new_password = sidebar.text_input("Password", key ="signup_password")
    if sidebar.button('Create Account'):

                       
        # Add the new account to the config dictionary
        config['credentials'].append({
            'username': new_username,
            'email': new_email,
            'password': new_password,  # You might want to ask for a password here
            'research_count': 0
        })
        # Save the updated config dictionary back to the config.yaml file
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file)
        st.session_state['signup'] = False
        st.success('Account created successfully!')
        sidebar.write(f'You can log in now :)')
        st.rerun()

# # Google authentication
# if not st.session_state['logged_in']:
#     if sidebar.button('Login with Google'):
#         handle_google_auth()

if st.session_state['logged_in']:
    # Fetch research count for the logged-in user
    research_count = 0
    for credential in config['credentials']:
        if st.session_state['username'] == credential['username']:
            research_count = credential['research_count']
            break

    sidebar.success(f'Logged in as {st.session_state["username"]}')
    sidebar.write(f'Research count: {research_count}')  # Display the research count
    # If research count is greater than 10, display the tip buttons
    if research_count > 10:
        sidebar.write(f'Your clearly enjoying the researcher if you want to help with manitence cost you can leave us a tip below :)')
        if sidebar.button('Tip :bank:'):
            sidebar.write('Redirecting to Buy Me A Coffee...[link](https://syncthree.ca)')
            # Here you can add the code to redirect to your Buy Me A Coffee link
        if sidebar.button('Tip with Crypto :coin:'):
            sidebar.write('[Crypto Tipping Platform](syncthree.ca)')
            # Here you can add the code to redirect to your Crypto Tipping Platform
    if sidebar.button('Logout :lock_with_ink_pen:'):
        st.session_state['logged_in'] = False
        st.session_state['username'] = None
        st.rerun() # Immediately rerun the app script

    
# Google Authentication

    

# # Initialize clients
tavily = TavilyClient(api_key="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")
client = openai.OpenAI(
    api_key="ad0dc3b33c6daf7e372777b6672803c6f959df53c9489d6ceb9d32483907a9df",
    base_url="https://api.together.xyz"    
)
 
def get_tavily_research(query, search_depth, max_results, include_images, include_answer, include_raw_content, include_domains, exclude_domains):
    """
    Perform research using Tavily's search.
    """
    try:
        response = tavily.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_images=include_images,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        if 'results' not in response or not response['results']:
            st.error("Tavily response does not contain 'results' or 'results' is empty.")
            return None, None  # Return None for both results and images
        # Extract images if they are included in the response
        images = response.get('images', []) if include_images else []
        return response['results'], images
    except Exception as e:
        st.error(f"An error occurred while fetching Tavily research: {e}")
        return None, None



def get_ai_summary(context):
    """
    Get a summary from OpenAI based on the Tavily research results.
    """
    try:
        context_for_ai = "\n\n".join([f"{obj['content']} (Source: {obj['url']})" for obj in context])
        completion = client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            temperature = 0.4,
            max_tokens= 2000,
            # top_p = 0.7,
            messages=[
                {"role": "system", "content": "I am an AI trained to summarize research data and provide insights on the research provided below. Please summarize the information below, be as verbose as possible."},
                {"role": "user", "content": context_for_ai}
            ],
            
            
        )   
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating AI summary: {e}")
        return None



def create_md_file(summary, images, research_results):
    """
    Create a markdown file with the AI summary, images, and research results.
    """
    # Start with the AI summary
    md_content = f"# AI Summary:\n{summary}\n\n"

    # Add images
    for img_url in images:
        md_content += f"![Image]({img_url})\n\n"

    # Add research results
    md_content += "# Research Results:\n"
    for result in research_results:
        md_content += f"- {result}\n"

    # Write the markdown content to a file
    with open("research_summary.md", "w", encoding='utf-8') as md_file:
        md_file.write(md_content)

    # Read the file content as bytes
    with open("research_summary.md", "rb") as md_file:
        return md_file.read()


# Initialize session state variables
if 'research_results' not in st.session_state:
    st.session_state['research_results'] = None
if 'images' not in st.session_state:
    st.session_state['images'] = None
if 'ai_summary' not in st.session_state:
    st.session_state['ai_summary'] = None

# Streamlit app interface
st.title('SyncThree Researcher')

# User input for the main query
user_query = st.text_input('Enter your research question:', 'What should I invest in 2024?')

# Advanced search expander
with st.expander("Advanced Search Options"):
    search_depth = st.selectbox('Select search depth:', ['basic', 'advanced'], index=0)
    max_results = st.number_input('Number of sources (Max 10):', min_value=1, value=5, max_value=10)
    include_images = st.checkbox('Include images in the response? (Must be on advanced search depth)')
    include_answer = st.checkbox('Include a short answer in the search results?')
    include_raw_content = st.checkbox('Include raw content of each site in the search results?')
    include_domains = st.text_input('Include domains (comma-separated, no spaces):')
    exclude_domains = st.text_input('Exclude domains (comma-separated, no spaces):')

    # Convert comma-separated strings to lists
    include_domains_list = [domain.strip() for domain in include_domains.split(',')] if include_domains else []
    exclude_domains_list = [domain.strip() for domain in exclude_domains.split(',')] if exclude_domains else []

# Remove this line
# button_col1, button_col2 = st.columns([1, 1])

# Research button
if 'research_done' not in st.session_state:
    st.session_state['research_done'] = False

# Replace button_col1.button with st.button
if st.button('Research 🔍') and not st.session_state['research_done']:
    # Use the variables defined inside the expander for the search
    st.session_state['research_results'], st.session_state['images'] = get_tavily_research(
        user_query,
        search_depth,
        max_results,
        include_images,
        include_answer,
        include_raw_content,
        include_domains_list,
        exclude_domains_list
    )
    if st.session_state['research_results']:
        st.session_state['ai_summary'] = get_ai_summary(st.session_state['research_results'])
        st.session_state['research_done'] = True

        # Increment research count for the logged in user
        for credential in config['credentials']:
            if st.session_state['username'] == credential['username']:
                credential['research_count'] += 1
                break

        # Save the updated data back to 'config.yaml'
        with open('config.yaml', 'w') as file:
            yaml.dump(config, file)

        st.rerun()   
        

# Generate MD button and Download MD button
if st.session_state['research_done']:
    md_data = create_md_file(
        st.session_state['ai_summary'],
        st.session_state['images'],
        st.session_state['research_results']
    )
    # Create a download button
    st.download_button(
        label="📥 Download Research Summary as Markdown",
        data=md_data,
        # file_name="research_summary.md",
        file_name=f"{user_query.replace(' ', '_')}_summary.md",
        mime="text/markdown"
    )

    # Add the "New Search" button here
    if st.button('🔄 New Search'):
        # Reset the necessary session state variables
        st.session_state['research_results'] = None
        st.session_state['images'] = None
        st.session_state['ai_summary'] = None
        st.session_state['research_done'] = False
        # Rerun the app to refresh the input fields
        st.rerun()
        
# Display the results and images if they exist in session state
if st.session_state['research_results']:
    st.title('📜 AI Summary:')
    st.write(st.session_state['ai_summary'])

    if st.session_state['images']:
        st.subheader('Related Images:')
        cols_per_row = 3
        cols = st.columns(cols_per_row)
        for index, img_url in enumerate(st.session_state['images']):
            with cols[index % cols_per_row]:
                st.image(img_url)

    st.title('Research Results:')
    st.write(st.session_state['research_results'])


# elif st.session_state['research_results'] is None and st.button('Research', key='research_button_2'):
#     st.error("No research results to display.")