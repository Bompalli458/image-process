from flask import Flask, request, jsonify
import pandas as pd
from io import StringIO
import uuid
import logging

from db_config import get_db_connection
from celery_config import celery_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def insert_processing_request(request_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                INSERT INTO processing_requests (request_id, status, created_at)
                VALUES (%s, %s, NOW())
                ''',
                (request_id, 'processing')
            )
            conn.commit()
            logger.info('Inserted into processing_requests with request_id: %s', request_id)
    except Exception as e:
        logger.error('Database error during insert_processing_request: %s', str(e))
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_products(records, request_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            for record in records:
                serial_no = record.get('S. No', 'Unknown Serial No')
                product_name = record.get('Product Name', 'Unknown Product')
                input_image_urls = record.get('Input Image Urls', '').split(',')

                filtered_image_urls = [url.strip() for url in input_image_urls if url.strip()]
                output_image_urls = []  # Placeholder for now

                cursor.execute(
                    '''
                    INSERT INTO products (serial_number, product_name, input_image_urls, output_image_urls, processing_request_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ''',
                    (serial_no, product_name, filtered_image_urls, output_image_urls, request_id)
                )
                logger.info('Inserted product: %s with request_id: %s', product_name, request_id)
            conn.commit()
    except Exception as e:
        logger.error('Database error during insert_products: %s', str(e))
        conn.rollback()
        raise
    finally:
        conn.close()

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the file part is in the request
        if 'file' not in request.files:
            logger.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Check if a file is selected
        if file.filename == '':
            logger.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400

        # Validate file type
        if file and file.filename.endswith('.csv'):
            request_id = str(uuid.uuid4())
            csv_data = file.read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_data))
            records = df.to_dict(orient='records')
            logger.info('Processing request_id: %s with %d records', request_id, len(records))

            try:
                insert_processing_request(request_id)
                insert_products(records, request_id)
            except Exception as e:
                logger.error('Error during file processing: %s', str(e))
                return jsonify({'error': 'File processing error'}), 500

            # Send the task to Celery for further processing
            result = celery_app.send_task('tasks.process_file_task', args=[records, request_id])

            return jsonify({'message': 'File is being processed', 'request_id': request_id}), 200

        # Invalid file type
        logger.error('Invalid file type: %s', file.filename)
        return jsonify({'error': 'Invalid file type'}), 400

    except Exception as e:
        logger.error('Error in upload_file: %s', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/status/<request_id>', methods=['GET'])
def get_status(request_id):
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT status FROM processing_requests
                    WHERE request_id = %s
                    ''', (request_id,)
                )
                result = cursor.fetchone()

                if result is None:
                    logger.error('Request ID %s not found', request_id)
                    return jsonify({'error': 'Request ID not found'}), 404

                status = result[0]
                return jsonify({'request_id': request_id, 'status': status}), 200

        except Exception as e:
            logger.error('Database error while fetching status: %s', str(e))
            return jsonify({'error': 'Database error while fetching status'}), 500
        finally:
            conn.close()

    except Exception as e:
        logger.error('Error in get_status: %s', str(e))
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
