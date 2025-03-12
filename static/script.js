document.getElementById("uploadBtn").addEventListener("click", function() {
        let fileInput = document.getElementById("fileInput").files[0];
        if (!fileInput) {
            alert("Seleziona un file CSV!");
            return;
        }

        let formData = new FormData();
        formData.append("file", fileInput);

        fetch("/upload", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Errore: " + data.error);
                return;
            }

            let filename = data.filename;
            let preview = data.preview;
            let columns = Object.keys(preview[0]);

            // Mostra anteprima dati
            document.getElementById("previewSection").style.display = "block";
            document.getElementById("tableHead").innerHTML = "<tr>" + columns.map(col => `<th>${col}</th>`).join("") + "</tr>";
            document.getElementById("tableBody").innerHTML = preview.map(row => "<tr>" + columns.map(col => `<td>${row[col]}</td>`).join("") + "</tr>").join("");

            // Mostra selezione colonna e statistiche
            document.getElementById("columnSelection").style.display = "block";
            document.getElementById("statsSelection").style.display = "block";

            let columnDropdown = document.getElementById("columnDropdown");
            columnDropdown.innerHTML = "";
            columns.forEach(col => {
                columnDropdown.innerHTML += `<option value="${col}">${col}</option>`;
            });

            // Calcola statistiche
            document.getElementById("generateStatsBtn").onclick = function() {
                let selectedColumn = columnDropdown.value;
                let selectedStats = Array.from(document.querySelectorAll("#statsCheckboxes input:checked"))
                                        .map(checkbox => checkbox.value);

                if (selectedStats.length === 0) {
                    alert("Seleziona almeno una statistica!");
                    return;
                }

                fetch(`/stats/${filename}/${selectedColumn}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ statistics: selectedStats })
                })
                .then(response => response.json())
                .then(data => {
                    let statsHtml = "<ul>";
                    for (let key in data) {
                        statsHtml += `<li><b>${key.replace("_", " ")}:</b> ${data[key]}</li>`;
                    }
                    statsHtml += "</ul>";

                    document.getElementById("statsResults").innerHTML = statsHtml;
                });
            };
        })
        .catch(error => console.error("Errore:", error));
    });
    document.getElementById("uploadBtn").addEventListener("click", function() {
        let fileInput = document.getElementById("fileInput").files[0];
        if (!fileInput) {
            alert("Seleziona un file CSV!");
            return;
        }

        let formData = new FormData();
        formData.append("file", fileInput);

        fetch("/upload", { method: "POST", body: formData })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Errore: " + data.error);
                return;
            }

            let filename = data.filename;
            let preview = data.preview;
            let columns = Object.keys(preview[0]);

            // Mostra anteprima dati
            document.getElementById("previewSection").style.display = "block";
            document.getElementById("tableHead").innerHTML = "<tr>" + columns.map(col => `<th>${col}</th>`).join("") + "</tr>";
            document.getElementById("tableBody").innerHTML = preview.map(row => "<tr>" + columns.map(col => `<td>${row[col]}</td>`).join("") + "</tr>").join("");

            // Mostra selezione colonna e tipo di grafico
            document.getElementById("columnSelection").style.display = "block";
            let columnDropdown = document.getElementById("columnDropdown");
            columnDropdown.innerHTML = "";
            columns.forEach(col => {
                columnDropdown.innerHTML += `<option value="${col}">${col}</option>`;
            });

            // Genera grafico al click
            document.getElementById("generateChartBtn").onclick = function() {
                let selectedColumn = columnDropdown.value;
                let chartType = document.getElementById("chartTypeDropdown").value;

                fetch(`/plot/${filename}/${selectedColumn}/${chartType}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert("Errore: " + data.error);
                        return;
                    }
                    document.getElementById("chart").src = data.image;
                    document.getElementById("chartSection").style.display = "block";
                });
            };
        })
        .catch(error => console.error("Errore:", error));
    });
    
