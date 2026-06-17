
import os
from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "llama-3.1-8b-instant")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")

VISION_BACKEND = os.getenv("VISION_BACKEND", "groq")
MLX_VISION_MODEL = os.getenv("MLX_VISION_MODEL", "mlx-community/Qwen2.5-VL-3B-Instruct-4bit")

POLICY_DIR = "data/policy"
CHROMA_DIR = "vectorstore/chroma"

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")