from transformers import pipeline
from flask import Flask, request, jsonify
import time


# Load a pre-trained BERT model for question answering
qa_pipeline = pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")


app = Flask(__name__)

# Mock data: Structured more like an FAQ for a better fit with our QA model
data = {
    "aspirin": "Aspirin is used to reduce fever and relieve mild to moderate pain from conditions such as muscle aches, toothaches, common cold, and headaches. It may also be used to reduce pain and swelling in conditions such as arthritis.",
    "ibuprofen": "Ibuprofen is used to relieve pain from various conditions such as headache, dental pain, menstrual cramps, muscle aches, or arthritis. It is also used to reduce fever and to relieve minor aches and pain due to the common cold or flu."
}

# Enhanced search function using BERT for natural language understanding
def search_answer(question):
    start_time = time.time()
    # Assume the question is about a keyword we can handle like 'aspirin' or 'ibuprofen'
    keyword = 'aspirin' if 'aspirin' in question.lower() else 'ibuprofen'
    context = data[keyword]
    result = qa_pipeline(question=question, context=context)
    execution_time = time.time() - start_time  # End timing
    print(f"Execution Time: {execution_time} seconds")
    return result['answer']

@app.route('/query', methods=['POST'])
def answer_query():
    start_time = time.time()
    question = request.json.get('question', '')
    if not question:
        return jsonify({"answer": "No question provided."}), 400

    # Use the enhanced search function
    answer = search_answer(question)
    latency = time.time() - start_time  # End timing
    print(f"Response Latency: {latency} seconds")
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    app.run(debug=True)


