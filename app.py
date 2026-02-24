from flask import Flask, request, jsonify, send_file, Response
from groq import Groq
from fpdf import FPDF
from dotenv import load_dotenv
import os
import io

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

def create_pdf_bytes(notice_text):
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

    return pdf.output()

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
        pdf_bytes = create_pdf_bytes(notice_text)
        pdf_b64 = __import__('base64').b64encode(pdf_bytes).decode('utf-8')
        return jsonify({
            "success": True,
            "notice": notice_text,
            "pdf_b64": pdf_b64
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)

application = app