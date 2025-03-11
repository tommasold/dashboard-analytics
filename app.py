from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Evita problemi di GUI su macOS
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "Nessun file caricato"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nessun file selezionato"}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    preview = df.head().to_dict(orient="records")
    return jsonify({"filename": file.filename, "preview": preview})

@app.route("/histogram/<filename>/<column>", methods=["GET"])
def generate_histogram(filename, column):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File non trovato"}), 404

    df = pd.read_csv(filepath)

    if column not in df.columns:
        return jsonify({"error": f"Colonna '{column}' non trovata"}), 400

    plt.figure(figsize=(6, 4))
    df[column].hist(bins=20, alpha=0.7, color="blue")
    plt.xlabel(column)
    plt.ylabel("Frequenza")
    plt.title(f"Istogramma di {column}")

    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    plt.close()

    return jsonify({"image": f"data:image/png;base64,{img_base64}"})

@app.route("/stats/<filename>/<column>", methods=["GET"])
def get_statistics(filename, column):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File non trovato"}), 404

    df = pd.read_csv(filepath)

    if column not in df.columns:
        return jsonify({"error": f"Colonna '{column}' non trovata"}), 400

    # Controlliamo che la colonna sia numerica
    if not pd.api.types.is_numeric_dtype(df[column]):
        return jsonify({"error": f"La colonna '{column}' non è numerica"}), 400

    # Calcolo delle statistiche
    stats = {
        "media": df[column].mean(),
        "mediana": df[column].median(),
        "deviazione_standard": df[column].std(),
        "minimo": df[column].min(),
        "massimo": df[column].max(),
        "conteggio": df[column].count(),
        "quartile_1": df[column].quantile(0.25),
        "quartile_3": df[column].quantile(0.75)
    }

    return jsonify(stats)

if __name__ == "__main__":
    app.run(debug=True)
