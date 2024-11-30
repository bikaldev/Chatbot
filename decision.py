from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate

class DecisionChain:
    def __init__(self):
        model = ChatGroq(
            model='llama3-70b-8192',
            temperature=0.0,
            max_retries=2
        )

        prompt = PromptTemplate(input_variables=["input"], template="""
        Based on the user input given below in triple backticks you are to return one of three options listed below.
        input: ```{input}```
        options: 
        A) conversational_form : This option is to be selected if the input contains a request for a callback (e.g, "Please contact me", "can someone call me", "can i leave my information for contact", etc) or if the user wants his/her recorded information in the conversational form to be displayed or discussed(e.g, "can you display my contact information?", "what is my name/email/phone number/appointment date ?").
        B) book_appoinment : This options is to be selected if the input contains a request to book appointment.
        C) normal_chat: This option is to be selected if the options A) and B) do not qualify.

        Note: Do not return any introductory or explanatory text, just return the option key "conversational_form", "book_appointment" or "normal_chat".
        """ )

        self.decision_chain = prompt | model

    def decide(self, input):
        return self.decision_chain.invoke(input=input).content

