FROM --platform=linux/amd64 python:3.12-bookworm
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR  /app

COPY . /app
ENV PYTHON_PATH "$PYTHON_PATH:/app/"
ENV PATH "/root/.local/bin:$PATH"
RUN pip install --upgrade pip
RUN set -o vi
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" &&  unzip awscliv2.zip && ./aws/install 
RUN poetry config --local virtualenvs.create false && poetry install  

RUN sota cicd aws authentication_profile_str > /root/.aws/credentials

# cleanups of caches and other stuff
RUN rm -rf /root/.cache/*


CMD streamlit run --server.address '0.0.0.0' --server.port '80' --server.enableCORS False state_of_the_art/app/start.py
