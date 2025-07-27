import os
import time
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file.filename != '':
        try:
            file.seek(0)
            try:
                df = pd.read_csv(file, encoding='utf-8', engine='python', on_bad_lines='skip')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='ISO-8859-1', engine='python', on_bad_lines='skip')

            required_cols = ['math score', 'reading score', 'writing score']
            if not all(col in df.columns for col in required_cols):
                return f"<h3>CSV missing required columns: {required_cols}</h3><a href='/'>Go Back</a>"

            # Ensure 'static' directory exists
            project_root = os.path.dirname(os.path.abspath(__file__))
            static_folder = os.path.join(project_root, 'static')
            if not os.path.exists(static_folder):
                os.makedirs(static_folder)

            timestamp = int(time.time())
            plot_filename = f'plot_{timestamp}.png'
            plot_path = os.path.join(static_folder, plot_filename)

            plt.figure(figsize=(8, 6))
            sns.boxplot(data=df[required_cols])
            plt.title("Student Performance - Boxplot")
            plt.ylabel("Scores")
            plt.savefig(plot_path)
            plt.close()

            plot_url = url_for('static', filename=plot_filename)
            return render_template('dashboard.html', plot_url=plot_url)

        except Exception as e:
            return f"<h3>Error reading CSV: {e}</h3><a href='/'>Go Back</a>"

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
