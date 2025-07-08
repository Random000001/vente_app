import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "rayen1234")
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USER', 'u59284_eB9v2rDNQP')}:"
        f"{os.getenv('DB_PASSWORD', 'mJMpY9v+ZTz.CltLlv4v!E+t')}@"
        f"{os.getenv('DB_HOST', '67.220.85.157')}:"
        f"{os.getenv('DB_PORT', '3306')}/"
        f"{os.getenv('DB_NAME', 's59284_casino_bot')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EURO_TO_DINAR = 4.5