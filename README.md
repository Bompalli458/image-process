Project Documentation
1. Project Overview
   1.1. Description
   This project is a Flask application designed to handle the uploading, processing, and status tracking of CSV files containing product information. It uses Celery for asynchronous task processing and Redis as the broker.

    1.2. Features
   File Upload: Allows users to upload CSV files for processing.
   Asynchronous Processing: Uses Celery to process uploaded files in the background.
   Status Check: Provides an endpoint to fetch the processing status using a unique request ID.
 
2. Installation
   2.1. Prerequisites
   Python 3.6 or later
   Redis (for Celery)
   PostgreSQL (or another database configured in db_config.py)

   2.2. Setup
   Clone the Repository
   git clone https://github.com/Bompalli458/image-process.git
   cd image-process

    2.3 Create and Activate Virtual Environment 
     python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

   2.4 Install Dependencies
   pip install -r requirements.txt
   
3. Configure the Database
   Ensure that your database settings in db_config.py are correctly set up.

Run Redis Server
Start the Redis server as per your installation method.
 I have installed with command: wsl --install
   create username and password
   run the redis server with command: sudo service redis-server start
   check the redis server started or not with command: redis-cli ping
   It responds with message: pong (means server is up)

create database tables with below script

1. processing_requests table have column such as id,request_id, status, created_at

          CREATE TABLE IF NOT EXISTS public.processing_requests
          (
          id integer NOT NULL DEFAULT nextval('processing_requests_id_seq'::regclass),
          request_id uuid NOT NULL,
          status character varying(20) COLLATE pg_catalog."default" NOT NULL,
          created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
          CONSTRAINT processing_requests_pkey PRIMARY KEY (id),
          CONSTRAINT processing_requests_request_id_key UNIQUE (request_id)
          )
          
          TABLESPACE pg_default;
          
          ALTER TABLE IF EXISTS public.processing_requests
          OWNER to postgres;
      
2. products table have columns such as  id,processing_request_id,serial_number,product_name,input_image_urls,output_image_urls,created_at

        CREATE TABLE IF NOT EXISTS public.products
        (
        id integer NOT NULL DEFAULT nextval('products_id_seq'::regclass),
        processing_request_id uuid,
        serial_number integer,
        product_name character varying(255) COLLATE pg_catalog."default",
        input_image_urls text[] COLLATE pg_catalog."default",
        output_image_urls text[] COLLATE pg_catalog."default",
        created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT products_pkey PRIMARY KEY (id),
        CONSTRAINT products_processing_request_id_fkey FOREIGN KEY (processing_request_id)
        REFERENCES public.processing_requests (request_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
        )
        
        TABLESPACE pg_default;
        
        ALTER TABLE IF EXISTS public.products
        OWNER to postgres;

4. Postman Collection
   Place the Postman collection file in the root project directory with the filename image_processing.postman_collection.json.
   The collection includes an endpoint for uploading CSV files. Ensure the CSV files have headers matching products.csv [S. No, Product Name, Input Image Urls].

5. Project Enhancements:
   AWS Integration: 
   Configured AWS for uploading compressed image URLs and providing publicly accessible object URLs. The compressed image URLs are stored in the output_image_urls column of the products table, associated with the input_image_urls.


6. Project Flow
   File Upload:
      Upon uploading a CSV file, the endpoint validates the format and headers.
      It processes the file contents, generates a unique request_id, and inserts records into the products table with default empty output_image_urls.
   Background Processing:
      Celery tasks are triggered to process the images listed in input_image_urls.
      The images are converted to JPEG format, compressed to 50% of the original size, and uploaded to an S3 bucket.
      The S3 object URLs (compressed images) are updated in the output_image_urls column of the products table.
   Completion:
      Once all images are processed, the status of the processing_requests table is updated to "completed."
   
   
7. Reference
   Upload File: Use the file products.csv for testing.
   Postman Collection: Use the collection from image_processing.postman_collection.json.

Important environment Variables

BUCKET_NAME = 'MAIL TO bompallinarasimhulu555@gmail.com for credentials'
ACCESS_KEY_ID = 'MAIL TO bompallinarasimhulu555@gmail.com for credentials'
SECRET_ACCESS_KEY = 'MAIL TO bompallinarasimhulu555@gmail.com for credentials'
DATABASE_URI = 'postgresql+psycopg2://postgres:postgres@localhost/image_processing'
REDIS_URL = 'redis://localhost:6379/0'

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'image_processing'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

The above ACCESS_KEY_ID,BUCKET_NAME,SECRET_ACCESS_KEY are not given to public access. Let me know if you wanted to use it.
you can contact me  :
email: bompallinarasimhulu555@gmail.com

