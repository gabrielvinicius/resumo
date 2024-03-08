import torch
from transformers import BartForConditionalGeneration, BartTokenizer


class BartTextSummarizer:
    def __init__(self):
        model_name = 'facebook/bart-large-cnn'
        self.model = BartForConditionalGeneration.from_pretrained(model_name)
        self.tokenizer = BartTokenizer.from_pretrained(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)

    def summarize(self, text, num_beams=4, length_penalty=2.0, max_length=142, min_length=56):
        inputs = self.tokenizer([text], return_tensors='pt').to(self.device)
        summary_ids = self.model.generate(inputs['input_ids'], num_beams=num_beams, length_penalty=length_penalty,
                                          max_length=max_length, min_length=min_length, early_stopping=True)
        summary = [self.tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in
                   summary_ids]
        return summary
