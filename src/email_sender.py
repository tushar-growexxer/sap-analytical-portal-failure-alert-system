import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from src import config
from src.utils import setup_logger

logger = setup_logger("email_sender")

def send_report_email(file_path):
    """
    Sends the specified file to the configured recipients via SMTP.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False

    if not config.EMAIL_TO:
        logger.warning("No recipients defined in EMAIL_TO. Skipping email.")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = config.SENDER_EMAIL
        msg['To'] = ", ".join(config.EMAIL_TO)
        msg['Cc'] = ", ".join(config.EMAIL_CC)
        msg['Subject'] = f"Failed Reports Alert - {os.path.basename(file_path)}"

        # Email Body
        body = f"""
        <html>
          <body>
            <p>Hello Team,</p>
            <p>Please find attached the list of scheduled reports that failed to send today or yesterday.</p>
            <p><b>File:</b> {os.path.basename(file_path)}</p>
            <br>
            <p>Thanks,<br>SAP Automation Team</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))

        # Attachment
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(file_path)}",
        )
        msg.attach(part)

        # Recipients list (To + CC)
        recipients = config.EMAIL_TO + config.EMAIL_CC

        # Connect to Server
        logger.info(f"Connecting to SMTP server: {config.SMTP_SERVER}:{config.SMTP_PORT}")
        server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        server.starttls()
        server.login(config.SENDER_EMAIL, config.SENDER_PASSWORD)
        
        # Send Email
        text = msg.as_string()
        server.sendmail(config.SENDER_EMAIL, recipients, text)
        server.quit()

        logger.info(f"Email sent successfully to {len(recipients)} recipients.")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False