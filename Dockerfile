
FROM python:3.10-slim

# Install dependencies
RUN pip install --no-cache-dir streamlit boto3

# Copy application code
COPY chat_app_final.py /app/chat_app_final.py

# Set working directory
WORKDIR /app

# Run the Streamlit app
CMD ["streamlit", "run", "chat_app_final.py"]
    