import easyocr
import json
import base64
import io
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

# Inicializa o leitor uma vez (evita recarregar a cada chamada)
# 'pt' = portugues, 'en' = ingles — etiquetas BR usam os dois
reader = easyocr.Reader(['pt', 'en'], gpu=False)

@app.route('/ocr', methods=['POST'])
def process_image():
    try:
        data = request.get_json()

        # Aceita imagem em base64 (enviada pelo n8n ou Bubble)
        if 'image_base64' in data:
            img_bytes = base64.b64decode(data['image_base64'])
            image = Image.open(io.BytesIO(img_bytes))
        else:
            return jsonify({'error': 'Envie a imagem em base64'}), 400

        # Executa OCR
        results = reader.readtext(image)

        # Formata resultado: lista de textos com confianca
        texts = []
        full_text = ''
        for (bbox, text, confidence) in results:
            texts.append({
                'text': text,
                'confidence': round(confidence, 3)
            })
            full_text += text + ' '

        return jsonify({
            'success': True,
            'full_text': full_text.strip(),
            'fields': texts
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
