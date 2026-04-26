# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import requests
import os
import torch
from typing import Optional
from utils.logger import logger
import sys
import os

# Ensure root (training/) is accessible for configs
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configs.config import config
import pytorch_lightning as pl
from transformers import AutoModelForCausalLM, AutoConfig, AutoTokenizer

OLLAMA_GENERATE_URL = config.ollama_generate_url
OLLAMA_MODEL = config.ltm_embedding
session = requests.Session()

class LocalCheckpointRefiner:
    """Uses a custom PyTorch Lightning checkpoint to refine text."""
    def __init__(self, checkpoint_path: str):
        logger.info(f"Loading local PyTorch refiner from {checkpoint_path}...")
        self.available = False
        self.module = None
        self.tokenizer = None
        
        try:
            model_config = AutoConfig.from_pretrained("EleutherAI/gpt-neo-125M")
            model_config.num_hidden_layers = 12
            model_config.hidden_size = 1024
            model_config.num_attention_heads = 16
            
            class RCODLightningModule(pl.LightningModule):
                def __init__(self, model_config):
                    super().__init__()
                    self.model = AutoModelForCausalLM.from_config(model_config)
                def forward(self, input_ids, attention_mask=None):
                    return self.model(input_ids=input_ids, attention_mask=attention_mask)

            if not os.path.exists(checkpoint_path):
                logger.warning(f"Checkpoint not found at {checkpoint_path}")
                return

            self.module = RCODLightningModule.load_from_checkpoint(
                checkpoint_path, 
                model_config=model_config,
                map_location="cpu"
            )
            self.module.eval()
            self.tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.available = True
            logger.info("Local PyTorch model loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load PyTorch checkpoint: {e}")

    def refine(self, text: str, max_length: int = 150) -> str:
        if not self.available or not self.module or not self.tokenizer:
            return text
            
        prompt = f"Refine and summarize this memory for context: {text}\nRefined:"
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=256)
        
        try:
            with torch.no_grad():
                output_tokens = self.module.model.generate(
                    **inputs, 
                    max_new_tokens=max_length,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            refined_text = self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)
            if "Refined:" in refined_text:
                refined_text = refined_text.split("Refined:")[-1].strip()
            return refined_text
        except Exception as e:
            logger.error(f"Error during PyTorch generation: {e}")
            return text


class OllamaRefiner:
    """Uses the local instruction-tuned model via Ollama for reliable summarization."""
    def refine(self, text: str, max_length: int = 150) -> str:
        prompt = f"Summarize and condense the following memory into a clear, concise bullet point for AI context. Do not add conversational filler. Memory: '{text}'"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_length,
                "temperature": 0.3
            }
        }
        try:
            response = session.post(OLLAMA_GENERATE_URL, json=payload, timeout=15)
            response.raise_for_status()
            return response.json().get("response", text).strip()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama refinement failed over network: {e}")
            return text
        except Exception as e:
            logger.error(f"Unexpected error in Ollama refinement: {e}")
            return text


def refine_memory(text: str, method: str = "ollama", ckpt_path: Optional[str] = None) -> str:
    """Main interface to refine memory."""
    if method == "ollama":
        refiner = OllamaRefiner()
        return refiner.refine(text)
    elif method == "pytorch":
        default_ckpt = config.ltm_dir.parent / "lightning_logs" / "version_2" / "checkpoints" / "epoch=4-step=415.ckpt"
        ckpt = ckpt_path if ckpt_path else str(default_ckpt)
        refiner = LocalCheckpointRefiner(ckpt)
        return refiner.refine(text)
    return text


if __name__ == "__main__":
    test_text = "The user prefers Vanilla CSS over TailwindCSS because they value control over abstraction and want to minimize dependency bloat in their projects."
    logger.info("Testing Qwen/Ollama Refiner (Primary)...")
    logger.info(f"Refined: {refine_memory(test_text, method='ollama')}")
    
    logger.info("Testing PyTorch Checkpoint Refiner (Experimental)...")
    logger.info(f"Refined: {refine_memory(test_text, method='pytorch')}")
