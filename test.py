from dotenv import load_dotenv
from hdbcli import dbapi
import os

# Load environment variables
load_dotenv()


def get_mobialert_failures():
    """
    Connects to SAP HANA and fetches MobiAlert reports that failed to send
    (i.e., have a non-null EMAILMESSAGE and were scheduled for yesterday).

    Returns a list of dicts with keys: CONFIGID, OBJECTID, DOCUMENTCODE,
    TYPE, USERCODE, CONFIGNAME, EMAILMESSAGE.
    Returns an empty list on error or no results.
    """
    conn = None
    cursor = None
    try:
        conn = dbapi.connect(
            address=os.getenv("HANA_ADDRESS"),
            port=int(os.getenv("HANA_PORT")),
            user=os.getenv("HANA_USER"),
            password=os.getenv("HANA_PASSWORD")
        )

        cursor = conn.cursor()
        cursor.execute('SET SCHEMA MOBIALERT')

        query = """
            SELECT t0."CONFIGID",T0."OBJECTID", T0."DOCUMENTCODE", T0."TYPE", T0."USERCODE", t1."CONFIGNAME", t0."EMAILMESSAGE"
            FROM CNFG1_LOG t0
            JOIN OCNFG t1 ON t1."CONFIGID" = t0."CONFIGID"
            WHERE DAYS_BETWEEN(
                    TO_DATE(TO_TIMESTAMP(t0."NEXTDATETIME")),
                    CURRENT_DATE
                  ) <= 1
            AND t0."EMAILMESSAGE" IS NOT NULL
            and t0."EMAILMESSAGE" not like 'No Records Found in RPT file%'
            ORDER BY t0."ALERTID" DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "CONFIGID":     row[0],
                "OBJECTID":     row[1],
                "DOCUMENTCODE": row[2],
                "TYPE":         row[3],
                "USERCODE":     row[4],
                "CONFIGNAME":   row[5],
                "EMAILMESSAGE": row[6],
            })

        return results

    except Exception as e:
        # Import here to avoid circular dependency issues at module level
        import logging
        logging.getLogger("test").error(f"MobiAlert DB query failed: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ── Standalone test run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    rows = get_mobialert_failures()
    if rows:
        print(f"Found {len(rows)} MobiAlert failure(s):")
        for r in rows:
            print(r)
    else:
        print("No MobiAlert failures found (or query returned no rows).")
