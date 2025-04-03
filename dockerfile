# start from a pyhton 11 base
FROM python:3.11-slim
# install FFMPEG
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean
WORKDIR /app
COPY . . 

#install dependencies
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
