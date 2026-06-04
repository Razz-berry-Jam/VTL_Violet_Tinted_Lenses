#comand line interface
import typer
import wikipediaapi
import Video_management

#ability to handle files
from pathlib import Path
from typing import Annotated

app = typer.Typer()#create the application

#encoding
@app.command()
def encode(secret_message: Annotated[Path,typer.Argument(exists=True,
                                                         file_okay=True,
                                                         dir_okay=False,
                                                         writable=False,
                                                         readable=True,
                                                         resolve_path=True,help="A .txt file containg your message"),],

           key: Annotated[Path,typer.Argument(exists=True,
                                              file_okay=True,
                                              dir_okay=False,
                                              writable=False,
                                              readable=True,
                                              resolve_path=True,help="A .txt file containg your shared secret key"),], 

           video: Annotated[Path,typer.Argument(exists=True,
                                                file_okay=True,
                                                dir_okay=False,
                                                writable=False,
                                                readable=True,
                                                resolve_path=True,help="A .mp4 file that is your shared video"),],):

    print("Encode mode selected")
    Video_management.video_to_frames(video)
    Video_management.encrypt(key, secret_message)

#decoding
@app.command()
def decode(key: Annotated[Path,typer.Argument(exists=True,
                                              file_okay=True,
                                              dir_okay=False,
                                              writable=False,
                                              readable=True,
                                              resolve_path=True,help="A .txt file containg your shared secret key"),], 

           video: Annotated[Path,typer.Argument(exists=True,
                                                file_okay=True,
                                                dir_okay=False,
                                                writable=False,
                                                readable=True,
                                                resolve_path=True,help="A .mp4 file that is your shared video"),], 

           encoded_video: Annotated[Path,typer.Argument(exists=True,
                                                        file_okay=True,
                                                        dir_okay=False,
                                                        writable=False,
                                                        readable=True,
                                                        resolve_path=True,help="A .mp4 file that the video containg the secret message\nNOTE: in current version send a txt file with the output of encryption"),],):
    
    print("Decode mode selected")
    Video_management.decrypt(key, encoded_video)

@app.command()
def Fialka_info():
    wiki_wiki = wikipediaapi.Wikipedia(
        #false email for an example
        user_agent='VTL (contact@example.com)',
        language='en'
    )
    page = wiki_wiki.page('Fialka')
    if page.exists():
        print("Here is some info about the original Fialka from Wikipedia: %s" % page.summary)

    else:
        print("Page does not exist.")


if __name__ == "__main__":
    app()
