import gradio as gr
import requests
import time
import os

# Usar host.docker.internal por defecto para Docker Desktop
BACKEND_URL = os.getenv("BACKEND_URL", "http://host.docker.internal:8000")
POLL_INTERVAL = 2  # segundos
MAX_POLLS = 10

def get_all_products():
    try:
        r = requests.get(f"{BACKEND_URL}/products", timeout=5)
        r.raise_for_status()
        data = r.json()
        return data.get("products", [])
    except Exception:
        return []

def search_by_text(query):
    if not query.strip():
        return [], [], "Introduce una descripción para buscar."
    try:
        r = requests.post(f"{BACKEND_URL}/search/text", json={"query": query}, timeout=10)
        r.raise_for_status()
        data = r.json()
        cats = data.get("categories", [])
        prods = data.get("products", [])
        if not prods:
            return cats, prods, "No se encontraron productos para la búsqueda."
        return cats, prods, ""
    except Exception as e:
        return [], [], f"Error al buscar por texto: {e}"

def search_by_image(image):
    if image is None:
        return [], [], "Sube una imagen para buscar."
    try:
        img_bytes = gr.processing_utils.encode_pil_to_bytes(image)
        files = {"file": ("image.png", img_bytes, "image/png")}
        r = requests.post(f"{BACKEND_URL}/search/image", files=files, timeout=30)
        r.raise_for_status()
        task_id = r.json().get("task_id")
        if not task_id:
            return [], [], "No se recibió task_id del backend."
    except Exception as e:
        return [], [], f"Error al enviar imagen: {e}"
    # Polling
    for i in range(MAX_POLLS):
        time.sleep(POLL_INTERVAL)
        try:
            poll = requests.get(f"{BACKEND_URL}/tasks/{task_id}/result", timeout=10)
            if poll.status_code == 202:
                continue
            poll.raise_for_status()
            data = poll.json()
            cats = data.get("categories", [])
            prods = data.get("products", [])
            if not prods:
                return cats, prods, "No se encontraron productos para la imagen."
            return cats, prods, ""
        except Exception:
            continue
    return [], [], "La inferencia tardó demasiado. Intenta de nuevo."

def main_search(text, image):
    if text and not image:
        return *search_by_text(text), gr.update(visible=False)
    if image and not text:
        cats, prods, msg = search_by_image(image)
        return cats, prods, msg, gr.update(visible=False)
    if text and image:
        # Prioridad: imagen
        cats, prods, msg = search_by_image(image)
        return cats, prods, msg, gr.update(visible=False)
    # Sin entrada: mostrar todos los productos
    prods = get_all_products()
    return [], prods, "Mostrando todos los productos.", gr.update(visible=False)

def format_products(products):
    if not products:
        return "No hay productos para mostrar."
    return "\n".join([
        f"<div style='padding:8px 0;border-bottom:1px solid #eee;'><b>{p['name']}</b> <span style='color:#888;'>({p['price']}€)</span></div>"
        for p in products
    ])

def format_categories(categories):
    if not categories:
        return "Sin categorías detectadas."
    return ", ".join(categories)

with gr.Blocks(theme=gr.themes.Soft(), css=".gradio-container {max-width: 700px !important;} .loader {color:#1976d2;font-weight:bold;}") as demo:
    gr.Markdown("""
    # 🛒 E-commerce IA
    <span style='color:#1976d2;font-size:1.1em;'>Busca productos por texto o imagen usando IA</span>
    """, elem_id="title")
    with gr.Row():
        with gr.Column():
            text_in = gr.Textbox(label="Buscar por texto", placeholder="Ej: camiseta deportiva roja", show_label=True)
            image_in = gr.Image(label="Buscar por imagen", type="pil", show_label=True)
            search_text_btn = gr.Button("Buscar por texto", elem_id="search-text-btn", variant="primary")
            search_image_btn = gr.Button("Buscar por imagen", elem_id="search-image-btn", variant="secondary")
        with gr.Column():
            loader = gr.Markdown("", visible=False, elem_id="loader")
            cats_out = gr.Textbox(label="Categorías detectadas", interactive=False, show_label=True)
            prods_out = gr.HTML(label="Productos encontrados")
            msg_out = gr.Markdown("", elem_id="msg")

    def on_search_text(text):
        loader.update(value="Buscando por texto...", visible=True)
        cats, prods, msg = search_by_text(text)
        return {
            loader: gr.update(value="", visible=False),
            cats_out: format_categories(cats),
            prods_out: format_products(prods),
            msg_out: msg
        }

    def on_search_image(image):
        loader.update(value="Buscando por imagen...", visible=True)
        cats, prods, msg = search_by_image(image)
        return {
            loader: gr.update(value="", visible=False),
            cats_out: format_categories(cats),
            prods_out: format_products(prods),
            msg_out: msg
        }

    search_text_btn.click(
        on_search_text,
        inputs=[text_in],
        outputs=[loader, cats_out, prods_out, msg_out],
        show_progress=True
    )
    # Permitir buscar pulsando Enter en el textbox
    text_in.submit(
        on_search_text,
        inputs=[text_in],
        outputs=[loader, cats_out, prods_out, msg_out],
        show_progress=True
    )
    search_image_btn.click(
        on_search_image,
        inputs=[image_in],
        outputs=[loader, cats_out, prods_out, msg_out],
        show_progress=True
    )

    # Mostrar todos los productos al cargar
    def on_load():
        prods = get_all_products()
        return format_products(prods)
    demo.load(on_load, inputs=None, outputs=prods_out)

demo.launch(server_name="0.0.0.0", server_port=7860)
