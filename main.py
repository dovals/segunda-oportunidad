from flask import Flask, render_template, request, redirect, url_for, flash
import os
from database import registrar_vendedor  # Importamos la función desde database.py

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # Para manejar mensajes flash

# Configurar carpeta de imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ruta principal (Marketplace)
@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('index.html', image_files=image_files)

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        imagen = request.files['imagen']
        if imagen:
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename))
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

# Ruta para registrar vendedores
@app.route('/registro', methods=['GET', 'POST'], endpoint='registrar_vendedor')
def registrar_vendedor_route():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        telefono = request.form['telefono']
        password = request.form['password']

        # Usar la función de database.py para registrar al vendedor
        if registrar_vendedor(nombre, email, telefono, password):
            flash('Registro exitoso. ¡Ahora puedes iniciar sesión!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error al registrar. Intenta nuevamente.', 'danger')

    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)
