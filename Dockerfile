# Use Python base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    runpod \
    websocket-client

# Copy handler and config files first
WORKDIR /app
COPY handler.py .
COPY entrypoint.sh .
COPY extra_model_paths.yaml .
COPY new_Wan22_api.json /new_Wan22_api.json
COPY new_Wan22_flf2v_api.json /new_Wan22_flf2v_api.json
RUN chmod +x entrypoint.sh

# Note: ComfyUI and models should be in /runpod-volume/
# Install ComfyUI requirements at runtime from volume

CMD ["/app/entrypoint.sh"]
