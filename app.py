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


# route per i vari diagrammi 

@app.route("/plot/<filename>/<column>/<chart_type>", methods=["GET"])
def generate_plot(filename, column, chart_type):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File non trovato"}), 404

    df = pd.read_csv(filepath)

    if column not in df.columns:
        return jsonify({"error": f"Colonna '{column}' non trovata"}), 400

    if not pd.api.types.is_numeric_dtype(df[column]):
        return jsonify({"error": f"La colonna '{column}' non è numerica"}), 400

    plt.figure(figsize=(6, 4))

    if chart_type == "histogram":
        df[column].hist(bins=20, alpha=0.7, color="blue")
        plt.xlabel(column)
        plt.ylabel("Frequenza")
        plt.title(f"Istogramma di {column}")

    elif chart_type == "boxplot":
        df.boxplot(column=[column])
        plt.title(f"Boxplot di {column}")

    elif chart_type == "scatter":
        # Selezioniamo un'altra colonna numerica casuale per fare il grafico scatter
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        numeric_cols.remove(column)
        if not numeric_cols:
            return jsonify({"error": "Nessun'altra colonna numerica disponibile per scatter plot"}), 400
        df.plot.scatter(x=column, y=numeric_cols[0], alpha=0.5, color="red")
        plt.xlabel(column)
        plt.ylabel(numeric_cols[0])
        plt.title(f"Scatter Plot: {column} vs {numeric_cols[0]}")

    elif chart_type == "line":
        df[column].plot(kind="line", marker="o", linestyle="-", color="green")
        plt.xlabel("Indice")
        plt.ylabel(column)
        plt.title(f"Line Chart di {column}")

    else:
        return jsonify({"error": "Tipo di grafico non supportato"}), 400

    # Salvare il grafico come immagine Base64
    img = BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")
    plt.close()

    return jsonify({"image": f"data:image/png;base64,{img_base64}"})

@app.route("/stats/<filename>/<column>", methods=["POST"])
def get_statistics(filename, column):
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "File non trovato"}), 404

    df = pd.read_csv(filepath)

    if column not in df.columns:
        return jsonify({"error": f"Colonna '{column}' non trovata"}), 400

    if not pd.api.types.is_numeric_dtype(df[column]):
        return jsonify({"error": f"La colonna '{column}' contiene testo, seleziona una colonna numerica"}), 400

    selected_stats = request.json.get("statistics", [])

    stats_map = {
        "media": float(df[column].mean()),  # Converti in float
        "mediana": float(df[column].median()),
        "moda": float(df[column].mode()[0]) if not df[column].mode().empty else None,
        "deviazione_standard": float(df[column].std()),
        "varianza": float(df[column].var()),
        "minimo": float(df[column].min()),
        "massimo": float(df[column].max()),
        "quartile_1": float(df[column].quantile(0.25)),
        "quartile_3": float(df[column].quantile(0.75)),
        "conteggio": int(df[column].count()),  # Converti in int
    }

    selected_stats_result = {stat: stats_map[stat] for stat in selected_stats if stat in stats_map}

    return jsonify(selected_stats_result)


if __name__ == "__main__":
    app.run(debug=True)
