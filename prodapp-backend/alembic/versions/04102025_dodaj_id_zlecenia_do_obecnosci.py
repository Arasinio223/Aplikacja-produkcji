"""dodaj id_zlecenia do obecnosci

Revision ID: dodaj_id_zlecenia_do_obecnosci
Revises: <poprzedni_revision_id>
Create Date: 2025-10-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'dodaj_id_zlecenia_do_obecnosci'
down_revision = 'fc565375f987'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('obecnosci', sa.Column('id_zlecenia', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_obecnosci_id_zlecenia',
        'obecnosci', 'zlecenia',
        ['id_zlecenia'], ['id_zlecenia'],
        ondelete='SET NULL'
    )

def downgrade():
    op.drop_constraint('fk_obecnosci_id_zlecenia', 'obecnosci', type_='foreignkey')
    op.drop_column('obecnosci', 'id_zlecenia')