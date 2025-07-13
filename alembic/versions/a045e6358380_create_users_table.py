"""create users table

Revision ID: a045e6358380
Revises: 
Create Date: 2025-07-10 17:16:07.136056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a045e6358380'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('mobile', sa.String(length=14), nullable=False, unique=True),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('user_type', sa.Enum('admin', 'doctor', 'patient', name='usertype'), nullable=True),
        sa.Column('division', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('thana', sa.String(length=100), nullable=True),
        sa.Column('profile_image', sa.String(length=255), nullable=True),
        sa.Column('license_number', sa.String(length=100), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('consultation_fee', sa.Integer(), nullable=True),
        sa.Column('available_timeslots', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('users')
