import setuptools
import subprocess
import os
import venv

# Create directories for logs and conversations
app_dir ='.'
os.makedirs(f'{app_dir}/logs', exist_ok=True)
os.makedirs(f'{app_dir}/conversations', exist_ok=True)

# Create a .env file for your OPENAI KEY
if not os.path.isfile(f'{app_dir}/.env'):
    with open(f'{app_dir}/.env', 'a') as f:
        f.write('# OpenAI Configuration\n')
        f.write('API_KEY=qwerty12345\n\n')
        f.write('# Pyttsx3 Configuraton')
        f.write('PYTTSX_VOICE_ID=1      # 0=Male or 1=Female\n')
        f.write('PYTTSX_VOLUME=0.5   # setting up volume level  between 0 and 1\n')
        f.write('PYTTSX_RATE=125     # setting up new voice rate\n')
    
setuptools.setup(
    name="speech-to-text-openai-chat",
    version="2023.09.15",
    author="Perrie Russell",
    author_email="perussell0815@gmail.com",
    description="Speech-to-Text and OpenAI Chat Interface",
    packages=setuptools.find_packages(),
    install_requires=[
        'openai',
        'attrs',
        'python-dotenv',
        'SpeechRecognition',
        'pyaudio',
        'pyttsx3',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'speech-to-text-openai-chat = speech_to_text_openai_chat.app:main',
        ],
    },
    python_requires=">=3.6",
)


