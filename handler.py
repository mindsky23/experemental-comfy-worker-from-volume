import os
import subprocess
import threading
import time
import requests
import json
import base64
import runpod


class ComfyUIHandler:
    def __init__(self):
        self.comfyui_process = None
        self.comfyui_url = "http://localhost:8188"
        self.setup_comfyui_paths()
        
    def setup_comfyui_paths(self):
        """
        Настраивает пути для ComfyUI:
        В RunPod Serverless volume монтируется в /runpod-volume
        Структура: /runpod-volume/ComfyUI/main.py и /runpod-volume/models/
        """
        # В RunPod Serverless volume монтируется в /runpod-volume
        # У пользователя структура: /workspace/ComfyUI/ и /workspace/models/
        runpod_volume = "/runpod-volume"
        
        # Определяем путь к ComfyUI
        # Проверяем структуру: /runpod-volume/ComfyUI/main.py
        if os.path.exists(f"{runpod_volume}/ComfyUI/main.py"):
            self.comfyui_path = f"{runpod_volume}/ComfyUI"
        elif os.path.exists(f"{runpod_volume}/main.py"):
            # Альтернативная структура: /runpod-volume/main.py
            self.comfyui_path = runpod_volume
        else:
            self.comfyui_path = f"{runpod_volume}/ComfyUI"  # По умолчанию
        
        print(f"ComfyUI path: {self.comfyui_path}")
        
        # Проверяем наличие main.py
        if not os.path.exists(f"{self.comfyui_path}/main.py"):
            print(f"Warning: ComfyUI main.py not found at {self.comfyui_path}")
        else:
            print(f"✓ ComfyUI found at {self.comfyui_path}")
        
    def start_comfyui(self):
        """Запускает ComfyUI в фоновом режиме"""
        if self.comfyui_process and self.comfyui_process.poll() is None:
            print("ComfyUI already running")
            return
        
        print("Starting ComfyUI...")
        
        # Команда для запуска ComfyUI
        cmd = [
            "python3",
            "-u",
            f"{self.comfyui_path}/main.py"
        ]
        
        self.comfyui_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=self.comfyui_path
        )
        
        # Ждем, пока ComfyUI запустится
        for i in range(60):
            try:
                response = requests.get(f"{self.comfyui_url}/system_stats", timeout=2)
                if response.status_code == 200:
                    print("ComfyUI is ready!")
                    return
            except:
                pass
            time.sleep(1)
        
        raise RuntimeError("ComfyUI failed to start within 60 seconds")
    
    def queue_prompt(self, prompt):
        """
        Отправляет промпт в очередь ComfyUI
        """
        p = {"prompt": prompt, "client_id": str(time.time())}
        
        response = requests.post(
            f"{self.comfyui_url}/prompt",
            json=p
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_history(self, prompt_id):
        """Получает историю выполнения промпта"""
        response = requests.get(
            f"{self.comfyui_url}/history/{prompt_id}"
        )
        response.raise_for_status()
        return response.json()
    
    def get_image(self, filename, subfolder="", folder_type="output"):
        """Загружает изображение из ComfyUI"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        
        response = requests.get(
            f"{self.comfyui_url}/view",
            params=data,
            timeout=10
        )
        response.raise_for_status()
        
        return response.content
    
    def process_comfyui_workflow(self, workflow_prompt):
        """
        Обрабатывает workflow ComfyUI и возвращает результаты
        
        Результаты сохраняются в:
        - /runpod-volume/ComfyUI/output/ (в volume, виден в RunPod)
        - Возвращаются в ответе API как base64
        """
        try:
            # Запускаем ComfyUI если он еще не запущен
            self.start_comfyui()
            
            # Отправляем промпт
            print("Queuing prompt...")
            queue_response = self.queue_prompt(workflow_prompt)
            prompt_id = queue_response["prompt_id"]
            
            print(f"Prompt queued with ID: {prompt_id}")
            
            # Ждем выполнения
            results = []
            max_wait = 300  # 5 минут максимум
            waited = 0
            
            while waited < max_wait:
                time.sleep(2)
                waited += 2
                
                history = self.get_history(prompt_id)
                
                if prompt_id in history:
                    print("Execution completed!")
                    
                    # Извлекаем результаты
                    prompt_outputs = history[prompt_id]["outputs"]
                    
                    for node_id in prompt_outputs:
                        node_output = prompt_outputs[node_id]
                        
                        if "images" in node_output:
                            for image_info in node_output["images"]:
                                filename = image_info["filename"]
                                subfolder = image_info.get("subfolder", "")
                                image_type = image_info.get("type", "output")
                                
                                image_data = self.get_image(filename, subfolder, image_type)
                                
                                # Кодируем в base64 для передачи
                                image_base64 = base64.b64encode(image_data).decode()
                                
                                results.append({
                                    "filename": filename,
                                    "image": image_base64
                                })
                    
                    return {
                        "status": "completed",
                        "results": results
                    }
                
                print(f"Waiting for execution... ({waited}s)")
            
            return {
                "status": "timeout",
                "message": "Execution exceeded maximum wait time"
            }
            
        except Exception as e:
            print(f"Error processing workflow: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


# Создаем глобальный handler
handler_instance = ComfyUIHandler()


def handler(event):
    """
    Основная функция обработчика для RunPod Serverless
    """
    try:
        input_data = event.get("input", {})
        
        # Поддерживаем разные форматы входа
        if "workflow" in input_data:
            # Пользователь отправляет готовый workflow
            workflow_prompt = input_data["workflow"]
        elif "prompt" in input_data:
            # Альтернативный формат
            workflow_prompt = input_data["prompt"]
        else:
            return {
                "error": "Missing 'workflow' or 'prompt' in input"
            }
        
        # Обрабатываем workflow
        result = handler_instance.process_comfyui_workflow(workflow_prompt)
        
        return result
        
    except Exception as e:
        return {
            "error": str(e)
        }


# Запускаем сервер RunPod
if __name__ == "__main__":
    print("Starting RunPod Serverless handler...")
    print("ComfyUI will be started on first request")
    
    runpod.serverless.start({"handler": handler})

