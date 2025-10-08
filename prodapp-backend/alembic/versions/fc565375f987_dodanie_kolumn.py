"""dodanie_kolumn

Revision ID: fc565375f987
Revises: 
Create Date: 2025-08-26 21:14:18.824097

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc565375f987'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Dodajemy kolumny jako nullable=True
    op.add_column('zlecenia', sa.Column('indeks', sa.String(), nullable=True))
    op.add_column('zlecenia', sa.Column('sztuk', sa.Integer(), nullable=True))
    op.add_column('zlecenia', sa.Column('deadline', sa.Date(), nullable=True))
    op.add_column('zlecenia', sa.Column('kontrakt', sa.String(), nullable=True))
    op.add_column('zlecenia', sa.Column('zl_klienta', sa.String(), nullable=True))
    op.add_column('zlecenia', sa.Column('liczba_elementow', sa.Integer(), nullable=True))
    op.add_column('zlecenia', sa.Column('waga_szt', sa.Float(), nullable=True))

    # 2. Uzupełniamy istniejące rekordy domyślnymi wartościami
    op.execute("UPDATE zlecenia SET indeks = '' WHERE indeks IS NULL")
    op.execute("UPDATE zlecenia SET sztuk = 0 WHERE sztuk IS NULL")
    op.execute("UPDATE zlecenia SET deadline = NOW() WHERE deadline IS NULL")
    op.execute("UPDATE zlecenia SET kontrakt = '' WHERE kontrakt IS NULL")
    op.execute("UPDATE zlecenia SET zl_klienta = '' WHERE zl_klienta IS NULL")
    op.execute("UPDATE zlecenia SET liczba_elementow = 0 WHERE liczba_elementow IS NULL")
    op.execute("UPDATE zlecenia SET waga_szt = 0 WHERE waga_szt IS NULL")

    # 3. Ustawiamy NOT NULL
    op.alter_column('zlecenia', 'indeks', nullable=False)
    op.alter_column('zlecenia', 'sztuk', nullable=False)
    op.alter_column('zlecenia', 'deadline', nullable=False)
    op.alter_column('zlecenia', 'kontrakt', nullable=False)
    op.alter_column('zlecenia', 'zl_klienta', nullable=False)
    op.alter_column('zlecenia', 'liczba_elementow', nullable=False)
    op.alter_column('zlecenia', 'waga_szt', nullable=False)


def downgrade():
    op.drop_column('zlecenia', 'waga_szt')
    op.drop_column('zlecenia', 'liczba_elementow')
    op.drop_column('zlecenia', 'zl_klienta')
    op.drop_column('zlecenia', 'kontrakt')
    op.drop_column('zlecenia', 'deadline')
    op.drop_column('zlecenia', 'sztuk')
    op.drop_column('zlecenia', 'indeks')