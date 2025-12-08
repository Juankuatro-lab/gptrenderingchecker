# Check if ChatGPT-User can surface your page from OpenAI's index

from openai import OpenAI

OPENAI_API_KEY = 'your_openai_key'
client = OpenAI(api_key=OPENAI_API_KEY)

test_1 = client.responses.create(
    model="gpt-5",
    tools=[{ "type": "web_search", "external_web_access": False }],

    tool_choice="auto",
    input="Can you access this page? {url}  If you can, make a summary."
)

# --------

# Check if ChatGPT-User can surface your page from OpenAI's index
# with a specific IP location

from openai import OpenAI

OPENAI_API_KEY = 'your_openai_key'
client = OpenAI(api_key=OPENAI_API_KEY)

test_1 = client.responses.create(
    model="gpt-5",
    tools=[{ "type": "web_search", "external_web_access": False }],

    tool_choice="auto",
    input="Can you access this page? {url}  If you can, make a summary."
)

# Declare your IP location for more concise output
user_location={
        "type": "approximate",
        "country": "GB",
        "city": "London",
        "region": "London",
    }
print(test_1.output_text)
