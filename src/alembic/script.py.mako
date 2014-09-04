"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${create_date}

"""

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

def upgrade():
    context = op.get_context()
    course_name = context.opts.get('course_name')
    ${upgrades if upgrades else "pass"}


def downgrade():
    context = op.get_context()
    course_name = context.opts.get('course_name')
    ${downgrades if downgrades else "pass"}
