"""Pre-migration check: stamp existing tables if they were created before Alembic was set up."""
import os
import subprocess
import sys


def check_and_stamp():
    """Check if tables exist from create_all and need stamping."""
    db_url = os.environ.get("TENSORHUB_DATABASE_URL", "")
    if not db_url:
        return

    # Convert async URL to sync URL for psycopg2
    sync_url = db_url.replace("+asyncpg", "+psycopg2")

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(sync_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            has_alembic = conn.execute(
                text(
                    "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name='alembic_version')"
                )
            ).scalar()

            if not has_alembic:
                has_roles = conn.execute(
                    text(
                        "SELECT EXISTS(SELECT 1 FROM information_schema.tables "
                        "WHERE table_schema='public' AND table_name='roles')"
                    )
                ).scalar()

                if has_roles:
                    print("Existing tables detected without Alembic version tracking.")
                    print("Stamping database with initial migration...")
                    subprocess.run(["alembic", "stamp", "001"], check=True)
                    print("Stamp complete.")
                else:
                    print("Fresh database detected. Migrations will create tables.")
            else:
                print("Alembic version tracking found. Proceeding with migrations.")
    except Exception as e:
        print(f"Warning: Could not check database state: {e}")
        print("Proceeding with standard migration...")


if __name__ == "__main__":
    check_and_stamp()