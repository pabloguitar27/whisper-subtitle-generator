from flask import Flask, request, render_template, send_file, make_response
import os
import subprocess
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    # Página principal con el formulario
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo.", 400

    # Guardar el archivo subido temporalmente
    file = request.files['file']
    input_file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    file.save(input_file_path)

    # Nombre del archivo de salida .srt
    output_file_name = os.path.splitext(file.filename)[0] + ".srt"
    output_file_path = f"temp/{output_file_name}"

    try:
        # Ejecutar Whisper para generar subtítulos
        subprocess.run(
            [
                "python", "-m", "whisper", input_file_path,
                "--model", "medium",
                "--language", "en",
                "--output_format", "srt",
                "--output_dir", "temp",
                "--max_line_width", "30",
                "--max_words_per_line", "7",
                "--max_line_count", "1",
                "--no_speech_threshold", "0.5",
                "--logprob_threshold", "-1.0",
                "--word_timestamps", "True"
            ],
            check=True
        )

        # Leer el archivo generado y devolverlo como respuesta
        with open(output_file_path, "rb") as f:
            srt_data = f.read()

        # Crear una respuesta para descargar el archivo directamente
        response = make_response(srt_data)
        response.headers['Content-Disposition'] = f'attachment; filename={output_file_name}'
        response.headers['Content-Type'] = 'text/plain'

        return response

    except subprocess.CalledProcessError as e:
        return f"Hubo un error al procesar el archivo:\n{e}", 500
    finally:
        # Limpieza de archivos temporales
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
