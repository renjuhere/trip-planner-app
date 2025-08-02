from asyncio import run
import os
import sys
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

# Constants
MAX_MESSAGES = 25
MAX_TURNS = 10
DEFAULT_QUERY = "I am Renjith. I would like to make a 3 days trip to Munnar, Kerala."

# Load environment variables
try:
    load_dotenv()
except (IOError, OSError) as e:
    print(f"Warning: Failed to load environment variables: {e}")
except Exception as e:
    print(f"Unexpected error loading environment variables: {e}")
    raise


async def initialize_tools():
    """Initialize MCP tools"""
    # Get MCP tools
    mcp_server = StdioServerParams(command="mcp", args=["run", "server.py"])
    tools = await mcp_server_tools(mcp_server)
    
    return tools

async def initialize_model_client():
    """Initialize LLM model client"""

    # Validate required environment variables
    required_vars = ["WATSONX_MODEL_ID", "WATSONX_API_KEY", "WATSONX_URL", "WATSONX_PROJECT_ID"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

    # Create Watsonx client
    wx_config = WatsonxClientConfiguration(
        model_id=os.environ.get("WATSONX_MODEL_ID"),
        api_key=os.environ.get("WATSONX_API_KEY"),
        url=os.environ.get("WATSONX_URL"),
        project_id=os.environ.get("WATSONX_PROJECT_ID"),
    )
    model_client = WatsonXChatCompletionClient(**wx_config)

    # If you prefer OpenAI Client, follow the below approach:
    #
    # openai_client = OpenAIChatCompletionClient(
    #     model="gpt-4o-2024-08-06",
    #     # api_key="sk-...", # Optional if you have an OPENAI_API_KEY environment variable set.
    # )

    return model_client

def create_agents(model_client, tools):
    """Create all trip planning agents."""

    trip_plan_builder_agent_prompt = """
    You are a trip planning agent. You will execute all the following tasks in sequence.

    Task-1. Use tool to get trip preferences of the User
    Task-2. Use tool to get attractions based on User's preferences
    """

    trip_plan_builder_agent = AssistantAgent(
        name="TripPlanBuilderAgent",
        description="An agent for planning Trips. This should be the first agent to engage for a new task.",
        model_client=model_client,
        system_message=trip_plan_builder_agent_prompt,
        tools=tools,
        reflect_on_tool_use=False,
        max_tool_iterations=len(tools) # this is important to override the default (1) and ensure all tools are used.
    )

    trip_plan_summarizer_prompt = """Build a comprehensive trip itinerary and end with TERMINATE keyword.

    Create a well-formatted, user-friendly response using this structure:

    🌟 **TRAVEL ITINERARY FOR [USER NAME]**

    📍 **DESTINATION:** [Location]
    📅 **DURATION:** [Number of days]
    ⏰ **TRAVEL DATES:** [If provided]

    ---

    🎯 **YOUR PREFERENCES:**
    • [List user's travel interests/preferences]

    ---

    🏛️ **RECOMMENDED ATTRACTIONS:**

    **Cultural & Historical:**
    • [Attraction name] - [Brief description]

    **Natural & Scenic:**
    • [Attraction name] - [Brief description]

    **Activities & Entertainment:**
    • [Attraction name] - [Brief description]

    ---

    📋 **DETAILED ITINERARY:**

    **Day 1: [Theme/Focus]**
    🌅 Morning (9:00 AM - 12:00 PM)
    • [Activity/Location] - [Duration, tips]

    🌞 Afternoon (1:00 PM - 5:00 PM)
    • [Activity/Location] - [Duration, tips]

    🌙 Evening (6:00 PM onwards)
    • [Activity/Location] - [Duration, tips]

    **Day 2: [Theme/Focus]**
    [Same format as Day 1]

    **Day 3: [Theme/Focus]**
    [Same format as Day 1]

    ---

    💡 **TRAVEL TIPS:**
    • [Practical advice for the destination]
    • [Best time to visit attractions]
    • [Local transportation suggestions]

    ---

    ✨ **Have an amazing trip!**

    TERMINATE"""

    trip_plan_summarizer_agent = AssistantAgent(
        name="TripPlanSummarizerAgent",
        description="An agent for summarizing the trip plan.",
        model_client=model_client,
        system_message=trip_plan_summarizer_prompt,
        reflect_on_tool_use=False
    )

    return [trip_plan_builder_agent, trip_plan_summarizer_agent]

def create_team(agents):
    """Create the agent team with termination conditions."""
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(max_messages=MAX_MESSAGES)

    return RoundRobinGroupChat(
        agents,
        description="Assist Users to plan trip by co-ordinating a team of agents.",
        termination_condition=termination,
        max_turns=MAX_TURNS,
        emit_team_events=False
    )

async def main(query: str) -> None:
    """Main function to run the trip planning system."""
    try:
        tools = await initialize_tools()
        model_client = await initialize_model_client()
        agents = create_agents(model_client, tools)
        agent_team = create_team(agents)
        stream = agent_team.run_stream(task=query)

        # stream = agents[0].run_stream(task=query)
        await Console(stream)
        
    except Exception as e:
        print(f"Failed to initialize: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        print("No query provided. Using default query.")
        query = DEFAULT_QUERY
    run(main(query=query))