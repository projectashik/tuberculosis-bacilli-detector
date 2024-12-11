from flask import Flask, render_template, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import time
import threading
import os
import sys
import tflite_runtime.interpreter as tflite
from PIL import Image as PILImage
import json
from azure.storage.blob import BlobServiceClient
from flask_migrate import Migrate
from sqlalchemy import and_, or_
import numpy as np
import math
from object_detection import ObjectDetection

# Initialize NumPy with specific configurations for Raspberry Pi
try:
    import numpy
    numpy.set_printoptions(threshold=sys.maxsize)
    import numpy as np
except ImportError as e:
    print(f"Error importing NumPy: {e}")
    print("Please install NumPy using: pip install numpy==1.23.0")
    raise

app = Flask(__name__)

class TFLiteObjectDetection(ObjectDetection):
    """Object Detection class for TensorFlow Lite"""
    def __init__(self, model_filename, labels):
        super(TFLiteObjectDetection, self).__init__(labels)
        self.interpreter = tflite.Interpreter(model_path=model_filename)
        self.interpreter.allocate_tensors()
        self.input_index = self.interpreter.get_input_details()[0]['index']
        self.output_index = self.interpreter.get_output_details()[0]['index']

    def predict(self, preprocessed_image):
        inputs = np.array(preprocessed_image, dtype=np.float32)[np.newaxis, :, :, (2, 1, 0)]  # RGB -> BGR and add 1 dimension.

        # Resize input tensor and re-allocate the tensors.
        self.interpreter.resize_tensor_input(self.input_index, inputs.shape)
        self.interpreter.allocate_tensors()

        self.interpreter.set_tensor(self.input_index, inputs)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_index)[0]

def run_tflite_inference(image_path, model_name):
    """Run TensorFlow Lite inference on an image"""
    try:
        print(f"\nProcessing image: {image_path}")

        # Check if image exists
        if not os.path.exists(image_path):
            return {
                'status': 'error',
                'error': f'Image file not found: {image_path}'
            }

        # Check if model exists
        model_path = os.path.join('models', model_name, 'model.tflite')
        labels_path = os.path.join('models', model_name, 'labels.txt')

        if not os.path.exists(model_path):
            return {
                'status': 'error',
                'error': f'Model file not found: {model_path}'
            }

        try:
            # Load labels
            with open(labels_path, 'r') as f:
                labels = [label.strip() for label in f.readlines()]

            # Initialize object detection model
            od_model = TFLiteObjectDetection(model_path, labels)

            # Load and process image
            image = PILImage.open(image_path)
            predictions = od_model.predict_image(image)

            print("Raw predictions type:", type(predictions))
            print("Raw predictions:", predictions)

            # Ensure predictions is a list of dictionaries with the required format
            if not isinstance(predictions, list):
                predictions = []

            # Validate each prediction has the required fields
            valid_predictions = []
            for pred in predictions:
                if isinstance(pred, dict) and 'probability' in pred and 'boundingBox' in pred:
                    valid_predictions.append(pred)
                else:
                    print(f"Invalid prediction format: {pred}")

            return {
                'status': 'success',
                'predictions': valid_predictions
            }

        except Exception as model_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Model error details: {error_trace}")
            return {
                'status': 'error',
                'error': f'Model error: {str(model_error)}\nTrace: {error_trace}'
            }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        return {
            'status': 'error',
            'error': f'Preprocessing error: {str(e)}\nTrace: {error_trace}'
        }

tensorflow_lite_models = {
    'tuberculosis': "tuberculosis_bacilla_v1"
}

# SQLite configuration (local database)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'

# PostgreSQL configuration (cloud backup database)
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'hospital_backup')
POSTGRES_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'

app.config['SQLALCHEMY_BINDS'] = {
    'postgres': POSTGRES_URI
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

ESP32_CAM_URL = "http://192.168.138.12"  # Change this to your ESP32-CAM IP address
ESP32_CAM_STREAM_URL = f"{ESP32_CAM_URL}:81/stream"  # Stream URL for ESP32-CAM
CAPTURE_DIR = "static/captures"  # Directory to save captured images
os.makedirs(CAPTURE_DIR, exist_ok=True)


# Add these constants at the top with other configurations
CAPTURE_TOTAL_IMAGES = 10
CAPTURE_INTERVAL_SECONDS = 3

# Azure Blob Storage settings
AZURE_CONNECTION_STRING = os.getenv('AZURE_CONNECTION_STRING')
AZURE_CONTAINER_NAME = os.getenv('AZURE_CONTAINER_NAME')

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    contact = db.Column(db.String(50))
    tests = db.relationship('Test', backref='patient', lazy=True)
    is_backed_up = db.Column(db.Boolean, default=False)
    backup_date = db.Column(db.DateTime)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    pathologist_name = db.Column(db.String(100))
    referring_doctor = db.Column(db.String(100))
    images = db.relationship('Image', backref='test', lazy=True)
    is_backed_up = db.Column(db.Boolean, default=False)
    backup_date = db.Column(db.DateTime)
    ai_status = db.Column(db.String(20), default='pending')  # pending, completed
    ai_results = db.Column(db.Text)  # JSON field to store AI analysis results
    manual_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    test_results = db.Column(db.Text)  # JSON field to store manual test results
    remarks = db.Column(db.Text)  # Additional remarks or notes
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    azure_url = db.Column(db.String(500))
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_backed_up = db.Column(db.Boolean, default=False)
    backup_date = db.Column(db.DateTime)

# PostgreSQL backup models
class PatientBackup(db.Model):
    __bind_key__ = 'postgres'
    __tablename__ = 'patient_backup'

    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    contact = db.Column(db.String(50))
    backup_date = db.Column(db.DateTime, default=datetime.utcnow)

class TestBackup(db.Model):
    __bind_key__ = 'postgres'
    __tablename__ = 'test_backup'

    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer)
    patient_original_id = db.Column(db.Integer)
    test_name = db.Column(db.String(100), nullable=False)
    test_date = db.Column(db.DateTime)
    pathologist_name = db.Column(db.String(100))
    referring_doctor = db.Column(db.String(100))
    backup_date = db.Column(db.DateTime, default=datetime.utcnow)

class ImageBackup(db.Model):
    __bind_key__ = 'postgres'
    __tablename__ = 'image_backup'

    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer)
    test_original_id = db.Column(db.Integer)
    image_path = db.Column(db.String(200), nullable=False)
    azure_url = db.Column(db.String(500))
    captured_at = db.Column(db.DateTime)
    backup_date = db.Column(db.DateTime, default=datetime.utcnow)

# Global variables
capture_images = False
capture_thread = None
current_test_id = None
image_count = 0


def ensure_test_directory(test_id):
    """Create a directory for the test if it doesn't exist"""
    test_dir = os.path.join(CAPTURE_DIR, f"test_{test_id}")
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def capture_images_periodically(app_instance):
    global capture_images, image_count, current_test_id

    # Create application context
    ctx = app_instance.app_context()
    ctx.push()  # Push the context

    try:
        # Create a unique directory for this test
        test_dir = os.path.join(CAPTURE_DIR, f"test_{current_test_id}")
        os.makedirs(test_dir, exist_ok=True)

        while capture_images and image_count < CAPTURE_TOTAL_IMAGES:
            try:
                # Capture an image from ESP32
                img_resp = requests.get(f"{ESP32_CAM_URL}/capture")
                if img_resp.status_code == 200:
                    # Save the image with unique name in test-specific directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"image_{timestamp}_{image_count + 1}.jpg"
                    filepath = os.path.join(test_dir, filename)

                    with open(filepath, "wb") as f:
                        f.write(img_resp.content)

                    # Save image metadata to database
                    relative_path = os.path.join(f"captures/test_{current_test_id}", filename)
                    new_image = Image(
                        test_id=current_test_id,
                        image_path=relative_path
                    )
                    db.session.add(new_image)
                    db.session.commit()

                    image_count += 1
                    print(f"Captured {filepath}")
            except Exception as e:
                print(f"Error capturing image: {e}")

            time.sleep(CAPTURE_INTERVAL_SECONDS)

        if image_count >= CAPTURE_TOTAL_IMAGES:
            capture_images = False

    finally:
        ctx.pop()  # Make sure we always pop the context

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_test')
def run_test():
    return render_template('run_test.html')

@app.route('/view_records')
def view_records():
    # Get filter parameters
    patient_name = request.args.get('patient_name', '').strip()
    test_name = request.args.get('test_name', '').strip()
    manual_status = request.args.get('manual_status', '').strip()
    ai_status = request.args.get('ai_status', '').strip()
    referring_doctor = request.args.get('referring_doctor', '').strip()
    pathologist_name = request.args.get('pathologist_name', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    # Start with base query
    query = Test.query.join(Patient)

    # Apply filters
    filters = []
    if patient_name:
        filters.append(Patient.name.ilike(f'%{patient_name}%'))
    if test_name:
        filters.append(Test.test_name.ilike(f'%{test_name}%'))
    if manual_status:
        filters.append(Test.manual_status == manual_status)
    if ai_status:
        filters.append(Test.ai_status == ai_status)
    if referring_doctor:
        filters.append(Test.referring_doctor.ilike(f'%{referring_doctor}%'))
    if pathologist_name:
        filters.append(Test.pathologist_name.ilike(f'%{pathologist_name}%'))

    # Handle date range
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            filters.append(Test.test_date >= date_from)
        except ValueError:
            pass

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the entire end date
            date_to = date_to + timedelta(days=1)
            filters.append(Test.test_date < date_to)
        except ValueError:
            pass

    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))

    # Order by most recent first
    tests = query.order_by(Test.test_date.desc()).all()
    return render_template('view_records.html', tests=tests)

@app.route('/get_test_results/<int:test_id>')
def get_test_results(test_id):
    test = Test.query.get_or_404(test_id)
    return jsonify({
        'ai_results': test.ai_results,
        'test_results': test.test_results
    })

@app.route('/save_patient', methods=['POST'])
def save_patient():
    data = request.form

    patient = Patient(
        name=data['patient_name'],
        address=data['address'],
        contact=data['contact']
    )
    db.session.add(patient)
    db.session.flush()

    test = Test(
        patient_id=patient.id,
        test_name=data['test_name'],
        pathologist_name=data['pathologist_name'],
        referring_doctor=data['referring_doctor']
    )
    db.session.add(test)
    db.session.commit()

    global current_test_id
    current_test_id = test.id

    # Create directory for this test's images
    ensure_test_directory(current_test_id)

    return redirect('/live_feed')

@app.route('/live_feed')
def live_feed():
    return render_template('live_feed.html', ESP32_CAM_STREAM_URL=ESP32_CAM_STREAM_URL, current_test_id=current_test_id)

@app.route('/start_capturing')
def start_capturing():
    global capture_images, capture_thread, image_count
    if not capture_images:
        capture_images = True
        image_count = 0
        capture_thread = threading.Thread(
            target=capture_images_periodically,
            args=(app,)
        )
        capture_thread.daemon = True
        capture_thread.start()
    return jsonify({"status": "started"})

@app.route('/capture_status')
def capture_status():
    global image_count
    return jsonify({
        "count": image_count,
        "total": CAPTURE_TOTAL_IMAGES,
        "completed": image_count >= CAPTURE_TOTAL_IMAGES
    })

@app.template_filter('from_json')
def from_json(value):
    """Convert a JSON string to Python object"""
    try:
        return json.loads(value)
    except:
        return []

@app.template_filter('tojson')
def to_json(value, indent=None):
    """Convert a Python object to JSON string"""
    try:
        return json.dumps(value, indent=indent)
    except:
        return str(value)

@app.route('/view_report/<int:test_id>')
def view_report(test_id):
    test = Test.query.get_or_404(test_id)
    return render_template('report.html', test=test)

@app.route('/backup_to_azure/<int:test_id>')
def backup_to_azure(test_id):
    try:
        # Validate environment variables
        if not AZURE_CONNECTION_STRING or not AZURE_CONTAINER_NAME:
            return jsonify({"status": "error", "message": "Azure configuration is missing"})

        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

        test = Test.query.get_or_404(test_id)
        if not test.images:
            return jsonify({"status": "error", "message": "No images found for this test"})

        successful_uploads = 0
        for image in test.images:
            if not image.azure_url:  # Only upload if not already uploaded
                # Get the full path of the image
                image_full_path = os.path.join('static', image.image_path)

                # Check if file exists
                if not os.path.exists(image_full_path):
                    continue

                try:
                    blob_name = f"test_{test_id}/{os.path.basename(image.image_path)}"

                    # Upload the blob
                    with open(image_full_path, "rb") as data:
                        container_client.upload_blob(name=blob_name, data=data, overwrite=True)

                    # Update the Azure URL using the account name from connection string
                    account_name = AZURE_CONNECTION_STRING.split(';')[1].split('=')[1]
                    image.azure_url = f"https://{account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{blob_name}"
                    successful_uploads += 1
                except Exception as upload_error:
                    print(f"Error uploading {image_full_path}: {str(upload_error)}")
                    continue

        if successful_uploads > 0:
            db.session.commit()
            return jsonify({"status": "success", "message": f"Successfully backed up {successful_uploads} images"})
        else:
            error_message = "No images were successfully backed up"
            return jsonify({"status": "error", "message": "No images were successfully backed up"})

    except Exception as e:
        print(f"Backup error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/update_quality/<int:quality>')
def update_quality(quality):
    try:
        # Ensure quality is within valid range
        quality = max(4, min(63, quality))

        # Send request to ESP32-CAM to update quality
        response = requests.get(f"{ESP32_CAM_URL}/control?var=quality&val={quality}")

        if response.status_code == 200:
            return jsonify({"status": "success", "quality": quality})
        else:
            return jsonify({"status": "error", "message": "Failed to update camera quality"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/backup_to_cloud/<int:test_id>')
def backup_to_cloud(test_id):
    try:
        # Get the test and related data
        test = Test.query.get_or_404(test_id)
        patient = test.patient

        # Create backup records
        patient_backup = PatientBackup(
            original_id=patient.id,
            name=patient.name,
            address=patient.address,
            contact=patient.contact
        )
        db.session.add(patient_backup)
        db.session.flush()

        test_backup = TestBackup(
            original_id=test.id,
            patient_original_id=patient.id,
            test_name=test.test_name,
            test_date=test.test_date,
            pathologist_name=test.pathologist_name,
            referring_doctor=test.referring_doctor
        )
        db.session.add(test_backup)
        db.session.flush()

        # Backup images
        for image in test.images:
            image_backup = ImageBackup(
                original_id=image.id,
                test_original_id=test.id,
                image_path=image.image_path,
                azure_url=image.azure_url,
                captured_at=image.captured_at
            )
            db.session.add(image_backup)

        # Update backup status
        test.is_backed_up = True
        test.backup_date = datetime.utcnow()
        patient.is_backed_up = True
        patient.backup_date = datetime.utcnow()

        for image in test.images:
            image.is_backed_up = True
            image.backup_date = datetime.utcnow()

        db.session.commit()
        return jsonify({"status": "success", "message": "Data backed up successfully"})

    except Exception as e:
        db.session.rollback()
        print(f"Backup error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/restore_from_backup')
def restore_from_backup():
    try:
        # Get all backup records
        patient_backups = PatientBackup.query.all()

        restored_count = 0
        for patient_backup in patient_backups:
            # Check if patient already exists
            existing_patient = Patient.query.filter_by(id=patient_backup.original_id).first()
            if not existing_patient:
                # Restore patient
                patient = Patient(
                    id=patient_backup.original_id,
                    name=patient_backup.name,
                    address=patient_backup.address,
                    contact=patient_backup.contact,
                    is_backed_up=True,
                    backup_date=patient_backup.backup_date
                )
                db.session.add(patient)
                db.session.flush()

                # Restore related tests
                tests = TestBackup.query.filter_by(patient_original_id=patient_backup.original_id).all()
                for test_backup in tests:
                    test = Test(
                        id=test_backup.original_id,
                        patient_id=patient.id,
                        test_name=test_backup.test_name,
                        test_date=test_backup.test_date,
                        pathologist_name=test_backup.pathologist_name,
                        referring_doctor=test_backup.referring_doctor,
                        is_backed_up=True,
                        backup_date=test_backup.backup_date
                    )
                    db.session.add(test)
                    db.session.flush()

                    # Restore related images
                    images = ImageBackup.query.filter_by(test_original_id=test_backup.original_id).all()
                    for image_backup in images:
                        image = Image(
                            id=image_backup.original_id,
                            test_id=test.id,
                            image_path=image_backup.image_path,
                            azure_url=image_backup.azure_url,
                            captured_at=image_backup.captured_at,
                            is_backed_up=True,
                            backup_date=image_backup.backup_date
                        )
                        db.session.add(image)

                restored_count += 1

        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Successfully restored {restored_count} records from backup"
        })

    except Exception as e:
        db.session.rollback()
        print(f"Restore error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/verify_test/<int:test_id>', methods=['POST'])
def verify_test(test_id):
    try:
        test = Test.query.get_or_404(test_id)
        test.manual_status = 'verified'
        db.session.commit()
        return jsonify({"status": "success", "message": "Test verified successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/reject_test/<int:test_id>', methods=['POST'])
def reject_test(test_id):
    try:
        test = Test.query.get_or_404(test_id)

        # Delete associated images from filesystem
        for image in test.images:
            if os.path.exists(os.path.join('static', image.image_path)):
                os.remove(os.path.join('static', image.image_path))

        # Delete the test directory
        test_dir = os.path.join(CAPTURE_DIR, f"test_{test_id}")
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

        # Delete the test and its associated images from database
        db.session.delete(test)
        db.session.commit()

        return jsonify({"status": "success", "message": "Test rejected and deleted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/rerun_test/<int:test_id>', methods=['POST'])
def rerun_test(test_id):
    try:
        test = Test.query.get_or_404(test_id)

        # Delete old images
        for image in test.images:
            if os.path.exists(os.path.join('static', image.image_path)):
                os.remove(os.path.join('static', image.image_path))
            db.session.delete(image)

        # Reset test status
        test.manual_status = 'pending'
        db.session.commit()

        # Set up for new capture
        global current_test_id, image_count
        current_test_id = test_id
        image_count = 0

        return jsonify({
            "status": "success",
            "message": "Test ready for rerun",
            "redirect_url": "/live_feed"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/update_test/<int:test_id>', methods=['POST'])
def update_test(test_id):
    try:
        test = Test.query.get_or_404(test_id)
        data = request.get_json()

        # Update test details
        if 'test_name' in data:
            test.test_name = data['test_name']
        if 'pathologist_name' in data:
            test.pathologist_name = data['pathologist_name']
        if 'referring_doctor' in data:
            test.referring_doctor = data['referring_doctor']
        if 'test_results' in data:
            test.test_results = json.dumps(data['test_results'])
        if 'remarks' in data:
            test.remarks = data['remarks']

        test.last_modified = datetime.utcnow()
        db.session.commit()

        return jsonify({"status": "success", "message": "Test updated successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    try:
        test = Test.query.get_or_404(test_id)

        # First delete all images from filesystem
        for image in test.images:
            if os.path.exists(os.path.join('static', image.image_path)):
                os.remove(os.path.join('static', image.image_path))
            # Delete each image record individually
            db.session.delete(image)

        # Commit the image deletions first
        db.session.commit()

        # Delete the test directory
        test_dir = os.path.join(CAPTURE_DIR, f"test_{test_id}")
        if os.path.exists(test_dir):
            os.rmdir(test_dir)

        # Now delete the test
        db.session.delete(test)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Test deleted successfully",
            "redirect_url": "/view_records"
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting test: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/run_ai_inference/<int:test_id>', methods=['POST'])
def run_ai_inference(test_id):
    try:
        test = Test.query.get_or_404(test_id)

        # Get the appropriate model name based on test type
        model_name = tensorflow_lite_models.get(test.test_name.lower())
        if not model_name:
            return jsonify({
                "status": "error",
                "message": f"No model found for test type: {test.test_name}"
            })

        results = []
        for image in test.images:
            image_path = os.path.join('static', image.image_path)
            if os.path.exists(image_path):
                inference_result = run_tflite_inference(image_path, model_name)
                results.append({
                    'image_path': image.image_path,
                    'result': inference_result
                })

        # Update test AI status and results
        test.ai_status = 'completed'
        test.ai_results = json.dumps(results)
        test.last_modified = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "AI inference completed successfully",
            "results": results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)})

# Add initialization function
def init_camera_settings():
    try:
        # Set framesize to 7 (SVGA - 800x600)
        response = requests.get(f"{ESP32_CAM_URL}/control?var=framesize&val=7")
        if response.status_code == 200:
            print("Camera framesize initialized successfully")
        else:
            print("Failed to initialize camera framesize")
    except Exception as e:
        print(f"Error initializing camera settings: {e}")

# Call initialization when app starts
with app.app_context():
    db.create_all()
    init_camera_settings()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
