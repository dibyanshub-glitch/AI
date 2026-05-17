from diffusers import StableDiffusionPipeline
import torch

pipe = None

def load_local_model():

    global pipe

    if pipe is None:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )

        if torch.cuda.is_available():
            pipe = pipe.to("cuda")

    return pipe


def generate_local(prompt):

    pipe = load_local_model()
    return pipe(prompt).images[0]
