FROM python:3.12

RUN pip install poetry==1.8.2

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install
COPY src ./src
RUN poetry install


ENTRYPOINT ["poetry","run","python", "-m","uvicorn","src.main:app"]