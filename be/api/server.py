from flask import Flask, request, jsonify

app = Flask(__name__)
apiPrefix = '/api'
@app.route(f'{apiPrefix}/graph', methods=['GET'])
def get_graph():
    return jsonify({
        'message': 'Hello, World!'
    })

if __name__ == '__main__':
    app.run(debug=True)