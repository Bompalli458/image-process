import os


BUCKET_NAME = os.getenv('BUCKET_NAME', 'compressed-images-url-bucket')
ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

# Database Configuration
DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql+psycopg2://postgres:postgres@localhost/image_processing')

# Redis Configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Optional: Direct DB Configuration (if needed separately)
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'image_processing')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
