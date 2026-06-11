import pandas as pd
import psycopg2
from pymongo import MongoClient
from psycopg2.extras import execute_batch
from psycopg2 import sql
from datetime import datetime

POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "arjun"
TARGET_DB = "tceq_project"

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "tceq_project"
MONGO_COLLECTION = "raw_nov_json"

TABLE_NAME = "tceq_violations"
CSV_OUTPUT = "tceq_violations.csv"


def create_database_if_not_exists():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TARGET_DB,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TARGET_DB)))
        print(f"Database '{TARGET_DB}' created.")
    else:
        print(f"Database '{TARGET_DB}' already exists.")

    cur.close()
    conn.close()


def load_mongo_to_postgres_and_save_csv():
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB]
    mongo_collection = mongo_db[MONGO_COLLECTION]

    pg_conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=TARGET_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    pg_cursor = pg_conn.cursor()

    try:
        pg_cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id BIGSERIAL PRIMARY KEY,
            rn_number TEXT,
            rn_name TEXT,
            business TEXT,
            phys_loc TEXT,
            phys_city TEXT,
            phys_state TEXT,
            phys_zip TEXT,
            county TEXT,
            investigation_no TEXT,
            invest_approved_dt TEXT,
            violation_status_date TEXT,
            coordinates_centroid_poly TEXT,
            region TEXT,
            violation_id TEXT,
            a_viol_track_num TEXT,
            a_viol_citations TEXT,
            b_viol_track_num TEXT,
            b_viol_citations TEXT,
            c_viol_track_num TEXT,
            c_viol_citations TEXT,
            viol_cnt TEXT,
            source TEXT,
            file_name TEXT,
            ingested_at TIMESTAMPTZ
        )
        """)
        pg_conn.commit()

        docs = list(
            mongo_collection.find(
                {},
                {"_id": 0, "raw_record": 1, "source": 1, "file_name": 1, "ingested_at": 1}
            )
        )

        print(f"Total MongoDB documents found: {len(docs)}")

        rows = []
        for doc in docs:
            record = doc.get("raw_record", {})
            rows.append((
                record.get("rn_number"),
                record.get("rn_name"),
                record.get("business"),
                record.get("phys_loc"),
                record.get("phys_city"),
                record.get("phys_state"),
                record.get("phys_zip"),
                record.get("county"),
                record.get("investigation_no"),
                record.get("invest_approved_dt"),
                record.get("violation_status_date"),
                record.get("coordinates_centroid_poly"),
                record.get("region"),
                record.get("violation_id"),
                record.get("a_viol_track_num"),
                record.get("a_viol_citations"),
                record.get("b_viol_track_num"),
                record.get("b_viol_citations"),
                record.get("c_viol_track_num"),
                record.get("c_viol_citations"),
                record.get("viol_cnt"),
                doc.get("source"),
                doc.get("file_name"),
                doc.get("ingested_at")
            ))

        if rows:
            insert_sql = f"""
            INSERT INTO {TABLE_NAME} (
                rn_number, rn_name, business, phys_loc, phys_city, phys_state, phys_zip,
                county, investigation_no, invest_approved_dt, violation_status_date,
                coordinates_centroid_poly, region, violation_id,
                a_viol_track_num, a_viol_citations, b_viol_track_num, b_viol_citations,
                c_viol_track_num, c_viol_citations, viol_cnt,
                source, file_name, ingested_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """

            execute_batch(pg_cursor, insert_sql, rows, page_size=1000)
            pg_conn.commit()

            pg_cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            total_rows = pg_cursor.fetchone()[0]
            print(f"Inserted {len(rows)} rows into PostgreSQL.")
            print(f"Total rows currently in PostgreSQL: {total_rows}")

            export_query = f"""
            SELECT
                rn_number, rn_name, business, phys_loc, phys_city, phys_state, phys_zip,
                county, investigation_no, invest_approved_dt, violation_status_date,
                coordinates_centroid_poly, region, violation_id,
                a_viol_track_num, a_viol_citations, b_viol_track_num, b_viol_citations,
                c_viol_track_num, c_viol_citations, viol_cnt,
                source, file_name, ingested_at
            FROM {TABLE_NAME}
            ORDER BY rn_number, investigation_no, violation_id
            """
            export_df = pd.read_sql_query(export_query, pg_conn)
            export_df.to_csv(CSV_OUTPUT, index=False)
            print(f"Saved PostgreSQL table to {CSV_OUTPUT}")
        else:
            print("No rows found in MongoDB.")

    except Exception as e:
        pg_conn.rollback()
        print("Error:", e)

    finally:
        pg_cursor.close()
        pg_conn.close()
        mongo_client.close()


if __name__ == "__main__":
    create_database_if_not_exists()
    load_mongo_to_postgres_and_save_csv()