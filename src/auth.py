import requests
import re
import time
from bs4 import BeautifulSoup
from src import config
from src.utils import setup_logger

logger = setup_logger("auth")

def perform_login():
    """
    Executes the full SAML + SAP B1 authentication flow.
    Returns:
        tuple: (requests.Session, csrf_token_string)
    """
    # Disable SSL Warnings
    requests.packages.urllib3.disable_warnings()
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/html, */*'
    })

    try:
        # 1. Access Portal
        logger.info(f"GET {config.PORTAL_URL}")
        resp1 = session.get(config.PORTAL_URL, verify=False)
        soup1 = BeautifulSoup(resp1.text, 'html.parser')

        saml_req = soup1.find('input', {'name': 'SAMLRequest'})
        if not saml_req:
            logger.error("SAMLRequest not found in initial response")
            return None, None

        # 2. Post to IDP
        logger.info(f"POST {config.IDP_SSO_URL}")
        resp2 = session.post(config.IDP_SSO_URL, data={
            'SAMLRequest': saml_req.get('value'),
            'RelayState': soup1.find('input', {'name': 'RelayState'}).get('value')
        }, verify=False)

        # Extract Token Ref
        saml2_token_ref = re.search(r'saml2TokenRef=([a-f0-9\-]+)', resp2.url + resp2.text)
        if not saml2_token_ref:
            logger.error("TokenRef not found in IDP response")
            return None, None
        token_ref = saml2_token_ref.group(1)

        # 3. Generate Security Token
        logger.info(f"GET {config.GEN_TOKEN_URL}")
        session.headers.update({'Referer': resp2.url})
        resp3 = session.get(f"{config.GEN_TOKEN_URL}?t={int(time.time()*1000)}", 
                            headers={'MaxDataServiceVersion': '2.0'}, verify=False)
        
        security_token = resp3.json().get('d', {}).get('GenerateSecurityToken')
        if not security_token:
            logger.error("Failed to generate security token")
            return None, None

        # 4. SAP B1 Login
        logger.info(f"POST {config.LOGON_URL} (Login)")
        resp4 = session.post(config.LOGON_URL, json={
            "DBInstance": config.DB_INSTANCE, 
            "CompanyDB": config.COMPANY_DB,
            "Account": config.SAP_USERNAME, 
            "Password": config.SAP_PASSWORD
        }, headers={
            'securitytoken': security_token, 
            'Content-Type': 'application/json;odata=verbose',
            'DataServiceVersion': '1.0', 
            'MaxDataServiceVersion': '2.0'
        }, verify=False)

        if resp4.status_code != 200 or resp4.json()['d']['LogonBySBOUser'] != 0:
            logger.error(f"Login Failed: {resp4.text}")
            return None, None

        # 5. Resume SSO
        logger.info(f"POST {config.IDP_SSO_URL} (Resume SSO)")
        session.headers.pop('securitytoken', None)
        session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
        resp5 = session.post(config.IDP_SSO_URL, data={'saml2TokenRef': token_ref}, verify=False)
        
        soup5 = BeautifulSoup(resp5.text, 'html.parser')
        saml_resp = soup5.find('input', {'name': 'SAMLResponse'})
        if not saml_resp:
            logger.error("SAMLResponse missing after login")
            return None, None

        # 6. ACS
        logger.info(f"POST {config.ACS_URL}")
        session.post(config.ACS_URL, data={
            'SAMLResponse': saml_resp.get('value'),
            'RelayState': soup5.find('input', {'name': 'RelayState'}).get('value')
        }, verify=False)

        # 7. Get CSRF
        logger.info(f"GET {config.CONTEXT_URL}")
        resp7 = session.get(config.CONTEXT_URL, headers={'X-Requested-With': 'XMLHttpRequest'}, verify=False)
        csrf_token = resp7.json().get('response', {}).get('data', {}).get('csrfToken')

        if not csrf_token:
            logger.error("Failed to retrieve CSRF token")
            return None, None

        return session, csrf_token

    except Exception as e:
        logger.error(f"Authentication exception: {e}")
        return None, None