from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def hello_name():
   return 'Hello World!'

if __name__ == '__main__':
   app.run(debug=True)