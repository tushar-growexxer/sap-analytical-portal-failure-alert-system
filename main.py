import json
import os
from src.auth import perform_login
from src.processor import process_and_save_data, append_mobialert_to_excel, handle_mobialert_failures
from src.email_sender import send_report_email
from src import config
from src.utils import setup_logger

logger = setup_logger("main")

def main():
    logger.info("Starting Scraper Job")
    
    # 1. Authenticate
    session, csrf_token = perform_login()
    
    if not session or not csrf_token:
        logger.critical("Authentication failed. Aborting.")
        return

    # 2. Fetch Analytical Portal Data
    logger.info(f"GET {config.TARGET_API}")
    api_headers = {
        'X-CSRF-TOKEN': csrf_token, 
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        history_response = session.get(config.TARGET_API, headers=api_headers, verify=False)
        
        if history_response.status_code == 200:
            logger.info("Data fetched successfully")
            
            raw_data = history_response.json()

            # 3. Process Analytical Portal Data → Excel
            generated_file_path = process_and_save_data(raw_data)

            # 4. Fetch MobiAlert failures from SAP HANA and append to the same Excel
            generated_file_path = handle_mobialert_failures(generated_file_path)

            # # 5. Send Email (only if a file was generated)
            # if generated_file_path and os.path.exists(generated_file_path):
            #     logger.info(f"Report generated at {generated_file_path}. Sending email...")
                
            #     email_status = send_report_email(generated_file_path)
                
            #     if email_status:
            #         logger.info("Email sent successfully.")
            #     else:
            #         logger.error("Email sending failed.")
            # else:
            #     logger.info("No failures found in either system – all healthy. Skipping email.")

        else:
            logger.error(f"Failed to fetch history. Status: {history_response.status_code}")
            
    except Exception as e:
        logger.error(f"Main loop exception: {e}")

if __name__ == "__main__":
    main()
