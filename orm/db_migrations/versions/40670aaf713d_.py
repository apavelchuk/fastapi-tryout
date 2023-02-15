"""empty message

Revision ID: 40670aaf713d
Revises:
Create Date: 2021-11-02 14:40:53.831726

"""
import sqlalchemy as sa
import sqlalchemy_utils

from alembic import op


# revision identifiers, used by Alembic.
revision = "40670aaf713d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=75), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user")
    # ### end Alembic commands ###