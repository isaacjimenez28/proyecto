from flask import Flask, jsonify, request
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

# Obtener todos los elementos
@app.route('/api/datos', methods=['GET'])
def mostrar_datos():
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
@app.route('/api/datos/<int:id_reservacion>', methods=['GET'])
def buscar_datos(id_reservacion):
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
@app.route('/api/datos', methods=['POST'])
def agregar_datos():
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
@app.route('/api/datos/<int:id>', methods=['PUT'])
def editar_datos(id):
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
@app.route('/api/datos/<int:id>', methods=['DELETE'])
def eliminar_datos(id):
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

if __name__ == '__main__':
    app.run(debug=True)