#!/usr/bin/env python3
"""
Script de prueba para verificar el formato de salida del modelo y la transformación
"""
import sys
import os

# Agregar el directorio de la aplicación de inferencia al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'inference'))

from inference.app.models.squeezenet import SqueezeNet

def test_model_output():
    """Prueba directa del modelo SqueezeNet"""
    print("=== PRUEBA DIRECTA DEL MODELO ===")
    model_path = "squeezenet.onnx"
    
    if not os.path.exists(model_path):
        print(f"Error: No se encuentra el modelo en {model_path}")
        return
    
    model = SqueezeNet(model_path)
    
    # Cargar imagen de prueba
    with open("gato.jpeg", "rb") as f:
        image_data = f.read()
    
    result = model(image_data)
    print("Resultado directo del modelo:")
    print(result)
    print()
    
    return result

def test_format_transformation():
    """Prueba de la transformación de formato (simular lógica del webhook)"""
    print("=== PRUEBA DE TRANSFORMACIÓN DE FORMATO ===")
    
    # Simular resultado del modelo (formato README)
    model_result = {
        "category": [
            {"label": 0, "confidence": 0.95},
            {"label": 1, "confidence": 0.03},
            {"label": 2, "confidence": 0.02}
        ]
    }
    
    # Aplicar transformación como en tasks.py
    categories = []
    for item in model_result["category"]:
        categories.append({
            "label": item["label"],
            "score": item["confidence"]  # Transformar "confidence" a "score"
        })
    
    webhook_result = {
        "categories": categories  # Usar "categories" para el webhook
    }
    
    print("Resultado después de la transformación (formato webhook):")
    print(webhook_result)
    print()
    
    return webhook_result

def main():
    print("Iniciando pruebas de formato...\n")
    
    # Prueba 1: Salida directa del modelo
    model_result = test_model_output()
    
    # Prueba 2: Salida procesada para webhook
    webhook_result = test_format_transformation()
    
    # Verificar las diferencias
    print("=== ANÁLISIS DE FORMATO ===")
    if model_result and webhook_result:
        print("Formato del modelo (README):", list(model_result.keys()))
        print("Formato del webhook:", list(webhook_result.keys()))
        
        # Verificar que los campos se transformaron correctamente
        if "category" in model_result and "categories" in webhook_result:
            print("✓ Transformación category → categories: OK")
        else:
            print("✗ Error en transformación category → categories")
            
        if (model_result.get("category") and webhook_result.get("categories") and
            "confidence" in model_result["category"][0] and "score" in webhook_result["categories"][0]):
            print("✓ Transformación confidence → score: OK")
        else:
            print("✗ Error en transformación confidence → score")
            
        # Verificar que los valores sean numéricos
        if (webhook_result.get("categories") and 
            all(isinstance(cat.get("label"), int) for cat in webhook_result["categories"])):
            print("✓ Labels son índices numéricos: OK")
        else:
            print("✗ Error: Labels no son índices numéricos")

if __name__ == "__main__":
    main()
