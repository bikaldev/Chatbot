from decision import DecisionChain
from conversational import ConversationalForm
from rag_chat import RAGChain

class ResponseGenerator:
    def __init__(self):
        self.decision_chain = DecisionChain()
        self.conv_form = ConversationalForm()
        self.rag_chat = RAGChain()

    def generator(self):
        while True:
            user_input = yield
            keyword = self.decision_chain.decide(user_input)
            if(keyword.strip() == "normal_chat"):
                # rag chat
                yield self.rag_chat.run(user_input).content
            else:
                conv_generator = self.conv_form.conversational_loop()
                for conv_response in conv_generator:
                    conv_response = conv_generator.send(user_input)
                    if("[EOF]" not in conv_response):
                        yield conv_response
                        user_input = yield
                    else:
                        conv_response = conv_response.replace("[EOF]","")
                        yield conv_response

                conv_generator.close()


def generate_text(text):
    for char in text:
        yield char

