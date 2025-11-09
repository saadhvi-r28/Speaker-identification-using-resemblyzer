"""
Flask API Backend for Voice Security System - Resemblyzer Edition
Uses the resemblyzer_starter module for real speaker embeddings
"""

import os
import sys
from pathlib import Path
import tempfile
import logging
from typing import Dict, Any
import base64

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import soundfile as sf

# Add paths
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

# Import Resemblyzer starter modules
from resemblyzer_starter.src.encoder import VoiceEncoderWrapper
from resemblyzer_starter.src.gallery import build_gallery_from_dir, save_gallery_npz, load_gallery_npz
from resemblyzer_starter.src.verify import verify_speaker as verify_speaker_helper, identify_speaker as identify_speaker_helper, cosine_sim

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Resemblyzer encoder (lazy load)
encoder = None
GALLERY_PATH = current_dir / 'data' / 'speaker_gallery.npz'
AUDIO_STORAGE = current_dir / 'data' / 'audio_samples'

def get_encoder():
    """Lazy load the encoder"""
    global encoder
    if encoder is None:
        logger.info("Loading Resemblyzer encoder...")
        encoder = VoiceEncoderWrapper()
        logger.info("Encoder loaded successfully")
    return encoder

def ensure_storage():
    """Ensure storage directories exist"""
    AUDIO_STORAGE.mkdir(parents=True, exist_ok=True)
    GALLERY_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_gallery():
    """Load current gallery or return empty"""
    if GALLERY_PATH.exists():
        ids, embs = load_gallery_npz(GALLERY_PATH)
        return dict(zip(ids, embs))
    return {}

def save_gallery(gallery: Dict[str, np.ndarray]):
    """Save gallery to NPZ"""
    ensure_storage()
    from resemblyzer_starter.src.gallery import save_gallery_npz as save_npz
    save_npz(gallery, GALLERY_PATH)

@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler"""
    logger.error(f"API Error: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': str(error),
        'message': 'An error occurred processing your request'
    }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Voice Security System API (Resemblyzer) is running',
        'version': '2.0.0-resemblyzer'
    })

@app.route('/api/stats', methods=['GET'])
def get_system_stats():
    """Get system statistics"""
    try:
        gallery = load_gallery()
        return jsonify({
            'success': True,
            'data': {
                'total_speakers': len(gallery),
                'gallery_path': str(GALLERY_PATH),
                'encoder_loaded': encoder is not None
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speakers', methods=['GET'])
def list_speakers():
    """Get list of registered speakers"""
    try:
        gallery = load_gallery()
        speaker_list = [{'id': sid, 'name': sid} for sid in gallery.keys()]
        
        return jsonify({
            'success': True,
            'data': speaker_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speakers/<speaker_id>', methods=['GET'])
def get_speaker(speaker_id):
    """Get specific speaker details"""
    try:
        gallery = load_gallery()
        if speaker_id not in gallery:
            return jsonify({
                'success': False,
                'error': 'Speaker not found'
            }), 404
        
        embedding = gallery[speaker_id]
        speaker_dir = AUDIO_STORAGE / speaker_id
        audio_files = []
        if speaker_dir.exists():
            audio_files = [f.name for f in speaker_dir.glob('*.wav')]
        
        speaker_data = {
            'id': speaker_id,
            'name': speaker_id,
            'embedding_dim': len(embedding),
            'audio_files': audio_files,
            'num_embeddings': 1
        }
        
        return jsonify({
            'success': True,
            'data': speaker_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speakers', methods=['POST'])
def register_speaker():
    """Register a new speaker using Resemblyzer"""
    try:
        data = request.get_json()
        speaker_id = data.get('speaker_id')
        name = data.get('name', speaker_id)
        
        if not speaker_id:
            return jsonify({
                'success': False,
                'error': 'Speaker ID is required'
            }), 400
        
        # Handle file uploads (base64 encoded audio)
        audio_files = []
        temp_files = []
        
        if 'audio_files' in data:
            for i, audio_data in enumerate(data['audio_files']):
                # Decode base64 audio
                audio_bytes = base64.b64decode(audio_data['data'])
                
                # Save to temporary file
                temp_file = Path(tempfile.mktemp(suffix='.wav'))
                temp_file.write_bytes(audio_bytes)
                audio_files.append(temp_file)
                temp_files.append(temp_file)
        
        if not audio_files:
            return jsonify({
                'success': False,
                'error': 'At least one audio file is required'
            }), 400
        
        # Get encoder and compute embeddings
        enc = get_encoder()
        embeddings = []
        
        ensure_storage()
        speaker_storage = AUDIO_STORAGE / speaker_id
        speaker_storage.mkdir(exist_ok=True)
        
        for i, audio_file in enumerate(audio_files):
            try:
                # Get embedding
                emb = enc.get_embedding(audio_file)
                embeddings.append(emb)
                
                # Save audio to persistent storage
                persistent_path = speaker_storage / f'{speaker_id}_{i+1}.wav'
                import shutil
                shutil.copy(audio_file, persistent_path)
                logger.info(f"Saved audio to {persistent_path}")
                
            except Exception as e:
                logger.error(f"Error processing audio {i}: {e}")
                continue
        
        # Clean up temp files
        for temp_file in temp_files:
            if temp_file.exists():
                temp_file.unlink()
        
        if not embeddings:
            return jsonify({
                'success': False,
                'error': 'Failed to generate embeddings from audio files'
            }), 500
        
        # Average embeddings for robust profile
        avg_embedding = np.mean(np.stack(embeddings, axis=0), axis=0).astype(np.float32)
        
        # Load existing gallery and add new speaker
        gallery = load_gallery()
        gallery[speaker_id] = avg_embedding
        save_gallery(gallery)
        
        logger.info(f"Registered speaker {speaker_id} with {len(embeddings)} samples")
        
        return jsonify({
            'success': True,
            'message': f'Speaker {name} registered successfully',
            'num_samples': len(embeddings)
        })
            
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/speakers/<speaker_id>', methods=['DELETE'])
def remove_speaker(speaker_id):
    """Remove a speaker"""
    try:
        gallery = load_gallery()
        
        if speaker_id not in gallery:
            return jsonify({
                'success': False,
                'error': 'Speaker not found'
            }), 404
        
        # Remove from gallery
        del gallery[speaker_id]
        save_gallery(gallery)
        
        # Remove audio files
        speaker_dir = AUDIO_STORAGE / speaker_id
        if speaker_dir.exists():
            import shutil
            shutil.rmtree(speaker_dir)
        
        return jsonify({
            'success': True,
            'message': f'Speaker {speaker_id} removed successfully'
        })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/verify', methods=['POST'])
def verify_speaker():
    """Verify speaker identity using Resemblyzer"""
    try:
        data = request.get_json()
        expected_speaker = data.get('expected_speaker')
        threshold = data.get('threshold', 0.75)
        
        if not expected_speaker:
            return jsonify({
                'success': False,
                'error': 'Expected speaker ID is required'
            }), 400
        
        # Handle audio data
        if 'audio_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Audio data is required'
            }), 400
        
        # Decode and save audio to temp file
        audio_bytes = base64.b64decode(data['audio_data'])
        temp_file = Path(tempfile.mktemp(suffix='.wav'))
        temp_file.write_bytes(audio_bytes)
        
        try:
            # Load gallery
            gallery = load_gallery()
            if expected_speaker not in gallery:
                return jsonify({
                    'success': False,
                    'error': f'Speaker {expected_speaker} not found in gallery'
                }), 404
            
            # Get test embedding
            enc = get_encoder()
            test_emb = enc.get_embedding(temp_file)
            
            # Compare with expected speaker
            profile_emb = gallery[expected_speaker]
            similarity = cosine_sim(test_emb, profile_emb)
            
            access_granted = similarity >= threshold
            
            return jsonify({
                'success': True,
                'data': {
                    'access_granted': access_granted,
                    'confidence': float(similarity),
                    'speaker_name': expected_speaker,
                    'threshold': threshold
                }
            })
            
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        logger.error(f"Verification error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/identify', methods=['POST'])
def identify_speaker():
    """Identify speaker from audio using Resemblyzer"""
    try:
        data = request.get_json()
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.7)
        
        # Handle audio data
        if 'audio_data' not in data:
            return jsonify({
                'success': False,
                'error': 'Audio data is required'
            }), 400
        
        # Decode and save audio to temp file
        audio_bytes = base64.b64decode(data['audio_data'])
        temp_file = Path(tempfile.mktemp(suffix='.wav'))
        temp_file.write_bytes(audio_bytes)
        
        try:
            # Load gallery
            gallery = load_gallery()
            if not gallery:
                return jsonify({
                    'success': False,
                    'error': 'No speakers in gallery'
                }), 400
            
            # Get test embedding
            enc = get_encoder()
            test_emb = enc.get_embedding(temp_file)
            
            # Compute similarities
            scores = []
            for speaker_id, profile_emb in gallery.items():
                sim = cosine_sim(test_emb, profile_emb)
                scores.append((speaker_id, float(sim)))
            
            # Sort by similarity
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get top matches
            top_matches = []
            for speaker_id, sim in scores[:top_k]:
                top_matches.append({
                    'speaker_id': speaker_id,
                    'name': speaker_id,
                    'confidence': sim
                })
            
            # Best match
            best_match = None
            if scores and scores[0][1] >= threshold:
                best_match = {
                    'speaker_id': scores[0][0],
                    'name': scores[0][0],
                    'confidence': scores[0][1]
                }
            
            return jsonify({
                'success': True,
                'data': {
                    'best_match': best_match,
                    'top_matches': top_matches,
                    'all_scores': {sid: score for sid, score in scores}
                }
            })
            
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        logger.error(f"Identification error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings"""
    try:
        settings = {
            'verification_threshold': 0.75,
            'identification_threshold': 0.70,
            'supported_formats': ['wav', 'mp3', 'flac', 'm4a'],
            'max_file_size': 50 * 1024 * 1024,  # 50MB
            'min_duration': 1,  # seconds
            'max_duration': 30,  # seconds
            'embedding_dim': 256,
            'encoder': 'Resemblyzer'
        }
        
        return jsonify({
            'success': True,
            'data': settings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_audio():
    """Handle audio file upload"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Save uploaded file
        temp_file = Path(tempfile.mktemp(suffix='.wav'))
        file.save(temp_file)
        
        try:
            # Read audio file
            audio_data, sr = sf.read(temp_file)
            
            # Convert to base64 for frontend
            audio_b64 = base64.b64encode(temp_file.read_bytes()).decode('utf-8')
            
            return jsonify({
                'success': True,
                'data': {
                    'audio_data': audio_b64,
                    'duration': len(audio_data) / sr,
                    'sample_rate': sr,
                    'filename': file.filename
                }
            })
            
        finally:
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Ensure storage
    ensure_storage()
    
    # Run development server
    print("🎙️ Starting Voice Security System API (Resemblyzer Edition)...")
    print("📡 API will be available at http://localhost:5001")
    print("🌐 React frontend should connect to this URL")
    print(f"💾 Gallery storage: {GALLERY_PATH}")
    print(f"🎵 Audio storage: {AUDIO_STORAGE}")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=False,
        threaded=True
    )
