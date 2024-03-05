from argparse import ArgumentParser
import youtube_dl
from pathlib import Path
import os
import re
from dotenv import load_dotenv
from deepgram import Deepgram
import asyncio

class ProcessLink:
    def __init__(self,link,summarise):
        self.link = link
        self.summarise = summarise 


    def getaudio(self):
        ydl_opts = {
            'format': 'bestaudio',
            'quiet' : 'True',
            'paths' : {'home' : f'{Path.home()}/tmpdownloads'},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '128',
            }]}
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        ydl.download(f'{self.link}')
        return os.listdir(f'{Path.home()}/tmpdownloads')
    
    async def convert_to_text(self,file_name):
        load_dotenv(f'{Path.cwd()}/config.env')
        deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
        with open(f"{Path.home()}/tmpdownloads/{file_name}",'rb') as file:
                source = {'buffer': file.read(),'mimetype': 'audio/mp3'}
                deepgram_client = Deepgram(deepgram_api_key)
                response = await deepgram_client.transcription.prerecorded(source, {'punctuate': True,'model': 'video','tier': 'nova','detect_language': True,'alternatives': 2})
                transcription = response['results']['channels'][0]['alternatives'][0]['transcript']
        return transcription

    async def summarise_text(self):
        #using Gemini Pro from google
        print("temp")

    async def processlink(self):
        audio_file_names = self.getaudio()
        for name in audio_file_names:
            processed_transcription = asyncio.run_until_complete(self.convert_to_text(name))
            audio_file_path = Path(f"{Path.home()}/tmpdownloads/{name}")
            text_file_path = Path(f"{Path.cwd()}/transcriptions/{os.path.splitext(name)[0]}.txt")
            text_file_path.write_text(f"{processed_transcription}")
            audio_file_path.unlink()
        return "The transcriptions have been processed and can be accessed in the transcriptions folder\nin the current directory :)"



class handleargs():
     def processargs(self):
        self.getargs()
        if not args.link and not args.summarise:
            print('Welcome to YT summariser | Transcriber :) \nType: --help for Usage instructions')
        else:
            pass

        if args.link is not None:
            process = ProcessLink(args.link,args.summarise)
            process.processlink()

     def getargs(self):
        # create an argument parse object
        parser = ArgumentParser()

        # Arguments
        parser.add_argument("--link",type=str,help="The a video link that is needed to generate the transcription")
        parser.add_argument("--summarise",type=str,help="Set this to yes or no to summarise the generated transcription By default the transcription will be generated")
        
        # Parse the args
        args = parser.parse_args()
        return args
        




if __name__ == '__main__':
    cli = handleargs()
    process_inputs = cli.processargs()