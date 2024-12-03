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

if __name__ == '__main__':
    app.run(debug=True)
