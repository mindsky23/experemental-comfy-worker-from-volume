# Быстрый старт

Пошаговая инструкция для развертывания ComfyUI в RunPod Serverless.

## Шаг 1: Подготовка Volume

1. Зайдите в RunPod → **Storage** → **Network Volumes**
2. Создайте новый volume (например, 100 GB)
3. Подключите к временному GPU Pod
4. Загрузите ваш рабочий ComfyUI:
   ```bash
   # Структура должна быть:
   /workspace/
   ├── ComfyUI/         # ComfyUI установлен здесь
   │   ├── main.py
   │   ├── custom_nodes/
   │   └── ...
   └── models/          # Модели в корне workspace
       ├── checkpoints/
       ├── vae/
       └── ...
   ```
   
   **Важно:** ComfyUI должен быть в `/workspace/ComfyUI/`, а модели в `/workspace/models/`
   
5. Отсоедините Pod

## Шаг 2: Сборка Docker образа

### На Mac (ARM/M1/M2/M3):
```bash
docker build --platform linux/amd64 -t your-username/comfyui-runpod:v1 .
docker push your-username/comfyui-runpod:v1
```

### На Linux:
```bash
docker build -t your-username/comfyui-runpod:v1 .
docker push your-username/comfyui-runpod:v1
```

## Шаг 3: Создание Template в RunPod

1. **Serverless** → **Templates** → **New Template**
2. Настройки:
   - Name: `comfyui-runpod`
   - Container Image: `your-username/comfyui-runpod:v1`
   - Registry: Docker Hub
   - Container Disk: 10 GB
   - **Volume Mount**: Выберите ваш volume
   - **Volume Mount Point**: `/runpod-volume`
   - Memory: 16 GB
   - GPU: A100 (или другой)

## Шаг 4: Создание Endpoint

1. **Serverless** → **Endpoints** → **New Endpoint**
2. Выберите созданный template
3. Настройки:
   - Min Workers: 0
   - Max Workers: 2
   - Idle Timeout: 60
   - Flashboot: ON

## Шаг 5: Тестирование

Отредактируйте `example_client.py`:
```python
ENDPOINT_ID = "ваш_endpoint_id"
RUNPOD_API_KEY = "ваш_api_ключ"
```

Запустите:
```bash
python3 example_client.py
```

## Проблемы?

### Worker не запускается
- Проверьте логи в RunPod консоли
- Убедитесь, что volume подключен

### ComfyUI не находит main.py
- Проверьте, что `/runpod-volume/main.py` существует
- Проверьте структуру volume

### Timeout
- Увеличьте timeout в RunPod настройках
- Проверьте логи для ошибок

## Готово!

Теперь вы можете отправлять запросы к endpoint через:
- Python клиент (см. `example_client.py`)
- HTTP API напрямую
- RunPod SDK

