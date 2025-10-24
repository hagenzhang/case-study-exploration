import asyncio
from typing import Optional
from contextlib import AsyncExitStack


from mcp import ClientSession
from mcp.shared.exceptions import McpError
from mcp.client.streamable_http import streamablehttp_client as http_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env
               # this includes our anthropic API key

class MCPClient:
    """
    The MCP Client class initializes with session management and API clients.
    We use AsyncExitStack for proper resource management.
    Configures Anthropic with the API key from environment variables for Claude access.
    """
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Optional getter for the MCP session id when using streamable transports
        self.get_session_id = None
        self.anthropic = Anthropic()
        
        

    # Server Connection Management
    # Method to connect to an MCP server via HTTP
    async def connect_to_server(self, server_url: str):
        """Connect to an MCP server via HTTP
        
        Sets up proper communication channels
        Initializes the session and lists available tools

        Args:
            server_url: The base URL of the running MCP server (e.g. http://localhost:8000)
        """
        # streamablehttp_client yields (read_stream, write_stream, get_session_id)
        read_stream, write_stream, get_session_id = await self.exit_stack.enter_async_context(
            http_client(server_url)
        )
        # store the session id getter for possible later use
        self.get_session_id = get_session_id

        # ClientSession expects (read_stream, write_stream)
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )

        try:
            await self.session.initialize()
        except McpError as e:
            # Provide a clearer error message when the server rejects/terminates the session
            print(f"Failed to initialize MCP session: {e}")
            raise

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])


    # Adding Query Processing Logic:
    # Core functionality for processing quries and handling tool calls
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools
        
        Maintains conversation context
        Handles Claude’s responses and tool calls
        Manages the message flow between Claude and tools
        Combines results into a coherent response
        """
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        assistant_message_content = []
        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                assistant_message_content.append(content)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input

                # Execute tool call
                result = await self.session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                assistant_message_content.append(content)
                messages.append({
                    "role": "assistant",
                    "content": assistant_message_content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result.content
                        }
                    ]
                })

                # Get next response from ClaudeWhat
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    messages=messages,
                    tools=available_tools
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    
    
    # Interactive Chat Interface
    # Adding in a chat loop and cleanup functionality
    async def chat_loop(self):
        """Run an interactive chat loop
        
        Provides a simple command-line interface
        Handles user input and displays responses
        Includes basic error handling
        Allows graceful exit
        """
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resource
        
        Proper cleanup of resources
        Error handling for connection issues
        Graceful shutdown procedures
        """
        await self.exit_stack.aclose()


# Main Execution Block
# Entry point to run the client

# Set the MCP server URL here
SERVER_URL = "http://localhost:8080/mcp/"

async def main():
    client = MCPClient()
    try:
        await client.connect_to_server(SERVER_URL)
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import requests
    
    payload = {
        "jsonrpc": "2.0",
        "method": "ping",
        "params": {},
        "id": 1
    }

    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json"
    }

    response = requests.post(SERVER_URL, json=payload, headers=headers)
    print("Request sent:")
    print(payload)
    print("Response received:")
    print(response.text)

    asyncio.run(main())

"""
Common Customizations:

1) Tool Handling:
    - Modify process_query to add custom tool handling logic
    - Add custom error handling for tool calls
    - Implement tool-specific response formatting
2) Response Processing:
    - Customize how tools are formatted
    - Add response filtering or transformation
    - Implement custom logging
3) User Interface:
    - Add a GUI or web interface
    - Implement rich console output
    - Add command history or autocomplete
    
    
    
    
Note for Initialization:
The client MUST initiate this phase by sending an initialize request containing:
- Protocol version supported
- Client capabilities
- Client implementation information
Example:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "roots": {
        "listChanged": true
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ExampleClient",
      "version": "1.0.0"
    }
  }
}

The server MUST respond with its own capabilities and information:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-03-26",
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": true
      },
      "resources": {
        "subscribe": true,
        "listChanged": true
      },
      "tools": {
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "version": "1.0.0"
    },
    "instructions": "Optional instructions for the client"
  }
}

After successful initialization, the client MUST send an initialized notification to indicate it is ready to begin normal operations:
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
"""