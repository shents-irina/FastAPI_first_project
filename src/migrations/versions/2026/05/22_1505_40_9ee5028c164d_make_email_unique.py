"""Make email unique

Revision ID: 9ee5028c164d
Revises: 54713f3cf040
Create Date: 2026-05-22 15:05:40.513094

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9ee5028c164d"
down_revision: Union[str, Sequence[str], None] = "54713f3cf040"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "users", type_="unique")
