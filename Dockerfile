FROM --platform=linux/amd64 python:3.12-bookworm
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR  /app

COPY . /app
ENV PYTHON_PATH "$PYTHON_PATH:/app/"
ENV PATH "/root/.local/bin:$PATH"
RUN pip install --upgrade pip
RUN echo 'set -o vi' >> ~/.bashrc
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" &&  unzip awscliv2.zip && ./aws/install 
RUN poetry config --local virtualenvs.create false && poetry install  
# cleanups of caches and other stuff
RUN pytest 
RUN rm -rf /root/.cache/*

CMD ./start_monorepo.sh
