from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')

def home():
    return jsonify(
        {"name": "Task API", 
         "version": "1.0", 
         "endpoints": ["/tasks"]})
     
     
     
app.route('/health')
def health():
    return jsonify({"status": "ok"})
    
if __name__ == '__main__':
    app.run(debug=True, port=8000)