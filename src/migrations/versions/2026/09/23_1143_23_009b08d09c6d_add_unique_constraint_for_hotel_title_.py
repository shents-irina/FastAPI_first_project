"""add unique constraint for hotel title and location

Revision ID: 009b08d09c6d
Revises: 4c9f10c24aab
Create Date: 2026-09-23 11:43:23.956641

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "009b08d09c6d"
down_revision: Union[str, Sequence[str], None] = "4c9f10c24aab"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_hotels_title_location", "hotels", ["title", "location"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_hotels_title_location", "hotels", type_="unique")
