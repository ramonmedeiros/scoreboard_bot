from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/result", methods = ['POST'])
def post_result():
    return jsonify({"data": str(request.data),
                    "json" : str(request.json),
                    "form": str(request.form)})

@app.route("/leaderboard", methods = ['GET'])
def get_leaderboard():
    return "Leaderboard"

if __name__ == "__main__":
    app.run()
