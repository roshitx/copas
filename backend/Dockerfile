FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE $PORT
CMD ["sh", "-c", "if [ -n \"$YTDLP_COOKIES_B64\" ]; then echo \"$YTDLP_COOKIES_B64\" | base64 -d > /tmp/youtube_cookies.txt && export YTDLP_COOKIE_FILE=/tmp/youtube_cookies.txt; fi && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
