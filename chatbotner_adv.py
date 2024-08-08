from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import time
app = Flask(__name__)

# Initialize the tokenizer and model for NER with a biomedical NER model
ner_model_name = "d4data/biomedical-ner-all"
tokenizer = AutoTokenizer.from_pretrained(ner_model_name)
model = AutoModelForTokenClassification.from_pretrained(ner_model_name)
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# Load a pre-trained BERT model for question answering
qa_model_name = "bert-large-uncased-whole-word-masking-finetuned-squad"
qa_pipeline = pipeline("question-answering", model=qa_model_name)

# Mock data
data = {
    "aspirin": "Aspirin is used to reduce fever and relieve mild to moderate pain from conditions such as muscle aches, toothaches, common cold, and headaches. It may also be used to reduce pain and swelling in conditions such as arthritis.",
    "ibuprofen": "Ibuprofen is used to relieve pain from various conditions such as headache, dental pain, menstrual cramps, muscle aches, or arthritis. It is also used to reduce fever and to relieve minor aches and pain due to the common cold or flu."
}

def get_context(question):
    start_time = time.time()
    # Use NER to detect drug names or other relevant entities
    ner_results = ner_pipeline(question)

    # Merge subwords into full entities
    entities = []
    current_entity = None
    current_entity_group = None

    for entity in ner_results:
        if entity['entity_group'] == current_entity_group:
            current_entity += entity['word'].replace("##", "")
        else:
            if current_entity:
                entities.append({"word": current_entity, "entity_group": current_entity_group})
            current_entity = entity['word'].replace("##", "")
            current_entity_group = entity['entity_group']
    
    if current_entity:
        entities.append({"word": current_entity, "entity_group": current_entity_group})


    # Extract relevant entities based on expected tags
    drugs = [entity['word'].lower() for entity in entities if entity['entity_group'] == 'Medication' and entity['word'].lower() in data]


    if drugs:
        return data[drugs[0]]  # Return context for the first recognized drug
    execution_time = time.time() - start_time  # End timing
    print(f"Execution Time: {execution_time} seconds")
    return "Sorry, no detailed information available."

@app.route('/query', methods=['POST'])
def answer_query():
    start_time = time.time()
    question = request.json.get('question', '')
    if not question:
        return jsonify({"answer": "No question provided."}), 400

    context = get_context(question)
    if context == "Sorry, no detailed information available.":
        return jsonify({"answer": context}), 404

    # Process the question with the QA pipeline using the retrieved context
    answer = qa_pipeline(question=question, context=context)
    latency = time.time() - start_time  # End timing
    print(f"Response Latency: {latency} seconds")
    return jsonify({"question": question, "answer": answer['answer']})

if __name__ == '__main__':
    app.run(debug=True)
