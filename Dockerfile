FROM python:3.10-slim as compiler
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt /app/requirements.txt
RUN pip install -Ur requirements.txt

FROM python:3.10-slim as runner
WORKDIR /app
COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY . /app/

# COPY . .
CMD ["python", "main.py"]