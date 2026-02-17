import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Credentials
DB_INSTANCE = os.getenv("DB_INSTANCE")
COMPANY_DB = os.getenv("COMPANY_DB")
SAP_USERNAME = os.getenv("SAP_USERNAME")
SAP_PASSWORD = os.getenv("SAP_PASSWORD")

# Base URL
BASE_URL = os.getenv("BASE_URL")

if not all([BASE_URL, DB_INSTANCE, COMPANY_DB, SAP_USERNAME, SAP_PASSWORD]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

# Derived URLs
PORTAL_URL = f"{BASE_URL}/Portal/"
IDP_SSO_URL = f"{BASE_URL}/sld/saml2/idp/sso"
ACS_URL = f"{BASE_URL}/Portal/saml2/sp/acs"
GEN_TOKEN_URL = f"{BASE_URL}/sld/sld.svc/GenerateSecurityToken"
LOGON_URL = f"{BASE_URL}/sld/sld.svc/LogonBySBOUser"
CONTEXT_URL = f"{BASE_URL}/Portal/user-context"
TARGET_API = f"{BASE_URL}/Portal/api/histories"

# File paths
OUTPUT_DIRECTORY = "daily_scheduled_data"
LOG_DIRECTORY = "logs"
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, "logs.txt")

# Report Configuration
REPORT_FILENAME_PREFIX = "failed_reports"

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Parse comma-separated emails into lists
EMAIL_TO = [e.strip() for e in os.getenv("EMAIL_TO", "").split(",") if e.strip()]
EMAIL_CC = [e.strip() for e in os.getenv("EMAIL_CC", "").split(",") if e.strip()]