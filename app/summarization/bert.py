import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class TextSummarizer:
    def __init__(self, model_name):
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def summarize(self, text, compression_rate=0.3, num_beams=4, length_penalty=2.0):
        tokens = self.tokenizer.encode("summarize: " + text, return_tensors='pt').to(self.device)
        summary_length = int(len(tokens[0]) * compression_rate)
        summary_ids = self.model.generate(tokens, num_beams=8, max_length=len(tokens[0]) + 1, length_penalty=2.0)
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
