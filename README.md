# resto-weather-agent
This project coordinates specialized agents—one for restaurants, one for weather—to answer a simple question: “Should we go out, and where?” It fetches real data, shares state across subgraphs, and returns a concise recommendation with top picks.

## Concepts

### 1) Multi-Agent Coordination
- The app is a **parent graph** that orchestrates two subgraphs:
  - **Weather agent** — gets the weather report for `(location, date)`.
  - **Restaurant agent** — finds and extracts a clean list of venues for `(location, event, date)`.
- Both subgraphs consume the **query analyzer** output; then a **recommendation analyzer** combines results to produce **GO / STAY-IN** plus top picks.

START


└─> query_analyzer ─┬─> weather_graph ─┐



└─> restaurant_graph ─┴─> recommendation_analyzer ─> END


### 2) Tool Integration
- **DuckDuckGo** via the `ddgs` package (no API key) to gather candidate venues from listicles/aggregators (TripAdvisor, Zomato, LBB, etc.).  
- **OpenWeatherMap** (recommended) to fetch a real forecast to inform the GO/STAY-IN decision (`OWM_API_KEY` in `.env`).  
- Tools run **inside nodes** (deterministic) so we don’t rely on the LLM “choosing” to call them.

### 3) State Management
- Shared state is defined with `TypedDict`/Pydantic models (e.g., `ParentState`, `RestaurantState`).
- Subgraphs **write** structured outputs (`restaurants`, `weather_report`) that the parent graph **reads** in `recommendation_analyzer`.
- Deterministic fetch nodes also store debugging text like `search_blob` so you can print/inspect raw tool output.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BenAyedMedAla/resto-weather-agent.git
   cd resto-weather-agent

2. **Install dependencies**:

-Make sure Python 3.10+ is installed.

-Create a virtual environment (optional but recommended):
     
    ```bash
    python -m venv venv
    source venv/bin/activate

-Install the necessary packages:
    ```bash
    pip install -r requirements.txt


3. **Set up environment variables**:
-Create a .env file in the root directory of the project.
-Add your API keys to the .env file :

   ```bash
   GROQ_API_KEY=your_weather_api_key
   

5. **Run the project:**:
     ```bash
   python main.py
## Example Responses : 
1. **Query: "Tell me about the best caffees for date night in paris for next saturday"** :



================================== Agent ==================================



GO to Paris for a date night, as the city's romantic atmosphere is perfect for a evening out.
Top picks:
* Café de Flore for historic charm
* Carette for Eiffel Tower views
* Breizh Café for delicious crepes
Book reservations in advance and arrive early to secure a good table.

2. **Query:  "Tell me about the best restaurants for breakfast in barcelone for next saturday "** :


================================== Agent ==================================



GO to Barcelona next Saturday for a delightful breakfast scene.  
Top picks: Can Culleretes for traditional Catalan dishes, Federal Café for international options, and Pinotxo Bar for market-fresh breakfast.
Reserve ahead, especially for popular spots, and consider exploring neighborhoods like El Raval or El Born.

