# import pandas as pd
# from transformers import pipeline
# import torch

# # Sample data
# data = {
#     'Product Category': ['Smartphone', 'Smartphone', 'Laptop', 'Headphones', 'Smartwatch', 'Unknown', 'Unknown'],
#     'Review': [
#         'I love the camera on this phone!', 
#         'The battery life on my phone is amazing.', 
#         'This laptop is super fast and lightweight!', 
#         'These headphones have excellent sound quality.', 
#         'The fitness tracking features on this watch are very useful.', 
#         'This device helps me keep track of my daily activity.', 
#         'My home has never felt safer.'
#     ]
# }

# df = pd.DataFrame(data)

# # Initialize the zero-shot classification pipeline
# classifier = pipeline('zero-shot-classification',
#                        model='facebook/bart-large-mnli')


# # Known product categories
# known_labels = ['Smartphone', 'Laptop', 'Headphones', 'Smartwatch']

# # New product categories (potential labels)
# new_labels = ['Fitness Tracker', 'Home Security System']

# # Combine all labels
# labels = known_labels + new_labels


# # Create a new column 'Predicted Category' in the df to store the predictions
# df['Predicted Category'] = df['Review'].apply(lambda x: classifier(x, labels)['labels'][0])



from transformers import pipeline

# classifier = pipeline(
#     "zero-shot-classification",
#     model="joeddav/xlm-roberta-large-xnli",
#     tokenizer="joeddav/xlm-roberta-large-xnli",
#     use_fast=False  # penting: hindari konversi ke tiktoken
# )

# classifier = pipeline("zero-shot-classification",
#                       model="facebook/bart-large-mnli")
# result = classifier("Jelaskan mengenai beauty greed", candidate_labels=["produk pakan ternak", "informasi umum"])
# print(result)


# from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

# model = AutoModelForSequenceClassification.from_pretrained("joeddav/xlm-roberta-large-xnli")
# tokenizer = AutoTokenizer.from_pretrained("joeddav/xlm-roberta-large-xnli", use_fast=False)  # ini penting

# classifier = pipeline("zero-shot-classification", model=model, tokenizer=tokenizer)

# result = classifier(
#     "Saya suka belajar bahasa pemrograman.",
#     candidate_labels=["Pendidikan", "Olahraga", "Kesehatan"],
#     hypothesis_template="Teks ini tentang {}."
# )
# print(result)

from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/LaBSE")
tokens = tokenizer.tokenize("Saya makan nasi goreng")
print(tokens)

