# Формат API для RunPod Serverless

## Базовый формат

```json
{
  "input": {
    "workflow": {
      "node_id": {
        "inputs": {...},
        "class_type": "NodeType"
      }
    },
    "images": [
      {
        "name": "filename.jpg",
        "image": "data:image/jpeg;base64,..."
      }
    ]
  }
}
```

## Компоненты

### 1. Workflow

Стандартный ComfyUI workflow с нодами.

**Пример:**
```json
{
  "workflow": {
    "2": {
      "inputs": {
        "unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "weight_dtype": "fp8_e4m3fn_fast"
      },
      "class_type": "UNETLoader"
    }
  }
}
```

### 2. Images (опционально)

Изображения для загрузки в ComfyUI перед обработкой.

**Формат:**
```json
{
  "images": [
    {
      "name": "91771d9aa876d0d6f931ca1ab14b8a30.jpg",
      "image": "data:image/jpeg;base64,/9j/4AAQ..."
    }
  ]
}
```

**Важно:**
- `name` - имя файла, которое должно совпадать с `"image": "filename"` в workflow
- `image` - base64 данные (можно с `data:image/jpeg;base64,` префиксом или без)

### 3. Обработка

Handler:
1. Загружает изображения через `/upload/image` API
2. Отправляет workflow в очередь ComfyUI
3. Ожидает выполнения
4. Возвращает результаты как base64

## Примеры

### cURL

```bash
curl -X POST "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "input": {
      "workflow": {...},
      "images": [...]
    }
  }'
```

### Python

```python
import requests
import base64

ENDPOINT_URL = "https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}

# Читаем изображение
with open("image.jpg", "rb") as f:
    img_data = base64.b64encode(f.read()).decode()
    img_b64 = f"data:image/jpeg;base64,{img_data}"

payload = {
    "input": {
        "workflow": {
            "40": {
                "inputs": {"image": "image.jpg"},
                "class_type": "LoadImage"
            }
        },
        "images": [
            {
                "name": "image.jpg",
                "image": img_b64
            }
        ]
    }
}

response = requests.post(ENDPOINT_URL, headers=HEADERS, json=payload)
result = response.json()
```

### JavaScript

```javascript
const endpointUrl = 'https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/runsync';
const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_API_KEY'
};

// Читаем файл
const file = await fileInput.files[0];
const base64 = await fileToBase64(file);

const payload = {
    input: {
        workflow: {
            "40": {
                inputs: {image: "image.jpg"},
                class_type: "LoadImage"
            }
        },
        images: [
            {
                name: "image.jpg",
                image: base64
            }
        ]
    }
};

const response = await fetch(endpointUrl, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(payload)
});

const result = await response.json();
```

## Формат ответа

### Успех

```json
{
  "status": "completed",
  "results": [
    {
      "filename": "ComfyUI_00001_.png",
      "image": "iVBORw0KGgoAAAANS..."
    }
  ]
}
```

### Ошибка

```json
{
  "status": "error",
  "message": "Error description"
}
```

### Timeout

```json
{
  "status": "timeout",
  "message": "Execution exceeded maximum wait time"
}
```

## Извлечение результатов

### Python

```python
if result["status"] == "completed":
    for item in result["results"]:
        filename = item["filename"]
        image_data = base64.b64decode(item["image"])
        
        with open(filename, "wb") as f:
            f.write(image_data)
```

### JavaScript

```javascript
if (result.status === 'completed') {
    result.results.forEach(item => {
        const imageData = atob(item.image);
        const blob = new Blob([imageData], {type: 'image/png'});
        const url = URL.createObjectURL(blob);
        
        // Используйте URL для отображения или скачивания
    });
}
```

## Troubleshooting

### Worker не запускается
- Проверьте логи в RunPod консоли
- Убедитесь что volume подключен
- Проверьте что ComfyUI найден в `/runpod-volume/ComfyUI/`

### Изображения не загружаются
- Проверьте формат base64
- Убедитесь что `name` совпадает с workflow
- Проверьте размер (не слишком большой)

### Workflow не выполняется
- Проверьте что все модели на месте
- Проверьте логи ComfyUI
- Убедитесь что workflow корректный

### Timeout
- Увеличьте `max_wait` в handler.py
- Проверьте что workflow не зависает
- Проверьте GPU ресурсы

## Примеры

См. файлы:
- `example_client.py` - базовый пример
- `example_wan_workflow.py` - WAN workflow пример
- `example_request.sh` - cURL пример

