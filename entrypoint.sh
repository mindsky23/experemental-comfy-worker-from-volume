#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Install ComfyUI requirements from volume
echo "Installing ComfyUI requirements..."
if [ -f /runpod-volume/ComfyUI/requirements.txt ]; then
    pip install --no-cache-dir -q -r /runpod-volume/ComfyUI/requirements.txt
fi

# Install custom nodes requirements
echo "Installing custom nodes requirements..."
find /runpod-volume/ComfyUI/custom_nodes -name "requirements.txt" -exec pip install --no-cache-dir -q -r {} \;

# Start ComfyUI in the background (from volume)
echo "Starting ComfyUI in the background..."
python /runpod-volume/ComfyUI/main.py --listen --use-sage-attention &

# Wait for ComfyUI to be ready
echo "Waiting for ComfyUI to be ready..."
max_wait=600  # 최대 10분 (установка зависимостей может занять время)
wait_count=0
while [ $wait_count -lt $max_wait ]; do
    if curl -s http://127.0.0.1:8188/ > /dev/null 2>&1; then
        echo "ComfyUI is ready!"
        break
    fi
    echo "Waiting for ComfyUI... ($wait_count/$max_wait)"
    sleep 2
    wait_count=$((wait_count + 2))
done

if [ $wait_count -ge $max_wait ]; then
    echo "Error: ComfyUI failed to start within $max_wait seconds"
    exit 1
fi

# Start the handler in the foreground
# 이 스크립트가 컨테이너의 메인 프로세스가 됩니다.
echo "Starting the handler..."
exec python /app/handler.py