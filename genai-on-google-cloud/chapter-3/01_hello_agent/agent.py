# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Hello Agent - From Zero to Agent in 7 Lines

This is the simplest possible ADK agent, matching Example 3-1 from
Chapter 3. It demonstrates the minimal configuration needed to create
a conversational agent:

1. Import the Agent class
2. Define the agent with name, model, and instruction
3. That's it!

The ADK runtime handles everything else:
- Session management
- Conversation history
- State persistence
- Event streaming

Theme: SmartHome Customer Support (consistent with Chapter 3)
"""

from google.adk.agents import Agent

# Example 3-1: The simplest agent definition - just 7 lines!
root_agent = Agent(
    name="CustomerSupportAgent",
    model="gemini-2.5-flash",
    instruction="You help customers with their SmartHome products."
)
