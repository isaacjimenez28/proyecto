from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/pages-profile')
def profile():
    return render_template('pages-profile.html')

@app.route('/pages-sign-in')
def sign():
    return render_template('pages-sign-in.html')

if __name__ == '__main__':
    app.run(debug=True)
