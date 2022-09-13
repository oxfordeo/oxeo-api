"""add tp to event labels

Revision ID: 1888633ebdd1
Revises: 563d9f293913
Create Date: 2022-09-13 15:31:42.984473

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "1888633ebdd1"
down_revision = "563d9f293913"
branch_labels = None
depends_on = None

# note: https://medium.com/makimo-tech-blog/upgrading-postgresqls-enum-type-with-sqlalchemy-using-alembic-migration-881af1e30abe   # noqa


def upgrade() -> None:

    with op.get_context().autocommit_block():
        op.execute("""ALTER TYPE "EventLabel" ADD VALUE 'total_precipitation'""")


def downgrade() -> None:

    op.execute("""ALTER TYPE "EventLabel" RENAME TO "EventLabelOld" """)
    op.execute(
        """CREATE TYPE "EventLabel" AS ENUM('ndvi','water_extents','soil_moisture','prediction')"""  # noqa
    )
    op.execute(
        """ALTER TABLE "events" ALTER COLUMN "labels" TYPE "EventLabel" USING """
        """ "labels"::text::"EventLabel" """
    )
    op.execute("""DROP TYPE "EventLabelOld" """)
