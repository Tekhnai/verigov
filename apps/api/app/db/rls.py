from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Engine


def enable_rls(engine: Engine) -> None:
    """Enable RLS and policies for tenant-scoped tables. Safe when app.tenant_id is not set."""
    ddl = """
    -- Helpers
    CREATE OR REPLACE FUNCTION app_current_tenant() RETURNS integer AS $$
    BEGIN
      RETURN COALESCE(NULLIF(current_setting('app.tenant_id', true), '')::int, -1);
    EXCEPTION WHEN others THEN
      RETURN -1;
    END;
    $$ LANGUAGE plpgsql;

    -- Users
    ALTER TABLE users ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS users_tenant_isolation ON users;
    CREATE POLICY users_tenant_isolation ON users
      USING (tenant_id = app_current_tenant());

    -- Targets
    ALTER TABLE targets ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS targets_tenant_isolation ON targets;
    CREATE POLICY targets_tenant_isolation ON targets
      USING (tenant_id = app_current_tenant());

    -- Checks
    ALTER TABLE checks ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS checks_tenant_isolation ON checks;
    CREATE POLICY checks_tenant_isolation ON checks
      USING (tenant_id = app_current_tenant());

    -- Reports
    ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS reports_tenant_isolation ON reports;
    CREATE POLICY reports_tenant_isolation ON reports
      USING (tenant_id = app_current_tenant());

    -- Audit
    ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
    DROP POLICY IF EXISTS audit_tenant_isolation ON audit_log;
    CREATE POLICY audit_tenant_isolation ON audit_log
      USING (tenant_id = app_current_tenant());
    """
    with engine.connect() as conn:
        conn.execute(text(ddl))
        conn.commit()
