# summarization/bert.py
from transformers import pipeline, BartTokenizer, BartForConditionalGeneration


def summarize_bert(text):
    summarizer = pipeline("summarization")
    # Calcular o comprimento desejado do resumo (30% do comprimento total do texto)
    desired_length = int(0.3 * len(text.split()))

    summary = summarizer(text, max_length=desired_length, min_length=5, length_penalty=2.0, num_beams=4)

    return summary[0]['summary_text']


def summarize_bart(text, compression_ratio=0.3):
    # Carregar o modelo pré-treinado BART para resumo
    model_name = "facebook/bart-large-cnn"
    tokenizer = BartTokenizer.from_pretrained(model_name)
    model = BartForConditionalGeneration.from_pretrained(model_name)

    # Tokenizar o texto
    input_ids = tokenizer.encode(text, return_tensors="pt", max_length=1024, truncation=True)

    # Calcular o novo comprimento máximo com base na taxa de compressão
    max_length = int(len(input_ids[0]) * compression_ratio)

    # Gerar o resumo
    summary_ids = model.generate(input_ids, max_length=max_length, length_penalty=2.0, num_beams=4, early_stopping=True)

    # Decodificar o resumo de volta para texto
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary