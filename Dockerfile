# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl gnupg ca-certificates \
    libglib2.0-0 libgobject-2.0-0 libnspr4 libnss3 \
    libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libexpat1 libdbus-1-3 libx11-6 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxcursor1 \
    libgbm1 libxkbcommon0 libxcb1 libasound2 \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libcairo-gobject2 \
    libgtk-3-0 libgdk-pixbuf-2.0-0 libatspi2.0-0 \
    fonts-liberation libxshmfence1 libxss1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
RUN python -m playwright install chromium

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "app.main:app"]
