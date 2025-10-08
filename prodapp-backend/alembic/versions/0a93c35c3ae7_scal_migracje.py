"""Scal migracje

Revision ID: 0a93c35c3ae7
Revises: bc43772a5ad8, dodaj_id_zlecenia_do_obecnosci
Create Date: 2025-10-04 20:19:44.861842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a93c35c3ae7'
down_revision: Union[str, Sequence[str], None] = ('bc43772a5ad8', 'dodaj_id_zlecenia_do_obecnosci')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
