# Use an official lightweight Python image
FROM python:3.11-slim
# Set the working directory in the container
WORKDIR /app--help--help
# Copy files into the docker
COPY cat.mp4 .
COPY VTL-V5.py .
COPY Video_management.py .
COPY Vid_manage_test.py .
COPY Violet.py .
COPY output.txt .
COPY test_message.txt .
COPY valid_test_key.txt .
COPY invalid_test_key.txt .
# Up to date
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*
    
RUN pip3 install typer
RUN pip3 install Wikipedia-API
#RUN pip3 install h264decoder

#RUN apt install mplayer
#RUN pip install mpylayer
#RUN pip3 install opencv-python   
#RUN pip install ffmpeg-python
#RUN pip install ffprobe-python

# Run the program
#CMD ["python", "VTL-V2.py"] #the program is an interface
ENTRYPOINT ["python", "VTL-V5.py"] #open and pass commands
