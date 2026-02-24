from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq
from fpdf import FPDF
from flask import Response
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_notice(data):
    prompt = f"""
You are a senior legal expert in Indian law with 20 years of experience drafting formal legal notices.
Generate a professional legal notice based on the following details:

Notice Type: {data['notice_type']}
Sender Name: {data['sender_name'].title()}
Sender Address: {data['sender_address'].title()}
Recipient Name: {data['recipient_name'].title()}
Recipient Address: {data['recipient_address'].title()}
Issue Description: {data['issue_description']}
Amount Involved (if any): {data['amount']}
Date of Incident: {data['incident_date']}

STRICT FORMATTING RULES:
- Start exactly like this, no square brackets:

{data['sender_name'].title()}
{data['sender_address'].title()}

Date: {data['incident_date']}

To,
{data['recipient_name'].title()}
{data['recipient_address'].title()}

Subject: Legal Notice for {data['notice_type']}

Dear {data['recipient_name'].title()},

- Then write 3 full paragraphs as the body of the notice
- Each paragraph must be 3-5 complete sentences, flowing naturally
- Do NOT break sentences into short lines
- Do NOT use square brackets anywhere
- Cite relevant Indian law (Indian Contract Act 1872, Consumer Protection Act, etc.)
- Include a clear demand with a 15-day deadline
- Include consequences if ignored
- End with a professional closing:

Yours sincerely,
{data['sender_name'].title()}

Note: This notice has been generated for informational purposes. Please consult a qualified advocate before sending.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def create_pdf(notice_text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.set_top_margin(20)
    pdf.set_auto_page_break(auto=True, margin=20)

    for line in notice_text.split('\n'):
        if line.strip() == '':
            pdf.ln(5)
        else:
            clean_line = line.strip().encode('latin-1', 'replace').decode('latin-1')
            pdf.write(8, clean_line)
            pdf.ln(8)

    filepath = f"static/{filename}.pdf"
    pdf.output(filepath)
    return filepath

@app.route('/')
def home():
    with open('templates/index.html', 'r') as f:
        content = f.read()
    return Response(content, mimetype='text/html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        notice_text = generate_notice(data)
        filename = str(uuid.uuid4())
        pdf_path = create_pdf(notice_text, filename)
        return jsonify({
            "success": True,
            "notice": notice_text,
            "pdf_url": f"/download/{filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/download/<filename>')
def download(filename):
    return send_file(f"static/{filename}.pdf", as_attachment=True, download_name="legal_notice.pdf")

if __name__ == '__main__':
    app.run(debug=True)

# Required for Vercel
application = app
```

---

**Fix 3 - Update `requirements.txt`** to pin exact versions:
```
flask==3.0.0
groq==0.4.2
fpdf2==2.7.6
flask-cors==4.0.0
python-dotenv==1.0.0