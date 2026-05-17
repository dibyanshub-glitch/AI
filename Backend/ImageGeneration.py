import asyncio
from pathlib import Path
from random import randint
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO
import os
from dotenv import load_dotenv

from Frontend.GUI import ShowTextToScreen
load_dotenv()

HF_TOKEN = os.getenv("HuggingFaceAPIKey")

# ---------- MODELS ----------
MODELS = [
    "black-forest-labs/FLUX.1-schnell"
]


client = InferenceClient(token=HF_TOKEN)

OUT_DIR = Path("Data")
OUT_DIR.mkdir(exist_ok=True)

# ---------- PROMPT ENHANCER ----------
STYLES = {
    "cinematic": "cinematic lighting, dramatic shadows, ultra realistic",
    "anime": "anime style, vibrant colors, manga style",
    "realistic": "photorealistic, DSLR quality",
    "art": "digital art, concept art, detailed illustration"
}


def detect_style(prompt: str):

    for style in STYLES:
        if style in prompt.lower():
            return style

    return "cinematic"


def enhance_prompt(prompt: str):

    style = detect_style(prompt)
    style_text = STYLES.get(style, "")

    return f"""
Highly detailed professional artwork,
{style_text},
{prompt}
""".strip()



# ---------- MODEL FALLBACK ----------
async def generate_with_fallback(prompt: str):

    for model in MODELS:
        try:
            print(f"Trying model → {model}")

            def safe_hf_generate(prompt, model):
                try:
                    return client.text_to_image(prompt=prompt, model=model)
                except StopIteration:
                    return None
                except Exception as e:
                    print("HF Error:", e)
                    return None

            img = await asyncio.to_thread(safe_hf_generate, prompt, model)

            if img:
                return img

        except Exception as e:
            print("Model failed:", model, e)

    # ---------- LOCAL FALLBACK ----------
    try:
        print("Using LOCAL diffusion fallback")

        from Backend.LocalDiffusion import generate_local
        return await asyncio.to_thread(generate_local, prompt)

    except Exception as e:
        print("Local fallback failed:", e)
        return None



# ---------- SAVE IMAGE ----------
def save_image(pil_img, prompt, idx):

    safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (" ", "_")).strip()
    safe_prompt = safe_prompt.replace(" ", "_")[:40]

    filename = OUT_DIR / f"{safe_prompt}_{idx}.png"

    pil_img.save(filename)
    return filename


# ---------- MAIN GENERATOR ----------
async def generate_images(prompt: str, count: int = 2):

    prompt = enhance_prompt(prompt)
    print("Enhanced Prompt:", prompt)

    results = []

    for i in range(count):

        progress = int(((i + 1) / count) * 100)
        ShowTextToScreen(f"Image generation {progress}%")

        img = await generate_with_fallback(prompt)

        if isinstance(img, bytes):
            img = Image.open(BytesIO(img))

        if isinstance(img, Image.Image):
            file = save_image(img, prompt, i)
            results.append(file)

            # ✅ SEND PREVIEW TO GUI
            from Frontend.PreviewBridge import send_preview
            send_preview(file)


    ShowTextToScreen("Image generation 100%")

    return results


# ---------- QUEUE ----------
class ImageQueueManager:

    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self.cancel_flag = False


    async def worker(self):
        while True:

            prompt = await self.queue.get()

            if self.cancel_flag:
                print("Generation cancelled")
                self.cancel_flag = False
                self.queue.task_done()
                continue


            
            prompt = prompt.replace("🎧 Listening...", "").strip()


            print("Queue Processing →", prompt)
            print("Generating image...")


            files = await generate_images(prompt)
            print("Generated:", files)
            print("Image generation completed")

            import webbrowser
            for f in files:
                webbrowser.open(f.resolve().as_uri())

            from Backend.Upscaler import upscale_image

            upscaled = []

            for img_path in files:
                from PIL import Image
                img = Image.open(img_path)

                img = upscale_image(img,prompt)
                img.save(img_path)

                upscaled.append(img_path)

            files = upscaled

            from Backend.ImageGallery import save_to_gallery

            for f in files:
                save_to_gallery(f)




            import webbrowser
            for f in files:
                webbrowser.open(f.resolve().as_uri())
                


            self.queue.task_done()

    async def cancel(self):
        self.cancel_flag = True

    async def add(self, prompt):

        await self.queue.put(prompt)

    async def start(self):
        if self.running:
            return

        self.running = True
        asyncio.create_task(self.worker())

import webbrowser

# ---------- GLOBAL ENGINE INSTANCE ----------
engine = ImageQueueManager()
