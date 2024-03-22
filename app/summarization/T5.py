import torch
import time
from transformers import T5ForConditionalGeneration, T5Tokenizer


class T5TextSummarizer:
    def __init__(self):
        self.model = T5ForConditionalGeneration.from_pretrained('t5-base')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-base')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def summarize(self, text, num_beams=8, length_penalty=1.0, max_length=142, min_length=124):
        start_time = time.time()
        inputs = self.tokenizer.encode("summarize: " + text, return_tensors='pt', max_length=int(len(text))).to(
            self.device)
        summary_ids = self.model.generate(inputs, num_beams=num_beams, length_penalty=length_penalty,
                                          max_length=int(len(text)), min_length=int(len(text) * 0.3),
                                          early_stopping=True)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                   summary_ids]
        end_time = time.time()
        processing_time = end_time - start_time
        return summary, processing_time
