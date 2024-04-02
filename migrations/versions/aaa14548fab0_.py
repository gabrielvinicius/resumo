"""empty message

Revision ID: aaa14548fab0
Revises: 156d8c2804ee
Create Date: 2024-04-02 00:32:35.894071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aaa14548fab0'
down_revision = '156d8c2804ee'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.add_column(sa.Column('audio_path', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('video', schema=None) as batch_op:
        batch_op.drop_column('audio_path')

    # ### end Alembic commands ###
