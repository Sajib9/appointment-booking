"""add doctor schedule table

Revision ID: c84454439aa0
Revises: b5956bcdcb85
Create Date: 2025-07-13 12:34:20.086648

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c84454439aa0'
down_revision: Union[str, Sequence[str], None] = 'b5956bcdcb85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum = sa.Enum('available', 'booked', name='doctor_schedule_status')
    op.create_table(
        'doctor_schedules',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('doctor_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('status', status_enum, nullable=False, server_default='available')
    )


def downgrade() -> None:
    op.drop_table('doctor_schedules')
