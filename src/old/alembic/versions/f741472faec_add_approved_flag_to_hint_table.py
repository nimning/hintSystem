"""Add approved flag to hint table

Revision ID: f741472faec
Revises: None
Create Date: 2014-07-16 20:17:46.805047

"""

# revision identifiers, used by Alembic.
revision = 'f741472faec'
down_revision = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    context = op.get_context()
    course_name = context.opts.get('course_name')
    hint_table = "{0}_hint".format(course_name)
    op.add_column(hint_table, sa.Column('approved', sa.Boolean,
                                        nullable=False, server_default='0'))

def downgrade():
    context = op.get_context()
    course_name = context.opts.get('course_name')
    hint_table = "{0}_hint".format(course_name)
    op.drop_column(hint_table, 'approved')
