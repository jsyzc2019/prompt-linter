from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from langchain.schema import SystemMessage
from langchain.agents import OpenAIFunctionsAgent
from langchain.agents import AgentExecutor

# llm
llm = ChatOpenAI(temperature=0)

# tools
def get_word_length(word: str) -> int:
    return len(word)

tools = [
    Tool.from_function(
        func=get_word_length,
        name="get_word_length",
        description="Returns the length of a word."
    )
]

# prompt
system_message = SystemMessage(
    content="You are very powerful assistant, but bad at calculating lengths of words."
)
prompt = OpenAIFunctionsAgent.create_prompt(system_message=system_message)

# create an agent
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)

# create an agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# run the agent executor
result = agent_executor.run("how many letters in the word 'weekly-practice'?")
print(result)
