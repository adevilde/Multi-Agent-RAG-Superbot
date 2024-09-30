import autogen
from rich import print
import chainlit as cl
from typing_extensions import Annotated
from chainlit.input_widget import (
   Select, Slider, Switch)
from autogen import AssistantAgent, UserProxyAgent
from utils.chainlit_agents import ChainlitUserProxyAgent, ChainlitAssistantAgent
from graphrag.query.cli import run_global_search, run_local_search

# LLama3 LLM from Lite-LLM Server for Agents #
llm_config_autogen = {
    "seed": 40,  # change the seed for different trials
    "temperature": 0,
    "config_list": [{"model": "litellm", 
                     "base_url": "http://0.0.0.0:4000/", 
                     'api_key': 'ollama'},
    ],
    "timeout": 60000,
}

async def ask_helper(func, **kwargs):
    res = await func(**kwargs).send()
    while not res:
        res = await func(**kwargs).send()
    return res

# class ChainlitAssistantAgent(AssistantAgent):
#     async def a_send(
#         self,
#         message: Union[Dict, str],
#         recipient: Agent,
#         request_reply: Optional[bool] = None,
#         silent: Optional[bool] = False,
#     ) -> bool:
#         await cl.Message(
#             content=f'*Sending message to "{recipient.name}":*\n\n{message}',
#             author="AssistantAgent",
#         ).send()
#         await super(ChainlitAssistantAgent, self).a_send(
#             message=message,
#             recipient=recipient,
#             request_reply=request_reply,
#             silent=silent,
#         )


# class ChainlitUserProxyAgent(UserProxyAgent):
#     async def get_human_input(self, prompt: str) -> str:
#         if prompt.startswith(
#             "Provide feedback to assistant. Press enter to skip and use auto-reply"
#         ):
#             res = await ask_helper(
#                 cl.AskActionMessage,
#                 content="Continue or provide feedback?",
#                 actions=[
#                         cl.Action(
#                             name="continue", value="continue", label="✅ Continue"
#                         ),
#                     cl.Action(
#                             name="feedback",
#                             value="feedback",
#                             label="💬 Provide feedback",
#                         ),
#                     cl.Action(
#                             name="exit",
#                             value="exit",
#                             label="🔚 Exit Conversation"
#                         ),
#                 ],
#             )
#             if res.get("value") == "continue":
#                 return ""
#             if res.get("value") == "exit":
#                 return "exit"

#         reply = await ask_helper(
#             cl.AskUserMessage, content=prompt, timeout=60)

#         return reply["content"].strip()

#     async def a_send(
#         self,
#         message: Union[Dict, str],
#         recipient: Agent,
#         request_reply: Optional[bool] = None,
#         silent: Optional[bool] = False,
#     ):
#         await cl.Message(
#             content=f'*Sending message to "{recipient.name}"*:\n\n{message}',
#             author="UserProxyAgent",
#         ).send()
#         await super(ChainlitUserProxyAgent, self).a_send(
#             message=message,
#             recipient=recipient,
#             request_reply=request_reply,
#             silent=silent,
#         )


@cl.on_chat_start
async def on_chat_start():
    try:
        settings = await cl.ChatSettings(
            [
                Switch(
                    id="search_type",
                    label="(GraphRAG) Local Search",
                    initial=True,
                ),
                Select(
                    id="content_type",
                    label="(GraphRAG) Content Type",
                    options=[
                        "prioritized list", 
                        "single paragraph", 
                        "multiple paragraphs", 
                        "multiple-page report"
                    ],
                    initial_index=0,
                ),
                Slider(
                    id="community",
                    label="(GraphRAG) Community Level",
                    initial=0,
                    min=0,
                    max=2,
                    step=1,
                ),


            ]
        ).send()

        search_type = settings.get("search_type")
        content_type = settings.get("content_type")
        community = settings.get("community")

        cl.user_session.set("search_type", search_type)
        cl.user_session.set("content_type", content_type)
        cl.user_session.set("community", community)

        retriever = AssistantAgent(
            name="retriever",
            llm_config=llm_config_autogen,
            system_message="""Only execute the function query_graphRAG to look for context. 
                    Output 'TERMINATE' when an answer has been provided.""",
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER",
            description="Retriever Agent",
        )

        user_proxy = ChainlitUserProxyAgent(
            "user_proxy",
            human_input_mode="ALWAYS",
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            llm_config=llm_config_autogen,
            code_execution_config=False,
            system_message='''Please provide feedback to the assistant. Interact with the retriever to provide any context.''',
            description="User Proxy Agent",
        )

        print("Agents created successfully.")

        cl.user_session.set("retriever", retriever)
        cl.user_session.set("user_proxy", user_proxy)

        msg = cl.Message(content=f"""Hello! What task would you like to get done today?      
                     """, 
                     author="User_Proxy")
        
        await msg.send()

        print("Message sent.")

    except Exception as e:
        print(f"Error: {e}")
        pass


@cl.on_settings_update
async def setup_agents(settings):
    response_type = settings.get("search_type")
    content_type = settings.get("content_type")
    community = settings.get("community")
    cl.user_session.set("search_type", response_type)
    cl.user_session.set("content_type", content_type)
    cl.user_session.set("community", community)
    print(f"Settings updated: {response_type}, {content_type}, {community}")


@cl.on_message
async def conversation(message: cl.Message):
    