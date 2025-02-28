from flask import Flask, request, render_template, make_response
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

    # Guardar el archivo subido temporalmente
    file = request.files['file']
    input_file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    file.save(input_file_path)

    # Nombre del archivo de salida .srt
    output_file_name = os.path.splitext(file.filename)[0] + ".srt"
    output_file_path = f"temp/{output_file_name}"

    try:
        print(f"Ejecutando Whisper en {input_file_path}...")  # Debug

        # Ejecutar Whisper y capturar errores
        result = subprocess.run(
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
            check=True,
            capture_output=True,
            text=True
        )

        print("Whisper output:", result.stdout)  # Debug
        print("Whisper errors:", result.stderr)  # Debug

        # Verificar si el archivo se generó
        if not os.path.exists(output_file_path):
            print(f"Error: Whisper no generó el archivo {output_file_path}")
            return "Error: No se generó el archivo de subtítulos.", 500

        # Leer el contenido del archivo .srt generado
        with open(output_file_path, "r", encoding="utf-8") as f:
            subtitulos = f.read()

        print("Subtítulos generados con éxito.")  # Debug

        # Mostrar los subtítulos en la página HTML
        return render_template('result.html', subtitulos=subtitulos, file_name=output_file_name)

    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando Whisper: {e.stderr}")  # Debug
        return f"Hubo un error al procesar el archivo:\n{e.stderr}", 500
    finally:
        # Limpieza opcional de archivos temporales
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
        if os.path.exists(output_file_path):
            os.remove(output_file_path)

@app.route('/download', methods=['POST'])
def download_file():
    # Obtener subtítulos desde la solicitud
    subtitulos = request.form['subtitulos']
    file_name = request.form['file_name']

    # Crear respuesta para descargar el archivo
    response = make_response(subtitulos)
    response.headers['Content-Disposition'] = f'attachment; filename={file_name}'
    response.headers['Content-Type'] = 'text/plain'

    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
