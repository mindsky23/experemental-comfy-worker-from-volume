#!/bin/bash

# Пример запроса к RunPod endpoint с вашим workflow
# Настройте эти переменные:
ENDPOINT_ID="9ttuqatz1yrval"
RUNPOD_API_KEY="YOUR_API_KEY_HERE"

# URL endpoint
ENDPOINT_URL="https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync"

# Создаем JSON payload
cat > /tmp/request.json << 'EOF'
{
  "input": {
    "workflow": {
      "2": {
        "inputs": {
          "unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
          "weight_dtype": "fp8_e4m3fn_fast"
        },
        "class_type": "UNETLoader",
        "_meta": {
          "title": "Load Diffusion Model"
        }
      },
      "3": {
        "inputs": {
          "clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
          "type": "wan",
          "device": "default"
        },
        "class_type": "CLIPLoader",
        "_meta": {
          "title": "Load CLIP"
        }
      },
      "4": {
        "inputs": {
          "vae_name": "wan_2.1_vae.safetensors"
        },
        "class_type": "VAELoader",
        "_meta": {
          "title": "Load VAE"
        }
      },
      "29": {
        "inputs": {
          "width": 1040,
          "height": 1280,
          "length": 121,
          "batch_size": 1
        },
        "class_type": "WanImageToVideo",
        "_meta": {
          "title": "WanImageToVideo"
        }
      },
      "40": {
        "inputs": {
          "image": "91771d9aa876d0d6f931ca1ab14b8a30.jpg"
        },
        "class_type": "LoadImage",
        "_meta": {
          "title": "Load Image"
        }
      }
    },
    "images": [
      {
        "name": "91771d9aa876d0d6f931ca1ab14b8a30.jpg",
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAoADwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD3+iiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//9k="
      }
    ]
  }
}
EOF

# Отправляем запрос
curl -X POST "$ENDPOINT_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $RUNPOD_API_KEY" \
  -d @/tmp/request.json

echo ""
echo "Запрос отправлен!"

