from __future__ import annotations

"""
Simple seed script for dev/demo:
- Creates tenant "demo" and admin user "admin@demo.local" (password: demo1234) if absent.
"""

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.repositories.tenants import create_tenant, get_tenant_by_name
from app.repositories.users import create_user, get_user_by_email


def main() -> None:
    db = SessionLocal()
    try:
        tenant = get_tenant_by_name(db, "demo")
        if tenant is None:
            tenant = create_tenant(db, "demo")
            print("Created tenant 'demo'")

        user = get_user_by_email(db, "admin@demo.local")
        if user is None:
            create_user(db, tenant.id, "admin@demo.local", hash_password("demo1234"), role="admin")
            print("Created user admin@demo.local / demo1234")
        else:
            print("Seed user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    main()
