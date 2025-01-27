from flask import Flask, request, render_template, send_from_directory
import os
import subprocess

app = Flask(__name__)

# Ruta para servir archivos generados (salida pública)
OUTPUT_FOLDER = "output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Página principal con el formulario
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No se proporcionó ningún archivo.", 400

    # Guardar el archivo subido
    file = request.files['file']
    input_file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    file.save(input_file_path)

    # Ruta de salida para el archivo .srt
    output_file_name = os.path.splitext(file.filename)[0] + ".srt"
    output_file_path = os.path.join(OUTPUT_FOLDER, output_file_name)

    try:
        # Ejecutar Whisper utilizando subprocess.run
        subprocess.run(
            [
                "python", "-m", "whisper", input_file_path,
                "--model", "medium",
                "--language", "en",
                "--output_format", "srt",
                "--output_dir", OUTPUT_FOLDER,
                "--max_line_width", "30",
                "--max_words_per_line", "7",
                "--max_line_count", "1",
                "--no_speech_threshold", "0.5",
                "--logprob_threshold", "-1.0",
                "--word_timestamps", "True"
            ],
            check=True
        )

        # Enlace para descargar el archivo generado
        return f"""
            <h1>Subtítulo generado correctamente</h1>
            <a href="/download/{output_file_name}" download>Descargar subtítulo</a>
        """
    except subprocess.CalledProcessError as e:
        return f"Hubo un error al procesar el archivo:\n{e}", 500
    finally:
        # Limpieza opcional del archivo subido para ahorrar espacio
        if os.path.exists(input_file_path):
            os.remove(input_file_path)

@app.route('/download/<filename>')
def download_file(filename):
    # Servir el archivo desde la carpeta pública de salida
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
