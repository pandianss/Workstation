FROM python:3.11-slim

WORKDIR /app

# For fully offline installation from local wheels:
# COPY wheels /app/wheels
# RUN pip install --no-index --find-links /app/wheels -r requirements.txt
# Otherwise, for an online build:
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
