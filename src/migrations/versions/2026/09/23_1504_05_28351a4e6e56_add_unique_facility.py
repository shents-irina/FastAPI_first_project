"""add unique facility

Revision ID: 28351a4e6e56
Revises: 452ba103b4aa
Create Date: 2026-09-23 15:04:05.264599

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "28351a4e6e56"
down_revision: Union[str, Sequence[str], None] = "452ba103b4aa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(None, "facilities", ["title"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "facilities", type_="unique")
