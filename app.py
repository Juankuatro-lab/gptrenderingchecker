
import os
import streamlit as st

try:
    import openai
    from openai import OpenAI
except ImportError as e:
    st.error(f"""
    ❌ Failed to import OpenAI module.
    
    Error: {str(e)}
    
    Please ensure requirements.txt contains:
    ```
    streamlit
    openai
    ```
    """)
    st.stop()
    
# Page configuration
st.set_page_config(
    page_title="OpenAI URL Inspection Tool",
    layout="wide"
)
# Sidebar for API key
st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key", 
    type="password", 
    help="Enter your OpenAI API key",
    value=os.environ.get("OPENAI_API_KEY", "")
)
# Main content
st.title("OpenAI URL Inspection Tool")
st.markdown("""
This app is an early attempt to create a **URL inspection tool** for OpenAI’s ChatGPT. It checks whether a page is cached in OpenAI’s index or requires grounding to synthesize an answer.

The app uses a **UK (London) user location**, which I found to reduce hallucinations in the output and better suit my use cases.

**More details** – [OpenAI Web Search Documentation](https://platform.openai.com/docs/guides/tools-web-search#live-internet-access)
""")
st.markdown("---")
# URL input
url = st.text_input(
    "Enter URL to test:", 
    placeholder="https://example.com", 
    help="Paste the URL you want to check"
)

# Run button
if st.button("Check OpenAI Index", type="primary", disabled=not api_key or not url):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar")
    elif not url:
        st.error("⚠️ Please enter a URL to test")
    else:
        try:
            with st.status("Checking URL...", expanded=True) as status_box:
                # Initialize OpenAI client 
                openai_client = openai.Client(api_key=api_key)
                
                # Check cached pages (external_web_access: False)
                external_web_access = False
                
                # User location based on OpenAI's documentation (London, UK)
                user_location = {
                    "type": "approximate",
                    "country": "GB",
                    "city": "London",
                    "region": "London",
                }
                
                status_box.update(label="Making API request...", state="running")
                
                # Make API call
                response = openai_client.responses.create(
                    model="gpt-5",
                    tools=[{
                        "type": "web_search",
                        "external_web_access": external_web_access
                    }],
                    tool_choice="auto",
                    input=f"Can you access this page {url}? If you can, make a summary"
                )
                
                status_box.update(label="Complete", state="complete")
                
                # Get response text
                output_text = response.output_text
                
                # Display raw response
                st.subheader("Response from OpenAI:")
                st.info(output_text)
                
                # Interpret results
                st.subheader("Interpretation:")
                
                if output_text.startswith("Yes—I can ") or output_text.startswith("I can access "):
                    st.success("""
                    ✅ **ChatGPT-User was not prevented by JavaScript blockers and surfaced a cached raw HTML to synthesize a likely answer in the live chat.**
                    
                    ChatGPT is familiar with your page and there may be little to no optimisation efforts for you take on.
                    """)
                elif (output_text.startswith("I can't access") or 
                      output_text.startswith("I couldn’t") or
                      output_text.startswith("I tried to open") or
                      ", but " in output_text):
                    st.warning("""
                    ⚠️ **ChatGPT-User may have been prevented by JavaScript blockers (CSR geo-location pop-ups e.g;) or the page simply couldn't be found in OpenAI's cached index.**
                    
                    Consider reviewing blocking CSR JavaScript and increase mentions and citations via targeted Digital PR efforts.
                    """)
                    
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.info("Please check your API key and try again. Make sure you have access to the GPT-5 model and the responses API.")
# Instructions
with st.expander("ℹ️ How to use this tool"):
    st.markdown("""
    1. **Enter your OpenAI API Key** in the sidebar (required)
    2. **Paste the URL** you want to test in the input field
    3. **Click "Check OpenAI Index"** to test if the URL is cached in OpenAI's index
    4. Review the results
    
    **Note:** This tool checks cached pages only and uses a fixed IP location for more consistent results - this is based on personal recent tests.
    """)
# Footer
st.markdown("---")
st.caption("Delivered by Simone De Palma for [SEODepths](https://seodepths.com)")
