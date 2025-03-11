from flask import Flask, render_template, request, jsonify
import os
import pandas as pd


app = Flask(__name__)


@app.route("/")

def index():
    
    return render_template("index.html")


#cartella dove salvare i file caricati

upload_folder="uploads"
os.makedirs(upload_folder,exist_ok=True)

app.config["UPLOAD_FOLDER"]=upload_folder

@app.route('/upload', methods=['POST'])

def upload_file():
    if "file" not in request.files:
        return jsonify({"error":"Nessun file caricato"}),400
    
    file=request.files["file"]
    
    if file.filename=="":
    
        return jsonify({"error":"Nessun file selezionato"}),400


    filepath=os.path.join(app.config["UPLOAD_FOLDER"],file.filename)
    file.save(filepath)
    
    
    #leggere il dataset
    
    df=pd.read_csv(filepath)
    
    #restituire anteprima primi 5 record
    
    preview=df.head().to_dict(orient="records")
    return jsonify({"filename": file.filename,"preview":preview})


if __name__ == "__main__":
    app.run(debug=True)
    
    
    
    