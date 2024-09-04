FROM python:3.12-bookworm
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . /app
WORKDIR  /app

RUN $HOME/.local/bin/poetry install


CMD streamlit run app/state_of_the_art/app/start.py
