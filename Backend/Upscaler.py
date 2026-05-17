from diffusers import StableDiffusionUpscalePipeline
import torch

pipe = None

def load_upscaler():

    global pipe

    if pipe is None:
        pipe = StableDiffusionUpscalePipeline.from_pretrained(
            "stabilityai/stable-diffusion-x4-upscaler"
        )

        if torch.cuda.is_available():
            pipe = pipe.to("cuda")

    return pipe


def upscale_image(image, prompt="high quality, ultra detailed"):

    return pipe(
        prompt=prompt,
        image=image
    ).images[0]

