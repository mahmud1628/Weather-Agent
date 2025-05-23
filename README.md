# 🌦️ Weather Agent using LangChain and Groq

This is a conversational weather assistant powered by **LangChain**, **Groq LLMs**, and **OpenWeatherMap API**. It can:

- Fetch **current weather**
- Provide **daily forecasts**
- Retrieve **historical weather data**

---

## ✅ Requirements

Before you begin, ensure you have the following:

- Python 3.8 or newer
- API keys for:
  - [Groq API](https://console.groq.com/)
  - [OpenWeatherMap API](https://openweathermap.org/api)
- FastAPI
- Firebase
- Google Cloud CLI
---

## 🧠 Installation Steps

1. **Clone or download this repository**

```bash
git clone https://github.com/mahmud1628/Weather-Agent
```

2. **Install the required python packages**

```bash
pip install langchain requests python-dotenv langchain_groq
```

3. **Create a .env file** <br>
In the root directory of your project, create a .env file with the following content:
```ini
GROQ_API_KEY=your_groq_api_key_here
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
```

4. **Run the server**
```bash
uvicorn main::app --reload
```
5. **Run the react app**
```bash
npm start
```
Once running, you can give prompt to the agent from the UI.

You can ask questions like:
 * What's the weather like in New York today?
 * Give me the forecast for London.
 * What was the weather in Tokyo 3 days ago?
 * Will it rain in Paris tomorrow?
 * Type exit to quit the program.



