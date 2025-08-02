# Trip Planner App - MCP Server

An intelligent trip planning application built with AutoGen agents and Model Context Protocol (MCP) server. This application uses AI agents to create personalized travel itineraries based on user preferences and real-time attraction data.

📖 **Learn More**: This project is explained in detail in the Medium article series ["MCP Simplified: A Friendly Guide to Model Context Protocol"](https://medium.com/@renjuhere/mcp-simplified-a-friendly-guide-to-model-context-protocol-1-4-9073e63113c5).

## Features

- 🤖 **Multi-Agent System**: Utilizes AutoGen agents for collaborative trip planning
- 🌍 **Real-time Attraction Data**: Integrates with OpenTripMap API for up-to-date attraction information
- 🎯 **Personalized Recommendations**: Considers user preferences for customized itineraries
- 🔧 **MCP Integration**: Built with Model Context Protocol for extensible tool integration
- 🧠 **AI-Powered**: Supports multiple LLM providers (WatsonX, OpenAI)

## Architecture

The application consists of two main agents:
- **TripPlanBuilderAgent**: Gathers user preferences and fetches attractions
- **TripPlanSummarizerAgent**: Creates comprehensive, formatted itineraries

## Prerequisites

- **Python**: 3.12 or higher
- **uv**: Install using curl or Homebrew from command-line
  ```bash
  # Using curl
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Using Homebrew (macOS)
  brew install uv
  ```

## Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd trip-planner-app/mcp-server
```

### 2. Install Dependencies

```bash
# Install dependencies from pyproject.toml
uv lock
uv sync
```

### 3. Environment Configuration

1. Copy the environment template:
   ```bash
   cp .env-copy .env
   ```

2. Update the `.env` file with your API credentials:
   ```env
   OPEN_TRIPMAP_API_KEY=your_tripmap_api_key_here
   WATSONX_URL=your_watsonx_url_here
   WATSONX_API_KEY=your_watsonx_api_key_here
   WATSONX_PROJECT_ID=your_watsonx_project_id_here
   WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
   ```

### 4. API Keys Setup

#### OpenTripMap API
- Sign up at [OpenTripMap Developer Portal](https://dev.opentripmap.org/login)
- Get your free API key
- Add it to your `.env` file

#### WatsonX API
- Access IBM WatsonX platform
- Obtain your API key, URL, and project ID
- Update the corresponding values in `.env`

## Usage

### Basic Usage

```bash
uv run trip_planner.py "I am John. I would like to plan a trip to Paris for 5 days"
```

### Query Format

Since this is not a conversational solution yet, use self-contained queries with the format:

```
I am <UserName>. I would like to plan a trip to <destination> for <duration>
```

### Examples

```bash
# 3-day trip to Munnar
uv run trip_planner.py "I am Renjith. I would like to make a 3 days trip to Munnar, Kerala."

# 7-day trip to Tokyo
uv run trip_planner.py "I am Sarah. I would like to plan a 7-day trip to Tokyo, Japan."

# Weekend trip to New York
uv run trip_planner.py "I am Mike. I would like to plan a weekend trip to New York City."
```

## Project Structure

```
mcp-server/
├── .env                 # Environment variables (create from .env-copy)
├── .env-copy           # Environment template
├── pyproject.toml      # Project dependencies
├── server.py           # MCP server with trip planning tools
├── trip_planner.py     # Main application entry point
├── uv.lock            # Dependency lock file
└── README.md          # This file
```

## Dependencies

- **autogen-agentchat**: Multi-agent conversation framework
- **autogen-ext**: Extensions for AutoGen
- **autogen-watsonx-client**: WatsonX integration
- **httpx**: HTTP client for API requests
- **mcp**: Model Context Protocol implementation

## User Preferences

The application includes a mock database for user preferences. Currently supported users:
- **renjith**: Interests in beaches, natural attractions, museums
- **bigblue**: Interests in cultural sites, sculptures

To add new users or modify preferences, update the `UserPreferencesDB` class in `server.py`.

## Customization

### Adding New Tools

To extend functionality, add new tools to `server.py`:

```python
@mcp.tool()
def your_new_tool(parameter: str) -> dict:
    """Description of your tool."""
    # Your implementation here
    return {"result": "data"}
```

### Switching LLM Providers

To use OpenAI instead of WatsonX, uncomment and configure the OpenAI client in `trip_planner.py`:

```python
openai_client = OpenAIChatCompletionClient(
    model="gpt-4o-2024-08-06",
    # api_key="sk-...", # Optional if OPENAI_API_KEY is set
)
```

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set in `.env`
2. **Location Not Found**: Verify the location name is spelled correctly
3. **No Attractions Returned**: Check if the location has attractions in OpenTripMap database

### Debug Mode

For debugging, you can modify the logging level in `server.py` or add print statements in `trip_planner.py`.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the application.

## Author

**Renjith Ramakrishnan**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.