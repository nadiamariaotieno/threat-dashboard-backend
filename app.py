from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
from textblob import TextBlob

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///terrorism_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Database Model
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(255))
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    sentiment = db.Column(db.String(50))
    threat_level = db.Column(db.String(50))

# Function to Analyze Threat Level
def analyze_threat(content):
    analysis = TextBlob(content)
    sentiment_score = analysis.sentiment.polarity  # Range: [-1,1]

    if sentiment_score < -0.5:
        return "High Threat"
    elif -0.5 <= sentiment_score < 0:
        return "Medium Threat"
    else:
        return "Low Threat"

# Web Scraper Function
def scrape_news(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title and text content
    title = soup.title.string if soup.title else "No Title"
    paragraphs = soup.find_all('p')
    content = ' '.join([p.get_text() for p in paragraphs])
    content = re.sub(r'\s+', ' ', content)

    # Analyze sentiment & threat level
    sentiment = analyze_threat(content)

    # Save to database
    new_report = Report(source=url, title=title, content=content, sentiment=sentiment, threat_level=sentiment)
    db.session.add(new_report)
    db.session.commit()

    return {"title": title, "sentiment": sentiment, "threat_level": sentiment}

# API Route to Scrape a News Article
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    result = scrape_news(url)
    return jsonify(result)

# API Route to Retrieve Reports
@app.route('/reports', methods=['GET'])
def get_reports():
    reports = Report.query.all()
    return jsonify([{ 
        "id": r.id, 
        "source": r.source, 
        "title": r.title, 
        "sentiment": r.sentiment, 
        "threat_level": r.threat_level 
    } for r in reports])

# Run the Flask App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database
    app.run(debug=True)
