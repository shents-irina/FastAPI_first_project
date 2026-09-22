"""

Revision ID: 4c9f10c24aab
Revises: ac30bb2bde38
Create Date: 2026-09-16 17:40:19.823207

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c9f10c24aab"
down_revision: str | Sequence[str] | None = "ac30bb2bde38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f("rooms_hotel_id_fkey"), "rooms", type_="foreignkey")
    op.create_foreign_key(None, "rooms", "hotels", ["hotel_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint(
        op.f("rooms_facilities_room_id_fkey"),
        "rooms_facilities",
        type_="foreignkey",
    )
    op.drop_constraint(
        op.f("rooms_facilities_facility_id_fkey"),
        "rooms_facilities",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "rooms_facilities",
        "facilities",
        ["facility_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        None,
        "rooms_facilities",
        "rooms",
        ["room_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(None, "rooms_facilities", type_="foreignkey")
    op.drop_constraint(None, "rooms_facilities", type_="foreignkey")
    op.create_foreign_key(
        op.f("rooms_facilities_facility_id_fkey"),
        "rooms_facilities",
        "facilities",
        ["facility_id"],
        ["id"],
    )
    op.create_foreign_key(
        op.f("rooms_facilities_room_id_fkey"),
        "rooms_facilities",
        "rooms",
        ["room_id"],
        ["id"],
    )
    op.drop_constraint(None, "rooms", type_="foreignkey")
    op.create_foreign_key(op.f("rooms_hotel_id_fkey"), "rooms", "hotels", ["hotel_id"], ["id"])
