# ComfyUI RunPod Serverless

ComfyUI worker для развертывания в RunPod Serverless с использованием существующего volume.

## Особенности

- ✅ Работает с RunPod Serverless
- ✅ Поддержка GPU
- ✅ Использует существующий volume с ComfyUI и моделями
- ✅ Автоматический запуск ComfyUI при первом запросе
- ✅ Интеграция с runpod.serverless API

## Ответы на ваши вопросы

### 1. Использовать стандартное API ComfyUI или нужен обработчик?

**Ответ:** Нужен handler для RunPod Serverless.

**Причины:**

- **RunPod Serverless** автоматически запускает воркеры при запросах
- **Handler** (`handler.py`) координирует ComfyUI внутри контейнера
- Обработчик запускает ComfyUI при первом запросе и управляет lifecycle
- Без обработчика ComfyUI не стартует автоматически

**Схема работы:**
```
HTTP запрос → RunPod API → Handler → Запуск ComfyUI → Обработка → Ответ
```

### 2. Как работают несколько serverless воркеров?

**Ответ:** RunPod управляет воркерами.

- **Idle** — воркеры ждут запросы без GPU
- **Cold start** — при первом запросе воркер запускается за 30–60 сек
- **Hot** — последующие запросы в пределах таймаута обрабатываются быстро
- **Timeout** — без активности воркер останавливается

Настройки:
- **Min Workers**: 0
- **Max Workers**: по необходимости
- **Idle Timeout**: 30–60 сек

### 3. Нужно ли будить воркеры вручную?

**Нет.** RunPod запускает их по запросам. Снимите пробу:
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync
```

Handler запустит ComfyUI и вернет результат.

## Структура Volume

Убедитесь, что ваш volume содержит правильную структуру:

```
/runpod-volume/          (будет /workspace в обычном Pod)
├── ComfyUI/             # ComfyUI установлен здесь
│   ├── main.py          # Главный файл ComfyUI
│   ├── custom_nodes/    # Ваши кастомные ноды
│   └── ...
└── models/              # Модели в корне workspace
    ├── checkpoints/
    ├── vae/
    └── ...
```

**Важно:** 
- ComfyUI находится в `ComfyUI/` подпапке
- Модели в `models/` в корне volume
- Результаты будут сохраняться в `ComfyUI/output/`

## Подготовка Docker образа

### 1. Сборка образа

**Важно**: На Mac с ARM используйте linux/amd64:

```bash
docker build --platform linux/amd64 -t your-dockerhub-username/comfyui-runpod:v1 .
```

На Linux x86:

```bash
docker build -t your-dockerhub-username/comfyui-runpod:v1 .
```

Сборка PyTorch может занять 5–10 минут.

### 2. Загрузка в Docker Hub

```bash
docker login
docker push your-dockerhub-username/comfyui-runpod:v1
```

## Развертывание в RunPod

### 1. Создание Network Volume

1. **Storage** → **Network Volumes**
2. Создайте volume
3. Загрузите ComfyUI и модели

### 2. Создание Serverless Template

1. **Serverless** → **Templates** → **New Template**
2. Настройки:
   - **Template Name**: `comfyui-runpod`
   - **Container Image**: `your-dockerhub-username/comfyui-runpod:v1`
   - **Container Registry**: `Docker Hub`
   - **Container Disk**: минимум 10 GB
   - **Volume Mount Point**: `/runpod-volume`
   - **Memory**: минимум 16 GB
   - **GPU**: нужный тип

### 3. Создание Endpoint

1. **Serverless** → **Endpoints** → **New Endpoint**
2. Настройки:
   - **Min Workers**: 0
   - **Max Workers**: по необходимости
   - **Idle Timeout**: 30–60 сек
   - **Flashboot**: включено

## Использование API

### Формат запроса

```python
import requests

endpoint_url = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"

# Workflow для ComfyUI (стандартный формат)
workflow = {
    "1": {
        "inputs": {"ckpt_name": "model.safetensors"},
        "class_type": "CheckpointLoaderSimple"
    },
    "2": {
        "inputs": {"text": "landscape", "clip": ["1", 1]},
        "class_type": "CLIPTextEncode"
    }
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}

response = requests.post(
    endpoint_url,
    headers=headers,
    json={"input": {"workflow": workflow}}
)
result = response.json()
print(result)
```

### Формат ответа

```json
{
  "status": "completed",
  "results": [
    {
      "filename": "image_123.png",
      "image": "base64_data"
    }
  ]
}
```

## Как это работает

### 1. Idle
Воркеры не потребляют GPU.

### 2. Cold start
При первом запросе:
- Запуск воркера
- Запуск ComfyUI
- Загрузка моделей
- Обработка запроса

### 3. Hot
Быстрая обработка последующих запросов.

### 4. Timeout
Worker останавливается; далее новый cold start.

## Переменные окружения

Через шаблон в RunPod:
- `PYTORCH_CUDA_ALLOC_CONF`: `max_split_size_mb:256`
- `MALLOC_ARENA_MAX`: `2`
- `civitai_token`: ваш токен

## Troubleshooting

### Worker не запускается
- Проверьте монтирование volume в `/runpod-volume`
- Проверьте логи в RunPod

### ComfyUI не находит модели
- Проверьте структуру `/runpod-volume/models/`
- Убедитесь, что модели есть в volume

### Timeout при обработке
- Увеличьте `max_wait` в `handler.py` (по умолчанию 300 секунд)
- Проверьте корректность workflow

### Ошибка при сборке на Mac
- Используйте `--platform linux/amd64`
- Загрузите образ в реестр

## Примеры интеграции

### Python клиент

```python
from runpod import serverless
import base64

def process_image(workflow):
    response = serverless.call_endpoint(
        endpoint_id="YOUR_ENDPOINT_ID",
        input_data={"workflow": workflow}
    )
    return response

result = process_image(my_workflow)
for image_result in result["results"]:
    image_data = base64.b64decode(image_result["image"])
    # Сохраняем или обрабатываем
```

### cURL

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"input": {"workflow": {...}}}'
```

## Лицензия

Используйте согласно лицензиям ComfyUI и ваших моделей.

