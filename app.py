from flask import Flask, render_template, request, jsonify
from utils.url_features import analyze_url

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url:
            return render_template('detection.html', error="Please enter a URL")
        
        try:
            analysis_result = analyze_url(url)
            return render_template('result.html', 
                                url=url,
                                result=analysis_result['prediction'],
                                risk_score=analysis_result['risk_score'],
                                risk_factors=analysis_result['risk_factors'],
                                features=analysis_result['features'])
        except Exception as e:
            return render_template('detection.html', error=str(e))
    
    return render_template('detection.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
