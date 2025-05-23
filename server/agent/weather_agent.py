# Weather Agent using LangChain and Groq

from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain.agents import Tool, AgentType, initialize_agent
import os
import requests
import json
from langchain_community.chat_message_histories import FirestoreChatMessageHistory



load_dotenv()

chat_histories = {}

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
if not openweathermap_api_key:
    raise ValueError("OPENWEATHERMAP_API_KEY environment variable not set.")
tomorrow_io_api_key = os.getenv("TOMORROW_IO_API_KEY")
if not tomorrow_io_api_key:
    raise ValueError("TOMORROW_IO_API_KEY environment variable not set.")

llm = ChatGroq(
    api_key=groq_api_key,
    # model="llama-3.1-8b-instant",
    # model="deepseek-r1-distill-llama-70b",
    model="qwen-qwq-32b",
    temperature=0.7,
)

def getCityFromIp(input: str = "") -> str:
    try:
        response = requests.get("https://ipinfo.io/json")
        response.raise_for_status()
        data = response.json()
        return data.get("city", "")
    except Exception as e:
        return f"Error detecting city: {e}"


def getCurrentWeather(city: str = "None") -> str:
    """
    Fetches weather data for a given city. If no city is provided, it detects the city from the user's IP.
    """

    if not openweathermap_api_key:
        return "Error: OpenWeatherMap API key is not set."

    if city is None or city.lower() == 'none':
        city = getCityFromIp()
    
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": openweathermap_api_key,
        "units": "metric",
        "cnt": 8
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if data.get("cod") != '200':
            return f"Error: {data.get('message', 'Unknown error')}"
        return json.dumps(data)
    
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
    
    # url = "https://api.openweathermap.org/data/2.5/forecast/daily"
    # url = "https://api.openweathermap.org/data/2.5/weather"
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": openweathermap_api_key,
        "units": "metric",
        "cnt": 24
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        if data["cod"] != '200':
            return f"Error: {data.get('message', 'Unknown error')}"
        return json.dumps(data)
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

    url = "https://api.tomorrow.io/v4/weather/history/recent"

    params = {
        "location": city,
        "apikey": tomorrow_io_api_key,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # print(data)

        timelines = data.get("timelines", {})
        if "hourly" not in timelines or not timelines["hourly"]:
            return f"No hourly historical data available for {city}."
        return json.dumps(timelines.get("daily", []))

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

def get_agent(session_id: str):
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        #max_iterations=5,
        handle_parsing_errors=True ,
        early_stopping_method="generate",  # Tries to produce an answer even if interrupted
    )

    if session_id not in chat_histories:
        chat_histories[session_id] = FirestoreChatMessageHistory(
        session_id=session_id, collection_name="chat-history", user_id="user-1")
    history = chat_histories[session_id]

    return agent, history

def get_agent_response(query: str, session_id: str):
    agent, history = get_agent(session_id)
    trimmed = history.messages[:10] if len(history.messages) > 10 else history.messages
    response = agent.invoke({"input": query, "chat_history": trimmed})
    history.add_user_message(query)
    history.add_ai_message(response["output"])
    return response["output"]