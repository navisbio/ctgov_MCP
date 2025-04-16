#!/usr/bin/env python3

"""
Example script demonstrating how to use the AACT Clinical Trials MCP server with Semantic Kernel.
"""

import os
import asyncio
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

# Load environment variables
load_dotenv()

# System message for the chatbot
SYSTEM_MESSAGE = """
You are a clinical research assistant that can help users analyze clinical trial data from ClinicalTrials.gov.
You can list the available tables, describe their structure, and run SQL queries to analyze the data.
You can also save important findings for later reference.

Always use the available tools when needed:
- list_tables: Use this to see all available tables in the database
- describe_table: Use this to see the columns and structure of a specific table
- read_query: Use this to run SQL queries against the database
- append_insight: Use this to save important findings you discover

The database structure follows the AACT database schema, with tables in the 'ctgov' schema.
"""

async def create_kernel() -> Kernel:
    """Create and configure the kernel with the AACT Clinical Trials MCP plugin."""
    kernel = Kernel()
    
    # Configure AI service - replace with your preferred service
    # This example uses OpenAI, but you can use any service that supports function calling
    import openai
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Create chat completion service
    chat_service = OpenAIChatCompletion(
        ai_model_id="gpt-4o",
        api_key=api_key,
        completion_parameters={
            "function_choice_behavior": FunctionChoiceBehavior.Auto()
        }
    )
    
    kernel.add_service(chat_service)
    
    # Create AACT Clinical Trials MCP plugin
    aact_mcp = MCPStdioPlugin(
        name="aact",
        description="Clinical Trials Database Plugin",
        command="uvx",
        args=["mcp-server-aact"],
        env={
            "DB_USER": os.environ.get("DB_USER"),
            "DB_PASSWORD": os.environ.get("DB_PASSWORD")
        }
    )
    
    # Add the plugin to the kernel
    kernel.add_plugin(aact_mcp)
    
    return kernel

async def chat_loop(kernel: Kernel):
    """Run an interactive chat loop with the Clinical Trials assistant."""
    # Create a chat history with the system message
    history = ChatHistory()
    history.add_system_message(SYSTEM_MESSAGE)
    
    print("Clinical Trials Data Assistant")
    print("Type 'exit' to quit")
    print()
    
    while True:
        # Get user input
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        # Add user message to history
        history.add_user_message(user_input)
        
        try:
            # Get chat service
            chat_service = kernel.get_service()
            
            # Generate assistant response
            print("Assistant: ", end="", flush=True)
            result = await chat_service.get_chat_message_content(
                history, 
                kernel=kernel
            )
            
            # Add assistant response to history
            if result:
                print(f"{result}")
                history.add_assistant_message(str(result))
            else:
                print("No response generated.")
            
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("\nGoodbye!")

async def main():
    """Main entry point."""
    kernel = await create_kernel()
    
    # Use the context manager to properly manage the plugin lifecycle
    async with kernel.get_plugin("aact")._plugin:
        await chat_loop(kernel)

if __name__ == "__main__":
    asyncio.run(main()) 