"""add unique constraint for m2m rooms_facilities

Revision ID: 3e91085e8efb
Revises: 28351a4e6e56
Create Date: 2026-09-25 16:12:48.315355

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3e91085e8efb"
down_revision: Union[str, Sequence[str], None] = "28351a4e6e56"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(
        "uq_m2m_room_id_facility_id",
        "rooms_facilities",
        ["room_id", "facility_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_m2m_room_id_facility_id", "rooms_facilities", type_="unique"
    )
