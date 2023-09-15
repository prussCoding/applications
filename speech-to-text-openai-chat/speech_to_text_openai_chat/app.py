#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import openai
import logging
import argparse
import threading
import speech_recognition as sr

from typing import List
from attrs import define
from datetime import datetime
from dotenv import dotenv_values
from speech_recognition.exceptions import UnknownValueError

# Setting Parameters agrs for program to run
parser  = argparse.ArgumentParser( prog='Speech-to-Text and OpenAI Chat Interface',description='Process speech to text to be send to OpenAI chat for a response')
parser.add_argument('-d', '--duration', dest='duration', type=int, help='set the lenght of time to listen to user voice input')
parser.add_argument('-f', '--filename', dest='filename', type=str, help='set the conversation file.')

# Setting Params from Parser Arguments
params = parser.parse_args()

# Setting secrets for .env file
secrets = dotenv_values(".env")

# Configure logging
current_date = datetime.now().strftime("%Y-%m-%d")
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

# Global Variables 
text: str = None
conversation_dir: str = 'conversations'
duration: int = params.duration
filename: str = f'{conversation_dir}/{params.filename}'
mymodule = 'myapplication'

# Basic Configuration for Logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] -> %(message)s',
    level=logging.DEBUG,
    force=True,
    handlers=[
        logging.FileHandler(f'logs/{mymodule}-{str(current_date)}.log'),
        logging.StreamHandler()
    ]
)

# Initialize the speech recognizer
init_rec = sr.Recognizer()

def microphone_select():
    """
    Displays a list of available microphones and prompts the user to select a microphone index.
    
    Returns:
        int: The selected microphone index.
    """
    print('Microphone List:')
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  Microphone: [{index}] - {name}")
    return int(input('Select the mic input index (number)?'))


def countdown(t):
    """
    Countdown timer function.

    Args:
        t (int): Duration in seconds.

    Returns:
        None
    """
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1


def speech_to_text(type, content, duration, mic) -> str:
    """
    Converts spoken language to text using a microphone.

    Args:
        content (str): The context or instruction for the user.
        duration (int): The duration in seconds to record audio.

    Returns:
        str: The recognized text from the spoken audio.
    """
    print(f'{content}')
    
    with sr.Microphone(device_index=mic) as source:
        audio_data = init_rec.record(source, duration=duration)
        logging.info("Recognizing your text.............")
        try: 
            global text 
            text = init_rec.recognize_google(audio_data)
            with open(filename, 'a') as f:
                f.write(f'Speech ({type}):\n[{current_datetime}] {text}\n')
            logging.info(text)
        except UnknownValueError as e:
            logging.warning(e)
    
    logging.debug(f'Module: myspeechtotext -> Method: speechtotext() -> Value: {text}')


def run(type, duration, content, mic):
    """
    Run the speech to text conversion and countdown simultaneously using multi-threading.
    
    Args:
        type (str): The type of speech recognition to use.
        duration (int): The duration of the recording in seconds.
        content (str): The content to convert to text.
        mic (int): The microphone index to use for the recording.
    
    Returns:
        str: The converted text.
    """
    thread1 = threading.Thread(target=speech_to_text, kwargs={"content": content, "duration": duration, "mic": mic, "type": type})
    thread2 = threading.Thread(target=countdown, kwargs={"t": duration })
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    logging.debug(f'Module: myspeechtotext -> Method: run() -> Value: {text}')
    return text


@define
class Prompt:
    role: str
    content: str
    
    
    def render(self) -> None:
        """
        Render the Prompt as a dictionary.

        Returns:
            dict: A dictionary representing the Prompt.
        """
        return {"role": self.role, "content": self.content}

@define
class MessagePrompt:
    system: Prompt = []
    user: Prompt = []
    
    
    def render(self) -> None:
        """
        Render the MessagePrompt as a list of dictionaries.

        Returns:
            list: A list of dictionaries representing the MessagePrompt.
        """
        result = [prompt.render() for prompt in [self.system, self.user]]
        logging.debug(f'Class: MessagePrompt -> Method: render() -> Value: {result}')
        return result


@define
class ChatPrompt:
    api_key: str
    engine: str
    message: MessagePrompt
    response: List[str] = None
    
    
    def chat_completion(self):
        """
        Perform a chat completion using OpenAI's API.

        Returns:
            bool: True if the API call was successful, False otherwise.
        """
        if not self.api_key:
            return False
        openai.api_key = self.api_key
        self.response = openai.ChatCompletion.create(
            model=self.engine,
            messages=self.message.render()
        )
        logging.debug(f'Class: ChatPrompt -> Method: chat_completion() -> Value: {self.response}')
        return True
    
      
    def render(self) -> None:
        """
        Render the ChatPrompt and perform the chat completion.

        Returns:
            None
        """
        self.chat_completion()
        return True


def main():
    """
    Run the main conversational loop, prompting the user for input and generating a response.

    Returns:
        None
    """
    mic = microphone_select()
    isMessageReady: bool = False
    while not isMessageReady:
        history_conversation = ''
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                history_conversation = f.read()
        logging.debug(f'Method func(main) -> {history_conversation}')
        context = run('context', duration, 'Speak the system instruction or guidance to the AI model', mic )
        question = run('question', duration, "Speak the user's input or query", mic)
        if input('Is both system and user input ready to submit (y/n)?') == 'y':
            isMessageReady = True

            mysystem = Prompt(role='system', content=f'{history_conversation}\n{context}')
            myuser = Prompt(role='user', content=question)
            
            mymessage = MessagePrompt(
                system=mysystem,
                user=myuser
            )
            
            chat = ChatPrompt(
                api_key=secrets['API_KEY'],
                engine='gpt-3.5-turbo',
                message=mymessage,
            )
            
            chat.render()
            content = chat.response["choices"][0]["message"]["content"]
            with open(filename, 'a') as f:
                f.write(f'Response (chat):\n[{current_datetime}] {content}\n')
            logging.info(f'Chat Response: {content}')

  
if __name__ == '__main__':
    main()
