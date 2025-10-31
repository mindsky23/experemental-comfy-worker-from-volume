#!/usr/bin/env python3
"""
Пример запроса с WAN workflow и загрузкой изображения
"""

import requests
import json

# Настройте эти переменные
ENDPOINT_ID = "9ttuqatz1yrval"
RUNPOD_API_KEY = "YOUR_API_KEY_HERE"

ENDPOINT_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"


# Ваш полный workflow (сокращенная версия для примера)
def get_wan_workflow():
    """
    Возвращает ваш WAN workflow
    ВАЖНО: Используйте ПОЛНЫЙ workflow из вашего примера!
    """
    workflow = {
        "2": {
            "inputs": {
                "unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
                "weight_dtype": "fp8_e4m3fn_fast"
            },
            "class_type": "UNETLoader"
        },
        "3": {
            "inputs": {
                "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
                "type": "wan",
                "device": "default"
            },
            "class_type": "CLIPLoader"
        },
        "4": {
            "inputs": {
                "vae_name": "wan_2.1_vae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "29": {
            "inputs": {
                "width": 1040,
                "height": 1280,
                "length": 121,
                "batch_size": 1
            },
            "class_type": "WanImageToVideo"
        },
        "40": {
            "inputs": {
                "image": "91771d9aa876d0d6f931ca1ab14b8a30.jpg"
            },
            "class_type": "LoadImage"
        }
    }
    
    return workflow


# Base64 изображение (пример, замените на ваше)
EXAMPLE_IMAGE_BASE64 = """data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAoADwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//9k="""


def send_request():
    """
    Отправляет запрос с workflow и изображением
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }
    
    payload = {
        "input": {
            "workflow": get_wan_workflow(),
            "images": [
                {
                    "name": "91771d9aa876d0d6f931ca1ab14b8a30.jpg",
                    "image": EXAMPLE_IMAGE_BASE64
                }
            ]
        }
    }
    
    print(f"Отправка запроса в {ENDPOINT_URL}")
    print(f"Workflow содержит {len(payload['input']['workflow'])} нод")
    print(f"Загружается 1 изображение")
    
    try:
        response = requests.post(ENDPOINT_URL, headers=headers, json=payload, timeout=600)
        response.raise_for_status()
        
        result = response.json()
        print(f"\n✓ Успех!")
        print(f"Результат: {json.dumps(result, indent=2)}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Ошибка: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Ответ сервера: {e.response.text}")
        return None


if __name__ == "__main__":
    if RUNPOD_API_KEY == "YOUR_API_KEY_HERE":
        print("ОШИБКА: Настройте RUNPOD_API_KEY в скрипте!")
        exit(1)
    
    print("=" * 70)
    print("WAN Workflow Request Test")
    print("=" * 70)
    
    result = send_request()
    
    if result:
        print("\n✓ Запрос успешно выполнен!")
    else:
        print("\n✗ Запрос не удался")

