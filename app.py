from flask import Flask, request, render_template, redirect, url_for
from PIL import Image

import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'bmp'}

# Fungsi untuk memeriksa ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Fungsi konversi grayscale
def convert_to_grayscale(image_path, output_path):
    img = Image.open(image_path)
    pixels = img.load()

    # Manipulasi pixel
    for i in range(img.width):
        for j in range(img.height):
            r, g, b = pixels[i, j][:3]  # Ambil RGB
            gray = (r + g + b) // 3  # Hitung rata-rata
            pixels[i, j] = (gray, gray, gray)  # Set pixel ke grayscale

    img.save(output_path)

def apply_blur(image_path, output_path):
    img = Image.open(image_path)
    pixels = img.load()
    new_image = img.copy()
    new_pixels = new_image.load()

    # Atur ukuran jendela blur
    window_size = 5  # Gunakan jendela 5x5 (bisa ditingkatkan ke 7x7, 9x9, dll.)
    offset = window_size // 2

    # Manipulasi pixel dengan rata-rata tetangga di jendela yang lebih besar
    for i in range(offset, img.width - offset):
        for j in range(offset, img.height - offset):
            r, g, b = 0, 0, 0
            count = 0

            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    pr, pg, pb = pixels[i + dx, j + dy][:3]
                    r += pr
                    g += pg
                    b += pb
                    count += 1

            # Hitung rata-rata dan terapkan ke piksel baru
            new_pixels[i, j] = (r // count, g // count, b // count)

    new_image.save(output_path)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Periksa apakah file diunggah
        if 'image' not in request.files:
            return render_template('index.html', error="No file selected.")

        file = request.files['image']
        option = request.form.get('operation')  # Ambil nilai 'operation'

        if file and allowed_file(file.filename):
            filename = file.filename
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            output_filename = f'output_{filename}'
            output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)

            file.save(input_path)

            # Pilih transformasi
            if option == 'grayscale':
                convert_to_grayscale(input_path, output_path)
            elif option == 'blur':
                apply_blur(input_path, output_path)
            else:
                return render_template('index.html', error="Invalid operation selected.")

            # Path untuk ditampilkan di HTML (aksesible dari browser)
            original_url = f"/{input_path}"
            transformed_url = f"/{output_path}"

            return render_template('result.html', original=original_url, transformed=transformed_url)

        return render_template('index.html', error="Invalid file format.")

    # GET request - render halaman upload
    return render_template('index.html')

if __name__ == '__main__':
    # Pastikan folder upload dan hasil ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    app.run(debug=True)
