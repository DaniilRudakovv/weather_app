"""Initial migration

Revision ID: 001
Revises:
Create Date: 2025-11-17 18:31:23

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('weather_queries',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('city_name', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('temperature', sa.Float(), nullable=True),
    sa.Column('feels_like', sa.Float(), nullable=True),
    sa.Column('humidity', sa.Integer(), nullable=True),
    sa.Column('pressure', sa.Integer(), nullable=True),
    sa.Column('weather_description', sa.String(), nullable=True),
    sa.Column('weather_main', sa.String(), nullable=True),
    sa.Column('wind_speed', sa.Float(), nullable=True),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('served_from_cache', sa.Boolean(), nullable=True),
    sa.Column('ip_address', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_weather_queries_city_name'), 'weather_queries', ['city_name'], unique=False)
    op.create_index(op.f('ix_weather_queries_timestamp'), 'weather_queries', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_weather_queries_timestamp'), table_name='weather_queries')
    op.drop_index(op.f('ix_weather_queries_city_name'), table_name='weather_queries')
    op.drop_table('weather_queries')