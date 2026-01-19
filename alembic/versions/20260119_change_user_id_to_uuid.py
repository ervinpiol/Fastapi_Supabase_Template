"""Change users.id to UUID

Revision ID: 20260119_change_user_id_to_uuid
Revises: bc1dce181450
Create Date: 2026-01-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260119_change_user_id_to_uuid"
down_revision: Union[str, None] = "bc1dce181450"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure pgcrypto is available for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Drop default/sequence tied to integer PK
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT;")

    # Convert existing integer ids to new UUID values
    op.execute("ALTER TABLE users ALTER COLUMN id TYPE uuid USING gen_random_uuid();")

    # Set new default
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT gen_random_uuid();")

    # Drop old sequence if it exists
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq CASCADE;")


def downgrade() -> None:
    # Recreate an integer sequence
    op.execute("CREATE SEQUENCE IF NOT EXISTS users_id_seq;")

    # Remove UUID default
    op.execute("ALTER TABLE users ALTER COLUMN id DROP DEFAULT;")

    # Convert UUIDs back to integers (new integers will be generated)
    op.execute(
        "ALTER TABLE users ALTER COLUMN id TYPE integer USING nextval('users_id_seq');"
    )

    # Set default to the integer sequence
    op.execute(
        "ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq');"
    )
