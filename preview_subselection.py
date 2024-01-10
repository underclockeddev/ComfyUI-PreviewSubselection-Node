from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
from os.path import join
import folder_paths
import random
import torch
import torchvision.transforms as transforms
import comfy.utils

class PreviewSubselection:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 1
        
    @classmethod
    def INPUT_TYPES(self):
        return {"required":{
                    "total_width": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                    "total_height": ("INT", {"default": 512, "min": 64, "max": 8192, "step": 8}),
                    "width": ("INT", {"forceInput": True, "min": 64, "max": 8192, "step": 8}),
                    "height": ("INT", {"forceInput": True, "min": 64, "max": 8192, "step": 8}),
                    "x": ("INT", {"forceInput": True, "min": 0, "max": 8192, "step": 8}),
                    "y": ("INT", {"forceInput": True, "min": 0, "max": 8192, "step": 8}),
                    "subselection_color": ("STRING", {"default": "red"}),
                    "background_color": ("STRING", {"default": "#444444"}),
                    "label": ("STRING", {"default": ""}),
                    "preview_method": (["Passthrough", "Render Here"],),
                    }
        }

    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "underclocked"
    OUTPUT_NODE = True
    FUNCTION = "show_preview"

    def show_preview(self, total_width, total_height, width, height, x, y, subselection_color, background_color, label, preview_method, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir)
        results = list()

        myImage = Image.new("RGBA", (total_width, total_height))
        draw = ImageDraw.Draw(myImage)
        draw.rectangle((0, 0, total_width, total_height), outline=background_color, fill=background_color, width=25)

        
        box = (x, y, x + width, y + height)
        draw.rectangle(box, outline=subselection_color, fill=subselection_color, width=0)

        text = label
        font_size = 100
        size = None
        while (size is None or size[0] > box[2] - box[0] or size[1] > box[3] - box[1]) and font_size > 0:
            font = ImageFont.truetype("cour.ttf", font_size)
            size = font.getsize_multiline(text)
            font_size -= 1
        draw.multiline_text((box[0], box[1]), text, "#000", font)

        im2arr = np.array(myImage)
        img = Image.fromarray(np.clip(im2arr, 0, 255).astype(np.uint8))
        file = f"{filename}_.png"
        img.save(os.path.join(full_output_folder, file), compress_level=self.compress_level)
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": self.type
        })
        transform = transforms.ToTensor()
        tensor = transform(myImage)
        result = list()
        result.append(torch.from_numpy(np.array(myImage).astype(np.float32) / 255.0).unsqueeze(0))
        if preview_method == "Passthrough":
            return {"result": result}
        else:
            return {"ui": { "images": results }, "result": result}