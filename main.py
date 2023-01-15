from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import os
import openai
from utils.ConfigManager  import Manager
config_manager = Manager()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'   

class WhatsAppIntegrationViaTwilio:
    def __init__(self):
        self.account_sid =config_manager.read_config("Default-Config","twilio_account_sid")
        self.auth_token = config_manager.read_config("Default-Config","twilio_auth_token")
        self.account_sid = 'ACd9ab61c140c4ccde89119344fe93d49e'  # Twilio Account SID
        self.auth_token = 'c5d0072213aaf613fb73f77889114780'     # Twilio Account Auth Token
        self.client = Client(self.account_sid, self.auth_token)

    def sendMessage(self,body_mess,numberlist):
        print(numberlist)
        message=""
        for number in numberlist:
            print(number)
            try:
                message = self.client.messages.create(
                                body=body_mess,
                                from_='whatsapp:+14155238886',
                                to=number)
            except TwilioRestException as ex:
                print(ex)
        
            #print(message.sid)       
      
    
    

class GPTHandler:
    def __init__(self, initializer_text):
        pass
        self.app_secret = config_manager.read_config("Default-Config","app_secret")
        self.open_api_key = config_manager.read_config("Default-Config","api_key")
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.app_secret 
        openai.api_key = self.open_api_key 
        response = openai.Completion.create(model="text-davinci-003", prompt=initializer_text, temperature=0, max_tokens=7)
        self.start_chat_log = initializer_text

    def ask(self,question, chat_log=None):
        if chat_log is None:
            chat_log = self.start_chat_log
        prompt = question
        print(prompt)
        response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=1024)
        answer = response.choices[0].text.strip()
        return answer

    def append_interaction_to_chat_log(self,question, answer, chat_log=None):
        if chat_log is None:
            chat_log = self.start_chat_log
        return f'{chat_log}Human: {question}\nAI: {answer}\n'



# TWILIO

starter="Hello "
whatspp = WhatsAppIntegrationViaTwilio()
gpthandler = GPTHandler(initializer_text=starter)


                                                     # Print Response
@app.route('/',methods=['POST'])
def hello():
    print("The arguments are ", request.args)
    payload = request.form
    print("The payload is ", payload)
    print("I am Alive high five")
    incoming_msg = request.values.get('Body', '').lower()
    print(incoming_msg)
    incoming_msg = request.data
    print(incoming_msg)
    return("Hello its working")

@app.route('/test', methods=['POST'])
def test():
    answer="No response"
    print("test fired")
    incoming_msg = request.values.get('Body', '').lower()
    if incoming_msg == "":
        incoming_msg = "How are we today"
    #incoming_msg = request.data 
    print(incoming_msg)
    if incoming_msg:
        chat_log = session.get('chat_log')
        print("Chat Log is {}".format(chat_log))
        answer = gpthandler.ask(incoming_msg, chat_log)
        print(answer)
    #incoming_msg = request.values['Body']
    #print(incoming_msg)
    return(answer)

@app.route('/bot', methods=['POST'])
def bot():
    payload = request.form
    print(payload)
    numberlist = [payload.get("From")]
    print(numberlist)
    incoming_msg = payload.get('Body')
    print(incoming_msg)
    answer="Sorry the bot just got busty..."
    if payload.get('Body')!= "":
        if incoming_msg:
            chat_log = session.get('chat_log')
            answer = gpthandler.ask(incoming_msg, chat_log)
            print(answer)
            session['chat_log'] = gpthandler.append_interaction_to_chat_log(incoming_msg, answer, chat_log)
            whatspp.sendMessage(answer,numberlist)
        else:
            whatspp.sendMessage("Message Cannot Be Empty!")
            print("Message Is Empty")
    return(answer)


if __name__ == '__main__':
    app.run()