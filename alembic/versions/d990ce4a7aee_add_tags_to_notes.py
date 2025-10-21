"""add_tags_to_notes

Revision ID: d990ce4a7aee
Revises: 001_initial_schema
Create Date: 2025-10-20 23:07:47.650515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection


# revision identifiers, used by Alembic.
revision = 'd990ce4a7aee'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tags column with database-appropriate defaults
    # PostgreSQL uses JSONB, SQLite uses TEXT with JSON encoding
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    
    if dialect_name == 'postgresql':
        # PostgreSQL: use JSONB with proper casting
        op.add_column('notes', sa.Column('tags', sa.JSON(), nullable=True))
        op.execute("UPDATE notes SET tags = '[]'::jsonb WHERE tags IS NULL")
    else:
        # SQLite: use TEXT with JSON encoding
        op.add_column('notes', sa.Column('tags', sa.JSON(), nullable=True, server_default='[]'))


def downgrade() -> None:
    # Remove tags column
    op.drop_column('notes', 'tags')
