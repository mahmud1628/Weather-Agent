# Weather Agent using LangChain and Groq

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import Tool, tool, AgentType, initialize_agent
import os
import requests



load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
if not openweathermap_api_key:
    raise ValueError("OPENWEATHERMAP_API_KEY environment variable not set.")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0.2,
    # max_tokens=1000,
    # top_p=0.95,
    # frequency_penalty=0,
    # presence_penalty=0,
)

def getCityFromIp(input: str = "") -> str:
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()
        return data.get("city", "")
    except Exception as e:
        return f"Error detecting city: {e}"
    
def detectInvalidInput(input: str) -> str:
    temp = input.lower().strip().split()
    for i in temp:
        # print(i)
        if i in ["none", "detect","(detect" "auto", "automatically","automatically)","location", "detect user's location automatically"]:
            return ""
    return input


@tool
def getWeatherData(city: str = "") -> str:
    """
    Fetches weather data for a given city. If no city is provided, it detects the city from the user's IP.
    """

    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."
    # Simulate fetching weather 
    
    # Sanitize vague inputs
    city = detectInvalidInput(city)

    if not city.strip():
        city = getCityFromIp()
    if not city.strip():
        return "Error: Unable to detect city from IP."
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": openweathermap_api_key,
        "units": "metric",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if data.get("cod") != 200:
            return f"Error: {data.get('message', 'Unknown error')}"
        return data
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    
get_weather_data = Tool(
    name="getWeatherData",
    func=getWeatherData,
    description=(
        "Fetches current weather for a city. If no city is given, it detects the user's location automatically. "
        "Use this tool to answer any questions about rain, temperature, or weather."
    ),
)

    

tools = [get_weather_data]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=False,
    # max_iterations=5,  # Stops after 3 steps
    # early_stopping_method="generate",  # Tries to produce an answer even if interrupted
)

query = "Will it rain cats and dogs today?"
response = agent.invoke({"input": query, "chat_history": []})
print(response["output"])

