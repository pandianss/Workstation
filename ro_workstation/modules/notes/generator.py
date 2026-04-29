from ..llm.client import LLMClient
from ..utils.paths import project_path

class NoteGenerator:
    def __init__(self):
        self.llm = LLMClient()
        
    def generate_note(self, template: str, subject: str, data_points: str, dept: str) -> str:
        prompt = f"Draft an office note based on template '{template}'. Subject: {subject}. Key points: {data_points}."
        system_prompt = f"You are a professional bank officer in the {dept} department. Output the note in standard PSB format (Ref No / Date / To / Subject / Background / Analysis / Recommendations / Approval sought)."
        
        return self.llm.generate(prompt, system_prompt)
        
    def generate_html_note(self, template_type: str, raw_data: str) -> str:
        """Generates an HTML office note based on a template and raw unstructured data"""
        if template_type == "Payment of Bills":
            import json
            
            # 1. Ask LLM to extract data as JSON
            schema = '''{
                "ref_no": "RO/DGL/PLNG/2026-27/05/04",
                "date": "DD.MM.YYYY",
                "subject": "PAYMENT OF BILLS",
                "vendor_name": "Name",
                "vendor_code": "CODE",
                "period": "Month Year",
                "line_items": [{"s_no": "1.", "date": "DD.MM.YYYY", "details": "Desc", "amount": 1000, "rate": "10/pc"}],
                "total": 1000,
                "budget_utilised": "Rs XXX/-",
                "recommendation_text": "Since the aforementioned..."
            }'''
            prompt = f"Extract details from this raw data into the specified JSON format:\n\n{raw_data}"
            system_prompt = f"You are an expert data extractor. Output ONLY valid JSON matching this schema: {schema}"
            
            json_response = self.llm.generate(prompt, system_prompt)
            
            # Try to parse the JSON
            try:
                if "[Ollama Offline Mode]" in json_response:
                    data = {
                        "ref_no": "RO/DGL/PLNG/2026-27/05/04",
                        "date": "29.04.2026",
                        "subject": "PAYMENT OF BILLS - DUMMY (OFFLINE MODE)",
                        "vendor_name": "Dream Designers",
                        "vendor_code": "VEN123",
                        "period": "April 2026",
                        "line_items": [
                            {"s_no": "1.", "date": "20.04.2026", "details": "Sign boards", "amount": 5000, "rate": "100/pc"}
                        ],
                        "total": 5000,
                        "budget_utilised": "Rs 38696/-",
                        "recommendation_text": "Since the aforementioned services were utilised by Regional Office for various events during the month of April 2026 from Dream Designers, we may make payment of Rs 5000/- to Dream Designers."
                    }
                else:
                    # Basic cleanup if the LLM wrapped it in markdown
                    if "```json" in json_response:
                        json_response = json_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in json_response:
                        json_response = json_response.split("```")[1].split("```")[0].strip()
                        
                    data = json.loads(json_response)
            except Exception as e:
                return f"<div style='color:red;'>Failed to parse AI output as JSON: {e}</div><pre>{json_response}</pre>"
            
            # 2. Load the HTML template
            template_path = project_path("modules", "notes", "templates", "payment_note.html")
            with template_path.open("r", encoding="utf-8") as f:
                html = f.read()
            
            # 3. Build line items HTML
            line_items_html = ""
            for item in data.get("line_items", []):
                line_items_html += f'''
                <tr>
                    <td style="padding: 10px; border: 1px solid #000; text-align: center;">{item.get('s_no', '')}</td>
                    <td style="padding: 10px; border: 1px solid #000; text-align: center;">{item.get('date', '')}</td>
                    <td style="padding: 10px; border: 1px solid #000;">{item.get('details', '')}</td>
                    <td style="padding: 10px; border: 1px solid #000; text-align: right;">{item.get('amount', '')}</td>
                    <td style="padding: 10px; border: 1px solid #000;">{item.get('rate', '')}</td>
                </tr>
                '''
                
            # 4. Replace placeholders
            replacements = {
                "{{ref_no}}": str(data.get("ref_no", "")),
                "{{date}}": str(data.get("date", "")),
                "{{subject}}": str(data.get("subject", "")),
                "{{vendor_name}}": str(data.get("vendor_name", "")),
                "{{vendor_code}}": str(data.get("vendor_code", "")),
                "{{period}}": str(data.get("period", "")),
                "{{total}}": str(data.get("total", "")),
                "{{budget_utilised}}": str(data.get("budget_utilised", "")),
                "{{recommendation_text}}": str(data.get("recommendation_text", "")),
                "{{line_items_html}}": line_items_html
            }
            
            for key, val in replacements.items():
                html = html.replace(key, val)
                
            return html
        
        return "<div>Template not found</div>"
