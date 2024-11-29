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

if __name__ == '__main__':
    app.run(debug=True)
