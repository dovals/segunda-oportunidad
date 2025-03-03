import psycopg2
from werkzeug.security import generate_password_hash

# Configuración de la base de datos
DB_CONFIG = {
    'dbname': 'segunda-oportunidad',
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': '3306'
}


def conectar_db():
    """Establece la conexión con la base de datos."""
    return psycopg2.connect(**DB_CONFIG)


def crear_tablas():
    """Crea las tablas necesarias si no existen."""
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Crear tabla 'vendedores'
        cur.execute("""
        CREATE TABLE IF NOT EXISTS vendedores (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            telefono VARCHAR(15),
            password VARCHAR(255)
        )
        """)

        # Crear tabla 'productos' (si también necesitas una tabla para los productos)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            descripcion TEXT,
            precio DECIMAL(10, 2),
            imagen VARCHAR(255),
            vendedor_id INTEGER REFERENCES vendedores(id)
        )
        """)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error al crear las tablas: {e}")


def registrar_vendedor(nombre, email, telefono, password):
    """Registra un nuevo vendedor en la base de datos."""
    hashed_password = generate_password_hash(password)
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO vendedores (nombre, email, telefono, password) VALUES (%s, %s, %s, %s)",
                    (nombre, email, telefono, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al registrar vendedor: {e}")
        return False


# Llamada a la función para crear las tablas si no existen
crear_tablas()
