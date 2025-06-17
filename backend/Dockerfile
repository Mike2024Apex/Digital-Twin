FROM python:3.12.5-bullseye

COPY ./backend/app /app

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT [ "streamlit", "run", "bot.py", "--server.port=8501", "--server.address=0.0.0.0" ]
