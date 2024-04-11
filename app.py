from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

app = Flask(__name__)

# Function to load CSV file
def load_csv(file):
    data = pd.read_csv(file)
    return data, file.filename

# Function to generate graphs with highlighted values based on threshold
def generate_graphs(data, thresholds):
    graphs = []
    for column in data.columns:
        if data[column].dtype == 'int64' or data[column].dtype == 'float64':
            plt.figure(figsize=(8, 6))
            sns.histplot(data[column], kde=True)
            plt.title(f'Distribution of {column}')
            
            # Highlight values outside the threshold range
            if column in thresholds:
                min_val, max_val = thresholds[column]
                plt.axvspan(-float('inf'), min_val, color='red', alpha=0.5, lw=2)  # Highlight left side in red
                plt.axvspan(max_val, float('inf'), color='red', alpha=0.5, lw=2)   # Highlight right side in red
            
            # Add specific constraints based on column names
            if column == 'hours of sleep':
                plt.axvspan(-float('inf'), 8, color='red', alpha=0.5, lw=2)  # Highlight values below 8 in red
            elif column == 'blood pressure':
                plt.axvspan(-float('inf'), 90, color='red', alpha=0.5, lw=2)  # Highlight values below 90 in red
            elif column == 'calories':
                plt.axvspan(-float('inf'), 2000, color='red', alpha=0.5, lw=2)  # Highlight values below 2000 in red
            elif column == 'Bmi':
                plt.axvspan(-float('inf'), 20, color='red', alpha=0.5, lw=2)  # Highlight values below 20 in red
            
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph_url = base64.b64encode(img.getvalue()).decode()
            graphs.append((column, graph_url, data[column].dtype))
            plt.close()

    return graphs

# Route to summarize graphs
@app.route("/summarize-graphs", methods=["POST"])
def summarize_graphs():
    data = pd.read_csv(request.files['file'])
    summaries = []  # Initialize summaries list
    # Summarize each graph and append to the summaries list
    for column in data.columns:
        if data[column].dtype == 'int64' or data[column].dtype == 'float64':
            summary = summarize_graph(data[column])
            summaries.append(summary)
    return jsonify(summaries)  # Return summaries as JSON

# Function to summarize graph data
def summarize_graph(data):
    summary = f"Mean: {data.mean()}, Median: {data.median()}, Min: {data.min()}, Max: {data.max()}"
    return summary

# Home route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            data, filename = load_csv(file)
            thresholds = {column: (data[column].min(), data[column].max()) for column in data.columns if data[column].dtype == 'int64' or data[column].dtype == 'float64'}
            graphs = generate_graphs(data, thresholds)
            return render_template("index.html", graphs=graphs, filename=filename)
    return render_template("index.html", graphs=None)

if __name__ == "__main__":
    app.run(debug=True)
