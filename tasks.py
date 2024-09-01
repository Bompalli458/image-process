import logging
from db_config import get_db_connection
from upload_image_to_s3 import upload_image_to_s3
from celery_config import celery_app

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@celery_app.task(name='tasks.process_file_task')
def process_file_task(records, request_id):
    logger.info('Starting process_file_task with request_id: %s', request_id)

    class ImageProcessData:
        def __init__(self, product_name, input_image_urls, output_image_urls):
            self.product_name = product_name
            self.input_image_urls = input_image_urls
            self.output_image_urls = output_image_urls

    conn = None
    try:
        conn = get_db_connection()
        for record in records:
            product_name = record.get('Product Name', 'Unknown Product')
            input_image_urls = record.get('Input Image Urls', '').split(',')
            filtered_image_urls = [url.strip() for url in input_image_urls if url.strip()]

            if not filtered_image_urls:
                logger.warning('No image URLs found for product: %s', product_name)
                continue

            logger.info('Processing product: %s with %d image(s)', product_name, len(filtered_image_urls))
            output_image_urls = []

            for image_url in filtered_image_urls:
                if not image_url:
                    logger.warning('Empty image URL found for product: %s', product_name)
                    continue

                try:
                    logger.info('Compressing image from URL: %s', image_url)
                    output_image_url = upload_image_to_s3(image_url)
                    output_image_urls.append(output_image_url)
                except Exception as e:
                    logger.error('Failed to process image URL %s with exception: %s', image_url, str(e))
                    continue

            image_data = ImageProcessData(product_name, filtered_image_urls, output_image_urls)
            update_product_data(conn, request_id, image_data)
    except Exception as e:
        logger.error('Failed to connect to the database or process records with exception: %s', str(e))
    finally:
        if conn:
            conn.close()
            logger.info('Database connection closed.')

def update_product_data(conn, request_id, image_data):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 1 FROM public.products WHERE processing_request_id = %s
                ''',
                (request_id,)
            )
            exists = cursor.fetchone() is not None

            if exists:
                logger.info('Record found for request_id: %s. Updating data.', request_id)

                output_image_urls_array = '{' + ','.join([f'"{url}"' for url in image_data.output_image_urls]) + '}'

                cursor.execute(
                    '''
                    UPDATE public.products
                    SET output_image_urls = %s
                    WHERE processing_request_id = %s
                    ''',
                    (output_image_urls_array, request_id)
                )
                conn.commit()
                logger.info('Data updated successfully for request_id: %s', request_id)
            else:
                logger.info('No record found for request_id: %s. Skipping insertion.', request_id)

            update_processing_request_status(conn, request_id, 'completed')
    except Exception as e:
        logger.error('Failed to update data in the database for request_id: %s with exception: %s', request_id, str(e))

def update_processing_request_status(conn, request_id, status):
    try:
        with conn.cursor() as cursor:
            logger.info('Updating processing request status for request_id: %s', request_id)
            cursor.execute(
                '''
                UPDATE public.processing_requests
                SET status = %s
                WHERE request_id = %s
                ''',
                (status, request_id)
            )
            conn.commit()
            logger.info('Processing request status updated successfully for request_id: %s', request_id)
    except Exception as e:
        logger.error('Failed to update processing request status for request_id: %s with exception: %s', request_id, str(e))

@celery_app.task(name='tasks.test_task')
def test_task():
    try:
        logger.info("Test task executed")
    except Exception as e:
        logger.error(f"Error executing test_task: {str(e)}")
