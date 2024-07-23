"""add game number

Revision ID: 45c62920b76f
Revises: d3975461e626
Create Date: 2024-07-20 21:47:20.619855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

# revision identifiers, used by Alembic.
revision: str = '45c62920b76f'
down_revision: Union[str, None] = 'd3975461e626'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('game', sa.Column('game_number', sa.Integer(), nullable=False))
    op.drop_column("tournament", "queue_id")
    op.drop_table("match_queue")
    op.drop_column("user", "contact_inf")

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('game', 'game_number')
    op.create_table('match_queue',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column("tournament", sa.Column("queue_id", sa.UUID(), autoincrement=False, nullable=False))
    op.create_foreign_key("queue_id", "tournament", "match_queue", ["queue_id"], ["id"])
    op.add_column("user", sa.Column("contact_inf", sa.String(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
