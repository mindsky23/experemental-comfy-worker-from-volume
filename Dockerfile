# Используем базовый образ с Python
FROM python:3.11-slim

# Устанавливаем необходимые системные зависимости
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем только минимальные зависимости (ComfyUI установит остальное сам)
RUN pip install --no-cache-dir -r requirements.txt

# Копируем handler
COPY handler.py .

# Устанавливаем переменные окружения из вашей команды
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256
ENV MALLOC_ARENA_MAX=2
ENV download_480p_native_models=false
ENV download_720p_native_models=false
ENV download_wan_fun_and_sdxl_helper=false
ENV download_vace=false
ENV civitai_token=5549c54156c475ff17041d5ec4720cf5

# Порт для ComfyUI
EXPOSE 8188

# Запускаем handler
CMD ["python3", "handler.py"]

