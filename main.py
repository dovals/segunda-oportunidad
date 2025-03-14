from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid
import mysql.connector  # Importar mysql.connector para la conexión a la base de datos
from database import crear_base_de_datos, crear_tablas, obtener_conexion, \
    obtener_productos_por_vendedor, agregar_producto, editar_producto, eliminar_producto, obtener_producto_por_id

app = Flask(__name__)

# Crear la base de datos y las tablas al iniciar la aplicación
crear_base_de_datos()
crear_tablas()
app.secret_key = 'clave_secreta'  # Para los mensajes flash

# Configuración para cargar imágenes
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Asegurar que la carpeta de uploads exista
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Función para verificar la extensión de las imágenes
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# Ruta principal - Listar productos con imágenes
@app.route('/')
def index():
    return render_template('index.html')


# Ruta para registrar o iniciar sesión
@app.route('/vendedor', methods=['GET', 'POST'])
def vendedor():
    if request.method == 'POST':
        if "login" in request.form:
            email = request.form['email']
            password = request.form['password']

            vendedor_id = validar_usuario(email, password)
            if vendedor_id:
                session['vendedor_id'] = vendedor_id
                flash('¡Inicio de sesión exitoso!', 'success')
                return redirect(url_for('dashboard_vendedor'))
            else:
                flash('Correo o contraseña incorrectos', 'danger')

    return render_template('vendedor.html')


# Ruta para Dashboard - Gestionar productos de un vendedor
@app.route('/dashboard_vendedor', methods=['GET', 'POST'])
def dashboard_vendedor():
    if 'vendedor_id' not in session:
        return redirect(url_for('vendedor'))  # Si no hay sesión, redirigir al login

    vendedor_id = session['vendedor_id']

    # Obtener productos del vendedor
    productos = obtener_productos_por_vendedor(vendedor_id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        imagenes = request.files.getlist('imagenes')  # Obtener todas las imágenes
        precio = float(request.form['precio'])  # Convertir el precio a un valor flotante
        descripcion = request.form['descripcion']
        telefono_contacto = request.form['telefono_contacto']

        # Validar que se hayan subido al menos 5 imágenes
        if len(imagenes) < 5:
            flash('Debes subir al menos 5 imágenes', 'danger')
            return render_template('dashboard.html', productos=productos)

        imagen_paths = []
        for imagen in imagenes:
            if imagen and allowed_file(imagen.filename):
                # Generar un nombre único para cada imagen
                filename = f"{vendedor_id}_{uuid.uuid4().hex}_{secure_filename(imagen.filename)}"
                imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                imagen_paths.append(f'uploads/{filename}')  # Ruta relativa a la carpeta estática

        # Agregar producto con múltiples imágenes
        if agregar_producto(nombre, imagen_paths, precio, descripcion, telefono_contacto, vendedor_id):
            flash('Producto agregado correctamente', 'success')
            return redirect(url_for('dashboard_vendedor'))  # Recargar la página para ver el producto agregado

    return render_template('dashboard.html', productos=productos)


# Ruta para editar un producto
@app.route('/editar_producto/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto_route(producto_id):
    producto = obtener_producto_por_id(producto_id)

    if request.method == 'POST':
        nombre = request.form['nombre']
        imagenes = request.files.getlist('imagenes')  # Obtener todas las imágenes
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        telefono_contacto = request.form['telefono_contacto']

        # Usar las imágenes actuales si no se suben nuevas
        imagen_paths = producto['imagenes']

        if len(imagenes) > 0:
            # Asegurarse de que se suban al menos 5 imágenes
            if len(imagenes) < 5:
                flash('Debes subir al menos 5 imágenes', 'danger')
                return redirect(url_for('editar_producto_route', producto_id=producto_id))

            imagen_paths = []
            for imagen in imagenes:
                if imagen and allowed_file(imagen.filename):
                    filename = secure_filename(imagen.filename)
                    imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    imagen.save(imagen_path)
                    imagen_paths.append(f'uploads/{filename}')  # Ruta relativa a la carpeta estática

        if editar_producto(producto_id, nombre, imagen_paths, precio, descripcion, telefono_contacto):
            flash('Producto actualizado correctamente', 'success')
            return redirect(url_for('dashboard_vendedor'))

    return render_template('editar_producto.html', producto=producto)


# Ruta para crear un producto
@app.route('/crear_producto', methods=['GET', 'POST'])
def crear_producto():
    if 'vendedor_id' not in session:
        flash('Debes iniciar sesión primero.', 'danger')
        return redirect(url_for('vendedor'))  # Redirigir al login si no hay sesión activa

    vendedor_id = session['vendedor_id']  # Obtener el vendedor_id de la sesión

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        imagenes = request.files.getlist('imagenes')  # Obtener todas las imágenes
        precio = float(request.form['precio'])  # Convertir el precio a un valor flotante
        descripcion = request.form['descripcion']
        telefono_contacto = request.form['telefono_contacto']

        # Validar que se hayan subido al menos 5 imágenes
        if len(imagenes) < 5:
            flash('Debes subir al menos 5 imágenes', 'danger')
            return render_template('crear_producto.html')  # Si no, mostrar el mensaje de error

        imagen_paths = []
        for imagen in imagenes:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(imagen_path)

                # Guardar solo la ruta relativa
                imagen_paths.append(f'uploads/{filename}')

        # Aquí es donde se agrega el producto con múltiples imágenes a la base de datos
        if agregar_producto(nombre, imagen_paths, precio, descripcion, telefono_contacto, vendedor_id):
            flash('Producto agregado correctamente', 'success')
            return redirect(url_for('dashboard_vendedor'))  # Redirige al dashboard

        else:
            flash('Error al agregar producto', 'danger')

    return render_template('crear_producto.html')  # Asegúrate de tener la plantilla 'crear_producto.html'

@app.route('/eliminar_imagen/<int:producto_id>/<string:imagen>', methods=['POST'])
def eliminar_imagen(producto_id, imagen):
    producto = obtener_producto_por_id(producto_id)
    imagenes = producto['imagenes'].split(',')  # Suponiendo que las imágenes están separadas por comas

    # Verificar si la imagen existe en las rutas del producto
    if imagen in imagenes:
        # Eliminar la imagen del servidor
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imagen))
        except FileNotFoundError:
            flash('La imagen no fue encontrada en el servidor', 'danger')
            return redirect(url_for('editar_producto_route', producto_id=producto_id))

        # Eliminar la imagen de la base de datos (actualizar las rutas)
        imagenes.remove(imagen)
        imagenes_str = ",".join(imagenes)  # Reconvertir la lista a una cadena separada por comas

        # Actualizar en la base de datos
        if editar_producto(producto_id, producto['nombre'], imagenes_str, producto['precio'], producto['descripcion'], producto['telefono_contacto']):
            flash('Imagen eliminada correctamente', 'success')
        else:
            flash('Error al eliminar imagen', 'danger')
    else:
        flash('Imagen no encontrada en el producto', 'danger')

    return redirect(url_for('editar_producto_route', producto_id=producto_id))

# Ruta para eliminar un producto
@app.route('/eliminar_producto/<int:producto_id>', methods=['POST'])
def eliminar_producto_route(producto_id):
    if eliminar_producto(producto_id):
        flash('Producto eliminado correctamente', 'success')
    else:
        flash('Error al eliminar producto', 'danger')
    return redirect(url_for('dashboard_vendedor'))


def agregar_producto(nombre, imagen_paths, precio, descripcion, telefono_contacto, vendedor_id):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        try:
            # Guardamos las imágenes como un JSON o texto en la base de datos
            imagen_paths_str = ",".join(imagen_paths)  # Convertir las rutas en una cadena separada por comas

            cursor.execute("""
                INSERT INTO productos (nombre, imagen, precio, descripcion, telefono_contacto, vendedor_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, imagen_paths_str, precio, descripcion, telefono_contacto, vendedor_id))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error al agregar producto: {err}")
        finally:
            cursor.close()
            conn.close()
    return False



if __name__ == '__main__':
    app.run(debug=True)
