from langchain_groq import ChatGroq
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

from tools import book_appointment_tool, validate_email_tool, validate_phone_tool

class ConversationalForm:
    def __init__(self):
        model = ChatGroq(
            model='llama3-70b-8192',
            temperature=0.0,
            max_retries=2
            )


        tools = [
            Tool(name="ValidateEmail", func=validate_email_tool, description="Validate email format."),
            Tool(name="ValidatePhone", func=validate_phone_tool, description="Validate phone number format."),
            Tool(name="BookAppointment", func=book_appointment_tool, description="Book an appointment using a date hint.")
        ]

        # Define a Custom Prompt
        custom_prompt = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad", "chat_history"],
        template="""
        Perform the given task as best you can. You have access to the following tools:

        {tools}

        Task: Your task is to determine the next step in this conversational flow. You will be given the conversation history and current user input. The flow is supposed to be as follows:
        - You should ask the user for name.
        - The user supplies the name.
        - You should ask the user for email.
        - The user supplies the email.
        - You verify the email using tool and provide feedback & ask again if invalid.
        - You ask the user for phone number.
        - You verify the phone number using tool and provide feedback & ask again if invalid.
        - You ask the user if they want to book an appointment.
        - You provides response.
        - If positive response comes from user, you use a tool to book appointment.
        - The conversation ends. Strictly mark the end of conversation with a `[EOF]` tag.

        Use the following format:

        ConversationHistory: the conversation until now
        CurrentInput: the current user input
        Thought: you should always think about what to do.
        (If action is necessary) 
        
            Action: the action to take should be one of [{tool_names}] and the exact format of input to send to the tool
            Action Input: the input to the action
            Observation: the result of the action
            Analysis: analysis of whether the observation is as expected
            Feedback: If the observation is as expected no feedback necessary. Else the final answer is the feedback to the user.
                
        Next Question: the next question to ask the user
        Final Answer: the final answer is feedback(if there is a feedback) followed by the next question.
        Begin!

        Conversational History: {chat_history}
        Current User Input: {input}
        Thought:{agent_scratchpad}
        """
        )

        # # Create an LLM Chain for the custom prompt
        # llm_chain = custom_prompt | model
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        # Create a Custom Agent
        agent = create_react_agent(model, tools, custom_prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=self.memory, handle_parsing_errors=True)

    def conversational_loop(self):
        while True:
            user_input = yield
            response = self.agent_executor.invoke({'input': user_input})['output']
            if("[EOF]" in response):
                yield response
                return
            yield response