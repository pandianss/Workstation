from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Nirmala UI for Trilingual (Tamil/Hindi) support
try:
    font_path = "C:/Windows/Fonts/Nirmala.ttc"
    pdfmetrics.registerFont(TTFont('Nirmala', font_path))
    UNICODE_FONT = 'Nirmala'
except:
    UNICODE_FONT = 'Helvetica'

# Regional Office Theme Management
RO_BLUE = HexColor('#21357F')
RO_LIGHT_BLUE = HexColor('#d9e2f3')
UNICODE_FONT = 'Nirmala'

THEME = {
    "colors": {
        "primary": RO_BLUE,
        "secondary": RO_LIGHT_BLUE,
        "text": HexColor('#000000'),
        "muted": HexColor('#4b5563'),
        "header_bg": RO_BLUE,
        "header_text": HexColor('#ffffff'),
    },
    "fonts": {
        "standard": UNICODE_FONT,
        "bold": f"{UNICODE_FONT}-Bold",
        "header_size": 11,
        "body_size": 10,
        "meta_size": 8,
        "signature_size": 6.5,
    },
    "layout": {
        "page_width": 8.5,
        "page_height": 11,
        "margins": 0.5,
        "header_height": 1.5,
        "footer_height": 0.75,
    }
}

RO_IDENTITY = {
    "office_name_ta": "மண்டல அலுவலகம், திண்டுக்கல்",
    "office_name_hi": "क्षेत्रीय कार्यालय, डिंडीगुल",
    "office_name_en": "Regional Office, Dindigul",
    "address_ta": "17 - I, முதல் தளம், பென்ஷனர் தெரு பழனி சாலை, திண்டுக்கல் - 624001",
    "address_hi": "17 - I, पहली मंजिल, पेंशनर स्ट्रीट, पलानी रोड, डिंडीगुल - 624001",
    "address_en": "17 - I, First Floor, Pensioner Street Palani Road, Dindigul - 624001",
    "contact_line": "Phone: 89259 53933 | Email: 3933ro@iob.bank.in",
}

DEFAULT_NOTE_CONTEXT = {
    **RO_IDENTITY,
    "department_ta": "திட்டமிடல் துறை",
    "department_hi": "योजना विभाग",
    "department_en": "Planning Department",
    "note_label_ta": "அலுவலக குறிப்பு",
    "note_label_hi": "कार्यालय नोट",
    "note_label_en": "Office Note",
    "salutation": "CM / SRM Sirs,",
    "signature_blocks": [
        {
            "name_ta": "சதீஷ் பாண்டியன் எஸ்",
            "name_hi": "सतीश पांडियन एस",
            "name_en": "Satish Pandian S",
            "designation_ta": "மேலாளர்",
            "designation_hi": "प्रबंधक",
            "designation_en": "Manager",
        },
        {
            "name_ta": "அண்ணாமலை எஸ்.எம்",
            "name_hi": "அண்ணாமலை எஸ்.எம்.",
            "name_en": "Annamalai SM",
            "designation_ta": "தலைமை மேலாளர்",
            "designation_hi": "मुख्य प्रबंधक",
            "designation_en": "Chief Manager",
        },
        {
            "name_ta": "சந்திர குமார் பி",
            "name_hi": "चंद्र कुमार पी",
            "name_en": "Chandra Kumar P",
            "designation_ta": "எஸ்.ஆர்.எம்",
            "designation_hi": "एस.ஆர்.எம்",
            "designation_en": "S.R.M",
        },
    ],
}
