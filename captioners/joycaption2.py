import os
import sys

import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoProcessor, LlavaForConditionalGeneration

# Constants
MODEL_NAME = "fancyfeast/llama-joycaption-alpha-two-hf-llava"
MODEL_PATH = "models/llama-joycaption-alpha-two-hf-llava"

# Ensure model is downloaded
if not os.path.exists(MODEL_PATH):
    print("Model not found. Downloading...")
    os.makedirs("models", exist_ok=True)
    snapshot_download(repo_id=MODEL_NAME, local_dir=MODEL_PATH)
    print("Download complete!")

# Load model and processor
print("Loading model...")
processor = AutoProcessor.from_pretrained(MODEL_PATH)
llava_model = LlavaForConditionalGeneration.from_pretrained(
    MODEL_PATH, torch_dtype=torch.bfloat16, device_map="auto"
)
llava_model.eval()


def describe_image(image_path):
    """Generate a descriptive caption for a single image and save it as a .txt file."""
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file '{image_path}' not found!")
        return

    # Load image
    image = Image.open(image_path).convert("RGB")

    # Build the conversation prompt
    convo = [
        {"role": "system", "content": "You are a helpful image captioner."},
        {
            "role": "user",
            "content": "Write a long descriptive caption for this image in a formal tone. Include information about lighting. Include information about camera angle. Do NOT mention any text that is in the image.",
        },
    ]

    # Format conversation for LLaVA
    convo_string = processor.apply_chat_template(
        convo, tokenize=False, add_generation_prompt=True
    )

    # Process inputs
    inputs = processor(text=[convo_string], images=[image], return_tensors="pt").to(
        "cuda"
    )
    inputs["pixel_values"] = inputs["pixel_values"].to(torch.bfloat16)

    # Generate caption
    with torch.no_grad():
        generate_ids = llava_model.generate(
            **inputs,
            max_new_tokens=300,
            do_sample=True,
            suppress_tokens=None,
            use_cache=True,
            temperature=0.6,
            top_k=None,
            top_p=0.9,
        )[0]

    # Trim prompt from output
    generate_ids = generate_ids[inputs["input_ids"].shape[1] :]

    # Decode and clean up caption
    caption = processor.tokenizer.decode(
        generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
    ).strip()

    # Save caption to .txt file
    txt_path = os.path.splitext(image_path)[0] + ".txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(caption)

    print(f"✅ Caption saved: {txt_path}")


def process_folder(folder_path):
    """Process all images in a given folder."""
    if not os.path.exists(folder_path):
        print(f"❌ Error: Folder '{folder_path}' not found!")
        return

    # Supported image formats
    valid_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

    # Find all image files
    image_files = [
        f for f in os.listdir(folder_path) if f.lower().endswith(valid_extensions)
    ]

    if not image_files:
        print(f"❌ No valid images found in '{folder_path}'")
        return

    print(f"📂 Processing {len(image_files)} images in '{folder_path}'...")

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        describe_image(image_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utils/describe-image.py <image_or_folder_path>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isdir(path):
        process_folder(path)  # Process all images in folder
    elif os.path.isfile(path):
        describe_image(path)  # Process a single image
    else:
        print("❌ Error: Invalid file or folder path.")
