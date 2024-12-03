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

<<<<<<< HEAD

@app.route('/Reservacion')
def reservacion():
    return render_template('Reservacion.html')

=======
>>>>>>> 5bcab4aff5e1e4a80fde8aabfbce89be064193d2
@app.route('/cliente')
def cliente():
    return render_template('cliente.html')

@app.route('/costo')
def costo():
    return render_template('costo.html')

if __name__ == '__main__':
    app.run(debug=True)