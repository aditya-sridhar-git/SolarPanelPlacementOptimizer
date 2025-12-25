"""
Flask Backend API for Solar Panel Placement Optimizer
Provides REST API for the React frontend to analyze rooftop images
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from analyze_rooftop import analyze_image

app = Flask(__name__)
CORS(app)  # Enable CORS for React dev server
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('output', exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze an uploaded rooftop image for solar panel placement"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Allowed: png, jpg, jpeg, webp, bmp'}), 400
    
    try:
        # Generate unique filename to avoid collisions
        unique_id = str(uuid.uuid4())[:8]
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{unique_id}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save uploaded file
        file.save(filepath)
        
        # Get optional configuration from request
        config = {}
        if request.form.get('latitude'):
            config['latitude'] = float(request.form.get('latitude'))
        if request.form.get('longitude'):
            config['longitude'] = float(request.form.get('longitude'))
        if request.form.get('pixel_to_meter'):
            config['pixel_to_meter'] = float(request.form.get('pixel_to_meter'))
        
        # Run the analysis
        result = analyze_image(filepath, config, output_dir='output')
        
        if result['success']:
            # Add URLs for the frontend to access results
            base_name = os.path.splitext(filename)[0]
            result['analysis_image_url'] = f'/output/{base_name}_analysis.png'
            result['uploaded_image_url'] = f'/uploads/{filename}'
            
            # Extract summary for easy frontend access
            analyses = result.get('analyses', [])
            if analyses:
                result['total_panels'] = sum(a['panel_count'] for a in analyses)
                result['total_capacity_kw'] = sum(a['energy']['system_capacity_kw'] for a in analyses)
                result['total_annual_kwh'] = sum(a['energy']['estimated_annual_kwh'] for a in analyses)
                result['total_co2_offset'] = sum(a['energy']['co2_offset_kg_year'] for a in analyses)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/output/<filename>')
def output_file(filename):
    """Serve analysis output images"""
    return send_from_directory('output', filename)


@app.route('/testcases/<filename>')
def testcase_file(filename):
    """Serve test case images for demo purposes"""
    return send_from_directory('testcases', filename)


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌞 SOLAR PANEL PLACEMENT OPTIMIZER - Web Interface")
    print("="*60)
    print("🌐 Open http://localhost:5000 in your browser")
    print("="*60 + "\n")
    app.run(debug=True, port=5000)
