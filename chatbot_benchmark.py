from flask import Flask, request, jsonify
import time
app = Flask(__name__)

# Mock data: A simple dictionary as our 'database'
data = {
    "aspirin": "Aspirin is used to reduce fever and relieve mild to moderate pain from conditions such as muscle aches, toothaches, common cold, and headaches. It may also be used to reduce pain and swelling in conditions such as arthritis.",
    "ibuprofen": "Ibuprofen is used to relieve pain from various conditions such as headache, dental pain, menstrual cramps, muscle aches, or arthritis. It is also used to reduce fever and to relieve minor aches and pain due to the common cold or flu."
}

# Function to search for keywords in the database
def search_database(query):
    start_time = time.time()
    keywords = query.lower().split()
    for keyword in keywords:
        if keyword in data:
            return data[keyword]
        
    execution_time = time.time() - start_time  # End timing
    print(f"Execution Time: {execution_time} seconds")
    return "No information available for the requested product."

@app.route('/query', methods=['POST'])
def answer_query():
    start_time = time.time()
    question = request.json.get('question', '')
    if not question:
        return jsonify({"answer": "No question provided."}), 400

    # Search the database using the question
    answer = search_database(question)
    latency = time.time() - start_time  # End timing
    print(f"Response Latency: {latency} seconds")
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
