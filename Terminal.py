from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from langchain.memory import CassandraChatMessageHistory, ConversationBufferMemory
from langchain.llms import OpenAI
from langchain import LLMChain, PromptTemplate
import json

cloud_config= {
  'secure_connect_bundle': 'secure-connect-choose-your-own-adventure.zip'
}

with open("Your_files.json") as f:
    secrets = json.load(f)

CLIENT_ID = secrets["clientId"]
CLIENT_SECRET = secrets["secret"]
ASTRA_DB_KEYSPACE = ""
OPENAI_API_KEY = ""

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()

message_history = CassandraChatMessageHistory(
    session_id="anything",
    session=session,
    keyspace=ASTRA_DB_KEYSPACE,
    ttl_seconds=3600
)

message_history.clear()

cass_buff_memory = ConversationBufferMemory(
    memory_key="chat_history",
    chat_memory=message_history
)

template = ''' "You are now a terminal/virtual guide for a hacker that is helping the CIA. you will help this CIA agent navigate "The Terminal" as they find a way to get rid of the virus You must guide this agent through riddles, challanges, choices, and consequences, dynamically adapting the tale based on the agents Decisions. Your goal is to create a branching narrative experience where choice leads to a new path, ultimately determining the Agent's fate.

Here are some rules to follow:

This game is Eerie and somewhat trilling.
Start by asking the player their name and then start the game.
Have a few paths that lead to success. If the User wins generate a response that explains the win and ends in the text: "The End.", I Will search for this text to end the game.
Have some paths that lead to the Death. If the User dies generate a response that explains the death and ends in the text: "The End.", I Will search for this text to end the game."
Here is the chat history, use this to understand what to say next: {chat_history} Human: {human_input} AI:
'''

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)
llm_chain = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=cass_buff_memory
)

choice = "start"

while True:
    response = llm_chain.predict(human_input=choice)
    print(response.strip())

    if "The End." in response:
        break

    choice = input("Your reply: ")