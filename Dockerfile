FROM --platform=linux/amd64 python:3.12-bookworm
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR  /app

COPY . /app
ENV PATH "/root/.local/bin:$PATH"
RUN pip install --upgrade pip
RUN poetry config --local virtualenvs.create false && poetry install  && rm -rf /root/.cache/*
ENV PYTHON_PATH "$PYTHON_PATH:/app/"
RUN set -o vi

CMD streamlit run --server.address '0.0.0.0' --server.port '80' --server.enableCORS True state_of_the_art/app/start.py
