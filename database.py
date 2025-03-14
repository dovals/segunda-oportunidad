import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash  # Usar funciones de werkzeug

# Configuración de la base de datos
db_config = {
    'user': 'root',  # Cambia por tu usuario de MySQL
    'password': '',  # Cambia por tu contraseña de MySQL
    'host': 'localhost',
    'database': 'segunda_oportunidad',  # Nombre de la base de datos
    'raise_on_warnings': True
}


# Función para crear la base de datos si no existe
def crear_base_de_datos():
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            # Intentamos crear la base de datos si no existe
            cursor.execute("CREATE DATABASE IF NOT EXISTS segunda_oportunidad")
            conn.commit()
            print("Base de datos creada o ya existe.")
        except mysql.connector.Error as err:
            print(f"Error al crear la base de datos: {err}")
        finally:
            conn.close()


# Función para conectar a la base de datos
def obtener_conexion():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar con la base de datos: {err}")
        return None


# Función para crear las tablas en la base de datos
def crear_tablas():
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vendedores (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    telefono VARCHAR(50),
                    password VARCHAR(255)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255),
                    imagen VARCHAR(255),
                    precio FLOAT,
                    descripcion TEXT,
                    telefono_contacto VARCHAR(10),
                    vendedor_id INT,
                    FOREIGN KEY (vendedor_id) REFERENCES vendedores(id)
                )
            """)
            conn.commit()
            print("Tablas creadas o ya existen.")
        except mysql.connector.Error as err:
            print(f"Error al crear las tablas: {err}")
        finally:
            conn.close()


# Función para registrar un vendedor
def registrar_vendedor(nombre, email, telefono, password):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            # Encriptar la contraseña antes de guardarla
            hashed_password = generate_password_hash(password)

            cursor.execute("INSERT INTO vendedores (nombre, email, telefono, password) VALUES (%s, %s, %s, %s)",
                           (nombre, email, telefono, hashed_password))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al registrar el vendedor: {err}")
        finally:
            conn.close()
    return False


# Función para validar el inicio de sesión del vendedor
def validar_usuario(email, password):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, password FROM vendedores WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                vendedor_id, password_hash = result
                # Verifica la contraseña usando la función de hash
                if check_password_hash(password_hash, password):  # Verificar el hash de la contraseña
                    return vendedor_id  # Devuelve el ID del vendedor si la contraseña es correcta
        except mysql.connector.Error as err:
            print(f"Error al validar usuario: {err}")
        finally:
            conn.close()
    return None


# Función para obtener los productos de un vendedor
def obtener_productos_por_vendedor(vendedor_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM productos WHERE vendedor_id = %s", (vendedor_id,))
            productos = cursor.fetchall()
            return productos
        except mysql.connector.Error as err:
            print(f"Error al obtener productos: {err}")
        finally:
            conn.close()
    return []


# Función para obtener un producto por su ID
def obtener_producto_por_id(producto_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM productos WHERE id = %s", (producto_id,))
            producto = cursor.fetchone()
            return producto
        except mysql.connector.Error as err:
            print(f"Error al obtener producto por ID: {err}")
        finally:
            conn.close()
    return None


# Función para agregar un producto
def agregar_producto(nombre, imagen, precio, descripcion, telefono_contacto, vendedor_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO productos (nombre, imagen, precio, descripcion, telefono_contacto, vendedor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, imagen, precio, descripcion, telefono_contacto, vendedor_id))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al agregar producto: {err}")
        finally:
            conn.close()
    return False


# Función para editar un producto
def editar_producto(producto_id, nombre, imagen, precio, descripcion, telefono_contacto):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE productos
                SET nombre = %s, imagen = %s, precio = %s, descripcion = %s, telefono_contacto = %s
                WHERE id = %s
            """, (nombre, imagen, precio, descripcion, telefono_contacto, producto_id))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al editar producto: {err}")
        finally:
            conn.close()
    return False


# Función para eliminar un producto
def eliminar_producto(producto_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM productos WHERE id = %s", (producto_id,))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al eliminar producto: {err}")
        finally:
            conn.close()
    return False
