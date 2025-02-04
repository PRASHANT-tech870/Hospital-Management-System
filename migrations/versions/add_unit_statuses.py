"""add unit statuses

Revision ID: add_unit_statuses
Revises: previous_revision
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_unit_statuses'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support JSON type natively, so we'll use Text
    op.add_column('equipment', sa.Column('unit_statuses', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('equipment', 'unit_statuses') 