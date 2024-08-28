FROM python:3.11

RUN python -m venv /app/.venv
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    pip install poetry

WORKDIR /app

COPY . /app/
# Install dependencies using Poetry
RUN poetry install

CMD ["poetry", "run", "python", "process_stream.py"]
