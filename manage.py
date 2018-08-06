from flask import Flask
import json
app = Flask(__name__)


@app.route('/')
def index():
    return '<h1>网站备案中</h1>'


@app.route('/demo', methods=['GET'])
def home():
	t = {}
	t['rank'] = '9'
	return json.dumps(t, ensure_ascii=False)



if __name__ == '__main__':
    app.run(debug=True)
