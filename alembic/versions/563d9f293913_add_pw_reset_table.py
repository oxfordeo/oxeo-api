"""Add PW Reset table

Revision ID: 563d9f293913
Revises: 41920631e9ea
Create Date: 2022-06-16 15:12:27.288802

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "563d9f293913"
down_revision = "41920631e9ea"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("reset_token", sa.String(), nullable=True),
        sa.Column("status", sa.Boolean(), nullable=True),
        sa.Column("create_datetime", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_password_reset_tokens_email"),
        "password_reset_tokens",
        ["email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_password_reset_tokens_id"),
        "password_reset_tokens",
        ["id"],
        unique=False,
    )
    # op.drop_table('spatial_ref_sys')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256),
    #    autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048),
    #    autoincrement=False, nullable=True),
    # sa.CheckConstraint('(srid > 0) AND (srid <= 998999)',
    #    name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    op.drop_index(
        op.f("ix_password_reset_tokens_id"), table_name="password_reset_tokens"
    )
    op.drop_index(
        op.f("ix_password_reset_tokens_email"), table_name="password_reset_tokens"
    )
    op.drop_table("password_reset_tokens")
    # ### end Alembic commands ###
