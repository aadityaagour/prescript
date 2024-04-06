from flask import Flask, request, render_template
import os
import PyPDF2
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# List of keywords to match
keywords = ['apple', 'pear', 'guava']

def extract_text_from_pdf(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text()
    return text

def match_keywords(text):
    matched_keywords = [keyword for keyword in keywords if keyword in text]
    return matched_keywords

def save_to_database(filename, keywords):
    conn = sqlite3.connect('documents.db')
    c = conn.cursor()
    c.execute("INSERT INTO documents (filename, keywords) VALUES (?, ?)", (filename, ', '.join(keywords)))
    conn.commit()
    conn.close()

def compare_keywords(first_keywords, second_keywords):
    common_keywords = list(set(first_keywords) & set(second_keywords))
    return common_keywords

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    word = request.form['word']
    pdf = request.files['pdf']
    pdf_filename = os.path.join(UPLOAD_FOLDER, pdf.filename)
    pdf.save(pdf_filename)
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_filename)
    
    # Match keywords
    matched_keywords = match_keywords(pdf_text)
    
    # Save to database
    save_to_database(pdf.filename, matched_keywords)
    
    # Retrieve previous document from the database
    conn = sqlite3.connect('documents.db')
    c = conn.cursor()
    c.execute("SELECT keywords FROM documents ORDER BY id DESC LIMIT 1")
    previous_keywords = c.fetchone()
    conn.close()
    
    # Compare keywords
    if previous_keywords:
        previous_keywords = previous_keywords[0].split(', ')
        common_keywords = compare_keywords(matched_keywords, previous_keywords)
    else:
        common_keywords = []
    
    # Do something with the word, PDF file, matched keywords, and common keywords
    # For demonstration purposes, I'm just printing them here
    print('Word:', word)
    print('PDF saved as:', pdf_filename)
    print('Matched Keywords:', matched_keywords)
    print('Common Keywords with Previous Document:', common_keywords)
    
    return 'Word: {}, PDF saved as {}. Matched Keywords: {}. Common Keywords with Previous Document: {}'.format(word, pdf_filename, matched_keywords, common_keywords)

if __name__ == '__main__':
    app.run(debug=True)
