from flask import Flask, jsonify, request
import pymysql

app = Flask(__name__)

# Configuración de la conexión a la base de datos MySQL
def obtener_conexion():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='isa123',
        db='hotel',
        cursorclass=pymysql.cursors.DictCursor
    )

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
