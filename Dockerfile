# Python base image
FROM python:3.12-slim

# Install dependencies for browsers
RUN apt-get update && \
    apt-get install -y wget curl gnupg unzip libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libxcomposite1 libxrandr2 libxdamage1 libxshmfence1 libpangocairo-1.0-0 \
    libpango-1.0-0 libgtk-3-0 libdrm2 libgbm1 libasound2 xvfb x11-utils && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install --no-cache-dir playwright && \
    playwright install

# Copy script
COPY . .

# Run script
CMD ["python", "test_ryanair.py"]
