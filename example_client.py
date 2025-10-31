#!/usr/bin/env python3
"""
Пример клиента для тестирования ComfyUI RunPod Serverless endpoint
"""

import requests
import base64
import json
from pathlib import Path

# Настройте эти переменные
ENDPOINT_ID = "YOUR_ENDPOINT_ID_HERE"
RUNPOD_API_KEY = "YOUR_API_KEY_HERE"

# URL endpoint
ENDPOINT_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"


def create_simple_workflow():
    """
    Создает простой workflow для генерации изображения
    Замените на свой реальный workflow
    """
    workflow = {
        "1": {
            "inputs": {
                "ckpt_name": "your_model.safetensors"  # Замените на вашу модель
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "text": "a beautiful landscape, 4k, detailed",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {
                "text": "text, watermark",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {
                "seed": 12345,
                "steps": 20,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "samples": ["4", 0],
                "vae": ["1", 2]
            },
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["6", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    return workflow


def process_image(workflow, images=None):
    """
    Отправляет workflow в RunPod endpoint и получает результат
    
    Args:
        workflow: dict - ComfyUI workflow
        images: list (optional) - список изображений в формате [{"name": "filename.jpg", "image": "base64_data"}]
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }
    
    payload = {
        "input": {
            "workflow": workflow
        }
    }
    
    # Добавляем изображения если они есть
    if images:
        payload["input"]["images"] = images
        print(f"Добавлено {len(images)} изображений для загрузки")
    
    print("Отправка запроса в RunPod...")
    print(f"Endpoint: {ENDPOINT_URL}")
    
    try:
        response = requests.post(ENDPOINT_URL, headers=headers, json=payload, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        print(f"Результат: {json.dumps(result, indent=2)}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}")
        return None


def save_images(result):
    """
    Сохраняет изображения из результата
    """
    if result.get("status") != "completed":
        print(f"Статус не 'completed': {result.get('status')}")
        return
    
    results = result.get("results", [])
    if not results:
        print("Нет результатов для сохранения")
        return
    
    # Создаем папку для сохранения
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    for i, image_result in enumerate(results):
        filename = image_result.get("filename", f"image_{i}.png")
        image_data = image_result.get("image")
        
        if image_data:
            # Декодируем base64
            image_bytes = base64.b64decode(image_data)
            
            # Сохраняем
            output_path = output_dir / filename
            output_path.write_bytes(image_bytes)
            print(f"Сохранено: {output_path}")
        else:
            print(f"Нет данных изображения для {filename}")


def main():
    """
    Основная функция для тестирования
    """
    print("ComfyUI RunPod Serverless Test Client")
    print("=" * 50)
    
    # Проверяем настройки
    if ENDPOINT_ID == "YOUR_ENDPOINT_ID_HERE" or RUNPOD_API_KEY == "YOUR_API_KEY_HERE":
        print("ОШИБКА: Настройте ENDPOINT_ID и RUNPOD_API_KEY в скрипте!")
        return
    
    # Создаем workflow
    workflow = create_simple_workflow()
    print("\nWorkflow:")
    print(json.dumps(workflow, indent=2))
    
    # Отправляем запрос
    result = process_image(workflow)
    
    # Сохраняем результаты
    if result:
        save_images(result)
    
    print("\nГотово!")


if __name__ == "__main__":
    main()

