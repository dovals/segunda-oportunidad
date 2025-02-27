from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)

# Configurar carpeta de imágenes
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ruta principal (Marketplace)
@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return render_template('index.html', image_files=image_files)

# Ruta de detalles del producto
@app.route('/detalle/<nombre>')
def detalle(nombre):
    producto = {
        'nombre': nombre,
        'imagen': nombre,
        'precio': '199.99',
        'descripcion': 'Descripción de ejemplo para este producto.',
        'telefono_contacto': '555-1234'
    }
    return render_template('detalles.html', producto=producto)

# Ruta para agregar productos
@app.route('/agregar_producto', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        imagen = request.files['imagen']
        if imagen:
            imagen.save(os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename))
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

if __name__ == '__main__':
    app.run(debug=True)
