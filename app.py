from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, Usuario, NivelUsuario
from werkzeug.security import generate_password_hash
import pymysql

app = Flask(__name__)

def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='isa123',
        db='hotel',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def inicio():
    return render_template("index.html")

@app.route('/pages-profile')
def profile():
    return render_template('pages-profile.html')

@app.route('/pages-sign-in')
def sign():
    return render_template('pages-sign-in.html')

@app.route('/cliente')
def cliente():
    return render_template('cliente.html')

@app.route('/costo')
def costo():
    return render_template('costo.html')

# Inicio Api del index reservacion
@app.route('/api/reservacion', methods=['GET'])
def mostrar_reservacion():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM reservacion")
            resultado = cursor.fetchall()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Buscar por ID
@app.route('/api/reservacion/<int:id_reservacion>', methods=['GET'])
def buscar_reservacion(id_reservacion):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM reservacion WHERE id_reservacion = %s", (id_reservacion,))
            result = cursor.fetchone()

        if result:
            return jsonify(result)
        else:
            return jsonify({'message': 'Dato no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Agregar nuevo dato
@app.route('/api/reservacion', methods=['POST'])
def agregar_reservacion():
    data = request.get_json()
    
    fecha_entrada = data.get('fecha_entrada')
    fecha_salida = data.get('fecha_salida')
      
    # Verifica si algún campo está vacío
    if not fecha_entrada or not fecha_salida:
        return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400

    # Si no hay errores, inserta los datos en la base de datos
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reservacion (fecha_entrada, fecha_salida, fecha_creacion)
                VALUES (%s, %s, NOW())
            """, (fecha_entrada, fecha_salida))
            conexion.commit()
        return jsonify({'mensaje': 'Elemento agregado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Editar un dato
@app.route('/api/reservacion/<int:id>', methods=['PUT'])
def editar_reservacion(id):
    try:
        data = request.get_json()

        fecha_entrada = data.get('fecha_entrada')
        fecha_salida = data.get('fecha_salida')
        
        # Verifica si algún campo está vacío
        if not fecha_entrada or not fecha_salida:
            return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400  

        # Actualizar los datos en la base de datos
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE reservacion
                SET fecha_entrada = %s, fecha_salida = %s, fecha_modificacion = NOW()
                WHERE id_reservacion = %s
            """, (fecha_entrada, fecha_salida, id))
            conexion.commit()

        return jsonify({'mensaje': 'Elemento editado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'conexion' in locals():  
            conexion.close()

# Eliminar un elemento
@app.route('/api/reservacion/<int:id>', methods=['DELETE'])
def eliminar_reservacion(id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM reservacion WHERE id_reservacion = %s", (id,))
            conexion.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Elemento no encontrado.'}), 404
        return jsonify({'mensaje': 'Elemento eliminado correctamente'}), 200
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1451:  # Código de error para restricción de clave foránea
            return jsonify({'error': 'No se puede eliminar porque está en uso.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()
# Fin de Api de Index reservacion
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    Email = data.get('Email')
    Password = data.get('Password')
    
    if not Email or not Password:
        return jsonify({'status': 'error', 'message': 'Faltan datos'}), 400
    
    user = Usuario.query.filter_by(Email=Email, estatus=1).first()
    
    if user and Password:
        session['usuario'] = user.id_usuario
        return jsonify({'status': 'success', 'message': 'Login exitoso'})
    return jsonify({'status': 'error', 'message': 'Datos incorrectos'})

@app.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('pages-sign-in'))
    return render_template('index.html')

@app.route('/api/usuarios', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_usuarios():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        usuarios=Usuario.query.paginate(page, per_page, False)
        data = [{
            'id_usuario': u.id_usuario,
            'nombres': u.nombres,
            'apepat': u.apepat,
            'apemat': u.apemat,
            'Email': u.Email,
        }]        

if __name__ == '__main__':
    app.run(debug=True)
