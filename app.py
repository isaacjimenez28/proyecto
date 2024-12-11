from flask import Flask, render_template, jsonify, request,redirect,url_for,session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from config import Config
#from models import db, Usuario, NivelUsuario
from werkzeug.security import generate_password_hash,check_password_hash
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

# Api Inicio reservacion
@app.route('/formulario', methods=['GET'])
def formulario():
    conexion = obtener_conexion()

    # Obtener lista de clientes
    query_cliente = "SELECT DISTINCT ID_Cliente_01 FROM reservaciones"
    conexion.execute(query_cliente)
    cliente = [row[0] for row in conexion.fetchall()]

    # Obtener lista de costos
    query_costo = "SELECT DISTINCT ID_Costo_01 FROM reservaciones"
    conexion.execute(query_costo)
    costo = [row[0] for row in conexion.fetchall()]

    conexion.close()
    return render_template('formulario.html', cliente=cliente, costo=costo)

@app.route('/reservacion', methods=['POST'])
def reservacion():
    ID_cliente_01 = request.form['ID_cliente_01']
    ID_Costo_01 = request.form['ID_Costo_01']
    fecha_entrada = request.form['fecha_entrada']
    fecha_salida = request.form['fecha_salida']

    if not ID_cliente_01 or not ID_Costo_01 or not fecha_entrada or not fecha_salida:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cliente (cliente, costo, fecha_entrada, fecha_salida)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (cliente, costo, fecha_entrada, fecha_salida))
            conexion.commit()

        return jsonify({'mensaje': 'Reservacion agregada correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close() 

#Api de cliente 
# Obtener todos los clientes
@app.route('/api/clientes', methods=['GET'])
def mostrar_clientes():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM cliente")
            resultado = cursor.fetchall()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Buscar cliente por ID
@app.route('/api/clientes/<int:id_cliente>', methods=['GET'])
def buscar_cliente(id_cliente):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM cliente WHERE ID_Cliente = %s", (id_cliente,))
            result = cursor.fetchone()

        if result:
            return jsonify(result)
        else:
            return jsonify({'mensaje': 'Cliente no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Agregar nuevo cliente
@app.route('/api/clientes', methods=['POST'])
def agregar_cliente():
    data = request.get_json()
    
    nombre = data.get('nombre')
    numero = data.get('numero')
    correo = data.get('correo')
    estatus = data.get('estatus', 'activo')  # Valor por defecto "activo"
      
    # Verifica si algún campo está vacío
    if not nombre or not numero or not correo:
        return jsonify({'mensaje': 'Faltan datos. Verifica tus datos.'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                INSERT INTO cliente (nombre, numero, correo, fecha_creacion, estatus)
                VALUES (%s, %s, %s, NOW(), %s)
            """, (nombre, numero, correo, estatus))
            conexion.commit()

        return jsonify({'mensaje': 'Cliente agregado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Editar cliente existente
@app.route('/api/clientes/<int:id_cliente>', methods=['PUT'])
def editar_cliente(id_cliente):
    data = request.get_json()
    
    nombre = data.get('nombre')
    numero = data.get('numero')
    correo = data.get('correo')
    usuario_modificacion = data.get('usuario_modificacion')
    estatus = data.get('estatus')

    # Verifica si los campos requeridos están presentes
    if not nombre or not numero or not correo or not usuario_modificacion:
        return jsonify({'mensaje': 'Faltan datos. Verifica tus datos.'}), 400

    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE cliente 
                SET nombre = %s, numero = %s, correo = %s, 
                    fecha_modificacion = NOW(), usuario_modificacion = %s, estatus = %s
                WHERE ID_Cliente = %s
            """, (nombre, numero, correo, usuario_modificacion, estatus, id_cliente))
            conexion.commit()

        return jsonify({'mensaje': 'Cliente actualizado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Eliminar cliente
@app.route('/api/clientes/<int:id_cliente>', methods=['DELETE'])
def eliminar_cliente(id_cliente):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM cliente WHERE ID_Cliente = %s", (id_cliente,))
            conexion.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Cliente no encontrado.'}), 404
        return jsonify({'mensaje': 'Cliente eliminado correctamente'}), 200
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1451:  # Restricción de clave foránea
            return jsonify({'error': 'No se puede eliminar el cliente porque está relacionado con otros datos.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

#Api de costo 
# Obtener todos los elementos
@app.route('/api/datos', methods=['GET'])
def mostrar_datos():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM costo")
            resultado = cursor.fetchall()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Buscar por ID
@app.route('/api/datos/<int:id_costo>', methods=['GET'])
def buscar_datos(id_costo):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM costo WHERE id_costo = %s", (id_costo,))
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
@app.route('/api/datos', methods=['POST'])
def agregar_datos():
    data = request.get_json()
    
    precio = data.get('precio')
    tipo_habitacion = data.get('tipo_habitacion')
    estatus = data.get('estatus')
      
    # Verifica si algún campo está vacío
    if not precio or not tipo_habitacion or not estatus:
        return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400

    # Si no hay errores, inserta los datos en la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO costo (precio, tipo_habitacion, fecha_creacion, estatus)
        VALUES (%s, %s, NOW(), %s)
    """, (precio, tipo_habitacion, estatus))
    conexion.commit()

    return jsonify({'mensaje': 'Elemento agregado correctamente'}), 201

@app.route('/api/datos/<int:id>', methods=['PUT'])
def editar_datos(id):
    try:
        data = request.get_json()

        precio = data.get('precio')
        tipo_habitacion = data.get('tipo_habitacion')
        estatus = data.get('estatus')
        
        # Verifica si algún campo está vacío
        if not precio or not tipo_habitacion or not estatus:
            return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400  

        # Actualizar los datos en la base de datos
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE costo 
                SET precio = %s, tipo_habitacion = %s, fecha_modificacion = NOW(), estatus = %s
                WHERE id_costo = %s
            """, (precio, tipo_habitacion, estatus, id))
            conexion.commit()

        return jsonify({'mensaje': 'Elemento editado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'conexion' in locals():  
            conexion.close()


# Eliminar un elemento
@app.route('/api/datos/<int:id>', methods=['DELETE'])
def eliminar_datos(id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM costo WHERE id_costo = %s", (id,))
            conexion.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Elemento no encontrado.'}), 404
        return jsonify({'mensaje': 'Elemento eliminado correctamente'}), 200
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1451:  # Código de error para restricción de clave foránea
            return jsonify({'error': 'No se puede eliminar el costo porque está en uso en reservaciones.'}), 400
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

#Api de perfiles 
# Obtener todos los perfiles
@app.route('/api/perfiles', methods=['GET'])
def mostrar_perfiles():
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM perfiles")
            resultado = cursor.fetchall()
        return jsonify(resultado)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Buscar perfil por ID
@app.route('/api/perfiles/<int:id>', methods=['GET'])
def buscar_perfil(id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT * FROM perfiles WHERE id = %s", (id,))
            perfil = cursor.fetchone()
        
        if perfil:
            return jsonify(perfil)
        else:
            return jsonify({'message': 'Perfil no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()

# Agregar nuevo perfil
@app.route('/api/perfiles', methods=['POST'])
def agregar_perfil():
    data = request.get_json()
    
    nombre = data.get('nombre')
    correo = data.get('correo')
    rol = data.get('rol')
    contrasena = data.get('contrasena')
    
    # Verifica si algún campo está vacío
    if not nombre or not correo or not rol or not contrasena:
        return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400

    # Insertar los datos en la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO perfiles (nombre, correo, rol, contrasena, fecha_creacion, fecha_modificacion, usuario_modificacion, estatus)
        VALUES (%s, %s, %s, %s, NOW(), NOW(), 'admin', 'activo')
    """, (nombre, correo, rol, contrasena))
    conexion.commit()

    return jsonify({'mensaje': 'Perfil agregado correctamente'}), 201

# Editar un perfil existente
@app.route('/api/perfiles/<int:id>', methods=['PUT'])
def editar_perfil(id):
    try:
        data = request.get_json()

        nombre = data.get('nombre')
        correo = data.get('correo')
        rol = data.get('rol')
        contrasena = data.get('contrasena')
        
        # Verifica si algún campo está vacío
        if not nombre or not correo or not rol or not contrasena:
            return jsonify({'mensaje': 'Falta un dato. Verifica tus datos.'}), 400  

        # Actualizar los datos en la base de datos
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("""
                UPDATE perfiles 
                SET nombre = %s, correo = %s, rol = %s, contrasena = %s, fecha_modificacion = NOW(), usuario_modificacion = 'admin', estatus = 'activo'
                WHERE id = %s
            """, (nombre, correo, rol, contrasena, id))
            conexion.commit()

        return jsonify({'mensaje': 'Perfil editado correctamente'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'conexion' in locals():  
            conexion.close()

# Eliminar un perfil
@app.route('/api/perfiles/<int:id>', methods=['DELETE'])
def eliminar_perfil(id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM perfiles WHERE id = %s", (id,))
            conexion.commit()
            if cursor.rowcount == 0:
                return jsonify({'error': 'Perfil no encontrado.'}), 404
        return jsonify({'mensaje': 'Perfil eliminado correctamente'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conexion.close()
        
        
if __name__ == '__main__':
    app.run(debug=True)
