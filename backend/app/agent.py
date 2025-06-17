import re
from graph_logic.graph import graph
from graph_logic.llm import chain, llm
from langchain.tools import Tool
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.conversational_chat.prompt import (
    FORMAT_INSTRUCTIONS,
    PREFIX,
    SUFFIX,
    TEMPLATE_TOOL_RESPONSE
)
import json
from langchain_core.runnables.history import RunnableWithMessageHistory
# Default template from langchain import hub
from langchain_core.prompts import PromptTemplate
from langchain_core.agents import AgentAction, AgentFinish
from utils import get_session_id
from tools.vector import get_resume
from tools.cypher import cypher_qa
from langchain_core.output_parsers.base import BaseOutputParser


class AgentOutputParser(BaseOutputParser):
    """
    A parser class to extract action and action input from LLM
    output text. It processes the text by removing code block
    delimiters and extracts the necessary information
    """
    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> dict:
        cleaned_output = text.strip()
        print("-----------------------------------------")
        print(f"CLEANED OUTPUT IS: {type(cleaned_output)}")
        print(cleaned_output)

        if cleaned_output is None:
            return {"action": "General Chat", "action_input": ""}
        thought_pattern = r'(Thought:)([ \w.?`!,?\'\n]*)'
        action_pattern = r'([ \w.?`!,?\'\n]*)(Action:)([ \w.!?\n]*)(Action Input:)([ \w.\':`!{}"?\n]*)'
        observation_pat = r"([ \w.?`!,?\'\n]*)(Observation:)([ \w`.?!,?'\n]*)"
        final_answer_pat = r"([ \w.?`!,?\'\n]*)(Final Answer:)([ \w.?`!,?\'\n]*)"
        thought_result = re.search(thought_pattern, cleaned_output)
        actions_result = re.search(action_pattern, cleaned_output)
        obs_result = re.search(observation_pat, cleaned_output)
        final_answer = re.search(final_answer_pat, cleaned_output)
        action = action_input = None
        log = cleaned_output if obs_result is None else obs_result.group(3)
        if actions_result is not None:
            print(actions_result.groups())
            action = actions_result.group(3).replace("\n", "").strip()
            action = re.findall(r"[\w ]+", action)[0]
            if len(actions_result.groups()) < 4:
                action_input = ""
            else:
                action_input = actions_result.group(5).replace("\n", "").strip()
                action_input = ', '.join(re.findall(r"[\w ]+", action_input))
        if action and action_input:
            action_input = action_input.replace('{"name":}', "").replace('"', "")
            return AgentAction(log=log,
                               tool=action,
                               tool_input=action_input)
        if final_answer is not None:
            final_ans = final_answer.group(3).strip()
            return AgentFinish(log=log, return_values={"output": final_ans})
        if actions_result is None:
            return AgentFinish(log=log, return_values={"output": cleaned_output})
        if 'Do I need to use a tool?' not in thought_result.group(2).strip():
            return AgentFinish(log=log, return_values={"output": cleaned_output})


# Create a set of tools
tools = [
    Tool.from_function(
        name="General Chat",
        description="For general chat not covered by other tools",
        func=chain.invoke,
    ),
    Tool.from_function(
        name="Resume Search",
        description="When you need to find information about experience"
                    "resume, tech stack, and skillset",
        func=get_resume,
    ),
    Tool.from_function(
        name="Employee information",
        description="Provide information about employees, clients, "
                    "projects, directors, and organization questions"
                    "and who works for who information using Cypher",
        func=cypher_qa
    )
]


# Create chat history callback
def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Create the agent
agent_prompt = PromptTemplate.from_template("""
You are an Employee of Apex Systems that is also a Resource Management expert providing information about Apex Systems employees and resumes.
Be as helpful as possible and return synthesized, concise and brief information.
Do not answer any questions that do not relate to Apex Systems, Employees, Associates, Managers, Supervisors, Sr, Tech Leads or Directors.

Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.


TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please, PLEASE ALWAYS use the following format:

```
Thought: Do I need to use a tool? Yes.
Action: the action to take, should be one of these tools: [{tool_names}]
Action Input: the input to the action.
Observation: the result of the action.
... (this Thought/Action/Action Input/Observation can repeat 2 times)
```
When you have a response, or answer you MUST ALWAYS use the format:

```
Thought: Do I need to use a tool? No.
Final Answer: [your response here]
```

Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")  # Default agent hub.pull("hwchase17/react-chat")
agent = create_react_agent(llm, tools, agent_prompt, stop_sequence=True,
                           output_parser=AgentOutputParser())
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    )

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)


# Create a handler to call the agent
def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """
    response = chat_agent.invoke(
            {"input": user_input},
            {"configurable": {"session_id": get_session_id()}},)
    return response['output']
