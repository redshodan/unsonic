"""Added user folders

Revision ID: 2fd8e4ce261c
Revises: 33bb0c204f1e
Create Date: 2018-12-26 07:14:46.955048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fd8e4ce261c'
down_revision = '33bb0c204f1e'
branch_labels = None
depends_on = None


def upgrade():
    # UserFolder
    op.create_table(
        'un_userfolders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('lib_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['un_users.id'],
                                name=op.f('fk_un_userfolders_user_id_un_users'),
                                ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lib_id'], ['libraries.id'],
                                name=op.f('fk_un_userfolders_lib_id_libraries'),
                                ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_un_userfolders'))
    )
    op.create_index('userfolders_user_index', 'un_userfolders', ['user_id'],
                    unique=False)


def downgrade():
    op.drop_index('userfolders_user_index', table_name='un_userfolders')
    op.drop_table('un_userfolders')
