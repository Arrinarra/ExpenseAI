"""add indexes for analytics

Revision ID: 779560de4538
Revises: e73e1dd85c49
Create Date: 2026-04-07 12:52:48.888946

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "779560de4538"
down_revision: Union[str, Sequence[str], None] = "e73e1dd85c49"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_index('ix_transactions_user_id_date', 'transactions', ['user_id', 'date'])
    op.create_index('ix_transactions_category_id', 'transactions', ['category_id'])

def downgrade():
    op.drop_index('ix_transactions_category_id', table_name='transactions')
    op.drop_index('ix_transactions_user_id_date', table_name='transactions')