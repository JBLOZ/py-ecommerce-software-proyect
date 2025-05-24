#!/usr/bin/env python3
"""
Script de prueba para verificar que el servicio de inferencia devuelve
etiquetas de ImageNet en lugar de índices numéricos.
"""

import requests
import sys
import os

def test_inference_service():
    """Prueba el servicio de inferencia con una imagen."""
    
    # URL del servicio de inferencia
    inference_url = "http://localhost:8001/infer/image/sync"
    
    # Ruta de la imagen de prueba
    image_path = "gato.jpeg"
    
    if not os.path.exists(image_path):
        print(f"Error: No se encontró la imagen {image_path}")
        return False
    
    try:
        # Preparar la imagen para la solicitud
        with open(image_path, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            
            print(f"Enviando imagen {image_path} al servicio de inferencia...")
            print(f"URL: {inference_url}")
            
            # Hacer la solicitud
            response = requests.post(inference_url, files=files, timeout=30)
            
            # Verificar la respuesta
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Respuesta exitosa: {response.status_code}")
                print(f"📋 Resultado completo: {result}")
                
                # Verificar si contiene categorías
                if 'category' in result and result['category']:
                    categories = result['category']
                    top_prediction = categories[0] if categories else None
                    
                    if top_prediction and 'label' in top_prediction:
                        label = top_prediction['label']
                        confidence = top_prediction.get('confidence', 0)
                        print(f"🎯 Predicción principal: {label}")
                        print(f"📊 Confianza: {confidence:.4f}")
                        
                        # Verificar si es una etiqueta de ImageNet (string) y no un índice numérico
                        if isinstance(label, str) and not label.isdigit():
                            print("✅ ¡ÉXITO! El servicio está devolviendo etiquetas de ImageNet correctamente")
                            print(f"🏷️  Clase detectada: '{label}'")
                            print(f"🔍 Total de categorías devueltas: {len(categories)}")
                            return True
                        else:
                            print(f"❌ ERROR: Se está devolviendo un índice numérico: {label}")
                            print("   El servicio debería devolver una etiqueta de ImageNet como 'Egyptian cat'")
                            return False
                    else:
                        print("❌ ERROR: No se encontró 'label' en la primera categoría")
                        return False
                else:
                    print("❌ ERROR: No se encontró 'category' en la respuesta o está vacía")
                    return False
            else:
                print(f"❌ Error en la solicitud: {response.status_code}")
                print(f"Respuesta: {response.text}")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: No se pudo conectar al servicio de inferencia")
        print("   Verifica que el servicio esté ejecutándose en http://localhost:8001")
        return False
    except requests.exceptions.Timeout:
        print("❌ ERROR: Timeout en la solicitud")
        return False
    except Exception as e:
        print(f"❌ ERROR inesperado: {str(e)}")
        return False

def check_service_health():
    """Verifica si el servicio está disponible."""
    try:
        health_url = "http://localhost:8001/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ Servicio de inferencia disponible")
            return True
        else:
            print(f"⚠️  Servicio responde pero con estado: {response.status_code}")
            return False
    except:
        print("❌ Servicio de inferencia no disponible")
        return False

if __name__ == "__main__":
    print("🧪 Iniciando prueba del servicio de inferencia de SqueezeNet")
    print("=" * 60)
    
    # Verificar conectividad del servicio
    print("1. Verificando disponibilidad del servicio...")
    if not check_service_health():
        print("   Intentando continuar con la prueba...")
    
    print("\n2. Probando clasificación de imagen...")
    success = test_inference_service()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ¡PRUEBA EXITOSA! El problema ha sido solucionado.")
        print("   El servicio ahora devuelve etiquetas de ImageNet en lugar de índices numéricos.")
    else:
        print("💥 PRUEBA FALLIDA. El problema aún no está resuelto.")
        print("   Revisar los logs del servicio para más información.")
    
    sys.exit(0 if success else 1)
