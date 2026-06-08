#!/usr/bin/env python3
"""
MiMi - Enhanced AI Agent
Main entry point with automatic configuration system detection.
"""

import os
import typer
import sys
import signal
from rich import print
from cli.agent import Agent
from config.config import config_manager

def handler(signum, frame):
    print("\n Use 'quit' command to exit.")
                    
def main():
    print("\n" + "="*50)
    print("🤖 MiMi AI Assistant")
    print("="*50)
    try:
        prompt = config_manager.get("agent.prompt", "User> ")
        model = config_manager.get("model.name", "Not configured")
        sessions_dir = config_manager.get("agent.session_dir")
        
        print(f"\n🚀 Starting with:")
        print(f"  • Model: {model}")
        print(f"  • Prompt: {prompt}")
        
        # Start agent
        signal.signal(signal.SIGINT, handler)
        agent = Agent(prompt, sessions_dir)
        agent.run()
            
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("💡 Try running: python create_user_config.py")
        sys.exit(1)

if __name__ == "__main__":
    typer.run(main)