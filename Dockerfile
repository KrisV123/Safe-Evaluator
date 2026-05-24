# only for testing in Linux enviroment

FROM python:3.12-slim

WORKDIR /safe_evaluator

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python", "-m", "tester"]
