from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html', template_folder='frontend', static_folder='frontend')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected for uploading'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Uploaded file must be a CSV'}), 400
        
        df = pd.read_csv(file)
        
        expected_columns = ['date', 'value']
        if not all(col in df.columns for col in expected_columns):
            return jsonify({'error': f"CSV file must contain columns: {', '.join(expected_columns)}"}), 400
        
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        df = df.sort_values(by='date').reset_index(drop=True)
        
        model = SARIMAX(df['value'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        results = model.fit()
        
        train_results = {
            'AIC': results.aic,
            'BIC': results.bic,
            'HQIC': results.hqic
        }
        
        start_date = df['date'].iloc[-1] + timedelta(days=1)
        end_date = start_date + timedelta(days=6)
        
        forecast_index = pd.date_range(start=start_date, end=end_date, freq='D')
        forecast = results.get_forecast(steps=7)
        
        forecast_data = {
            'date': forecast_index.strftime('%Y-%m-%d').tolist(),
            'forecast': forecast.predicted_mean.values.tolist()
        }
        
        return jsonify({
            'train_results': train_results,
            'forecast': forecast_data
        }), 200
    
    except KeyError as e:
        return jsonify({'error': f"KeyError: {str(e)}"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
