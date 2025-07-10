import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "rayen1234")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'u3118085_YwEd7gXSdL')}:"
        f"{os.getenv('DB_PASSWORD', 'q^rqDt5J+eHpjM1XEr7T2mE+')}@"
        f"{os.getenv('DB_HOST', '217.182.175.212')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 's3118085_db1752105802292')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EURO_TO_DINAR = 4.5
