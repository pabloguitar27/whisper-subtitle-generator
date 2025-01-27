from flask import Flask, request, render_template, send_file
import os
import subprocess

app = Flask(__name__)

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
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_file_name = os.path.splitext(file.filename)[0] + ".srt"
    output_file_path = os.path.join(output_dir, output_file_name)

    try:
        # Ejecutar Whisper utilizando subprocess.run
        subprocess.run(
            [
                "python", "-m", "whisper", input_file_path,
                "--model", "medium",  # Cambia a otro modelo si es necesario
                "--language", "en",  # Ajusta el idioma si es necesario
                "--output_format", "srt",
                "--output_dir", output_dir,
                "--max_line_width", "30",
                "--max_words_per_line", "7",
                "--max_line_count", "1",
                "--no_speech_threshold", "0.5",
                "--logprob_threshold", "-1.0",
                "--word_timestamps", "True"  # Necesario para limitar las líneas
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
    # Ruta completa del archivo generado
    file_path = os.path.join("output", filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Archivo no encontrado.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
