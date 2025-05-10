# Weather Agent using LangChain and Groq

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import Tool, tool, AgentType, initialize_agent
import os
import requests
from datetime import datetime, timedelta



load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
if not openweathermap_api_key:
    raise ValueError("OPENWEATHERMAP_API_KEY environment variable not set.")

llm = ChatGroq(
    groq_api_key=groq_api_key,
    # model="llama-3.1-8b-instant",
    # model="deepseek-r1-distill-llama-70b",
    model="qwen-qwq-32b",
    temperature=0.7,
    # max_tokens=1000,
    # top_p=0.95,
    # frequency_penalty=0,
    # presence_penalty=0,
)

def get_coordinates(city: str):
    """
    Fetches the coordinates (latitude and longitude) of a given city using OpenWeatherMap API.
    """
    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."
    
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
        return data['coord']['lon'], data['coord']['lat']
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

def getCityFromIp(input: str = "") -> str:
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()
        return data.get("city", "")
    except Exception as e:
        return f"Error detecting city: {e}"


@tool
def getCurrentWeather(city: str = "") -> str:
    """
    Fetches weather data for a given city. If no city is provided, it detects the city from the user's IP.
    """

    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."
    # Simulate fetching weather 

    if city is None or city == 'None' or city == 'none':
        city = getCityFromIp()
    
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
    
get_current_weather_data = Tool(
    name="getCurrentWeather",
    func=getCurrentWeather,
    description=(
        "Fetches today's current weather for a city. If no city is given, it detects the user's location automatically. "
        "Input should be the provided city name only. If not provided,input will be 'None'."
        "Use this tool to answer any questions about rain, temperature, or weather."
    ),
)


def getDailyForecast(city: str = "") -> str:
    """
    Fetches hourly weather forecast for a given city. If no city is provided, it detects the city from the user's IP.
    """
    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."
    

    if city is None or city == 'None' or city == 'none':
        city = getCityFromIp()
    
    url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    # url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": openweathermap_api_key,
        "units": "metric",
        #"cnt": 3,  # Number of days to forecast
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if data["cod"] != '200':
            return f"Error: {data.get('message', 'Unknown error')}"
        return data
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    
get_daily_forecast = Tool(
    name="getDailyForecast",
    func=getDailyForecast,
    description=(
        "Fetches daily weather forecast for a city.  If no city is given, it detects the user's location automatically. You don't need to detect location. "
        "Use this tool to answer any questions about rain, temperature, or weather for days after today. Input should be the provided city name only. If not provided,input will be 'None'."
    ),
)


@tool
def getHistoricalData(input):
    """
    Fetches historical weather data for a given city and number of days ago.
    Two inputs are required: city and days. If no city is provided, it detects the city from the user's IP."
    """
    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."


    inputs = input.split(",")
    if len(inputs) != 2:
        return "Error: Invalid input format. Please provide city and days in the format: city, days"
    city = inputs[0].strip()
    days =int(inputs[1].strip())

    if city is  None or city == 'None' or city == 'none':
        city = getCityFromIp()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    lon, lat = get_coordinates(city)
    url = "https://history.openweathermap.org/data/2.5/history/city"
    params = {
        #"q": city,
        "lat": lat,
        "lon": lon,
        "appid": openweathermap_api_key,
        'type': 'hour',
        'start': start_timestamp,
        'end': end_timestamp,
        'cnt': 1,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if data["cod"] != '200':
            return f"Error: {data.get('message', 'Unknown error')}"
        return data
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    
get_historical_data = Tool(
    name="getHistoricalData",
    func=getHistoricalData,
    description=(
        "Fetches historical weather data for a city. "
        "Two inputs are required: city and days. If no city is provided, it detects the city from the user's IP, so pass 'None'"
        "Inout format :city, days "
        "Use this tool to answer any questions about rain, temperature, or weather for days before today. "
    ),
)

    

tools = [
    get_current_weather_data,
    get_daily_forecast,
    get_historical_data,
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=5,
    handle_parsing_errors=True , # Stops after 3 steps
    early_stopping_method="generate",  # Tries to produce an answer even if interrupted
)

while True:
    query = input("Ask me about the weather: ")
    if query == "exit":
        break
    response = agent.invoke({"input": query, "chat_history": []})
    print("Response:" ,response["output"])

