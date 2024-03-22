import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer


class GPT2TextSummarizer:
    def __init__(self):
        self.model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def summarize(self, text, max_length=142):
        inputs = self.tokenizer.encode("summarize: " + text, return_tensors='pt').to(self.device)
        summary_ids = self.model.generate(inputs, max_length=len(text) + 1, early_stopping=True)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                   summary_ids]
        return summary
