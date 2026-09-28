"""add unique constraint for room hotel_id  and title

Revision ID: 452ba103b4aa
Revises: 009b08d09c6d
Create Date: 2026-09-23 13:15:46.083164

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "452ba103b4aa"
down_revision: Union[str, Sequence[str], None] = "009b08d09c6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_rooms_hotel_id_title", "rooms", ["hotel_id", "title"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_rooms_hotel_id_title", "rooms", type_="unique")
