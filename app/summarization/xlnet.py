import torch
from transformers import XLNetTokenizer, XLNetLMHeadModel

class XLNetTextSummarizer:
    def __init__(self):
        self.model = XLNetLMHeadModel.from_pretrained('xlnet-base-cased')
        self.tokenizer = XLNetTokenizer.from_pretrained('xlnet-base-cased')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def summarize(self, text, num_beams=8, length_penalty=1.0, max_length=142):
        inputs = self.tokenizer.encode("summarize: " + text, return_tensors='pt',truncation=True).to(self.device)
        min_length = int(len(text) * 0.3)  # 30% do tamanho do texto original
        summary_ids = self.model.generate(inputs, num_beams=num_beams, length_penalty=length_penalty,
                                           max_length= len(text)+1,min_length=min_length,early_stopping=True)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                   summary_ids]
        return summary
