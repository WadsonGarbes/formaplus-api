"""empty message

Revision ID: dc38bc5fadc7
Revises: 
Create Date: 2022-08-20 17:31:44.906346

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc38bc5fadc7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('first_seen', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=1024), nullable=False),
    sa.Column('answer', sa.String(length=512), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_timestamp'), 'questions', ['timestamp'], unique=False)
    op.create_index(op.f('ix_questions_user_id'), 'questions', ['user_id'], unique=False)
    op.create_table('tokens',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('access_token', sa.String(length=64), nullable=False),
    sa.Column('access_expiration', sa.DateTime(), nullable=False),
    sa.Column('refresh_token', sa.String(length=64), nullable=False),
    sa.Column('refresh_expiration', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tokens_access_token'), 'tokens', ['access_token'], unique=False)
    op.create_index(op.f('ix_tokens_refresh_token'), 'tokens', ['refresh_token'], unique=False)
    op.create_index(op.f('ix_tokens_user_id'), 'tokens', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tokens_user_id'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_refresh_token'), table_name='tokens')
    op.drop_index(op.f('ix_tokens_access_token'), table_name='tokens')
    op.drop_table('tokens')
    op.drop_index(op.f('ix_questions_user_id'), table_name='questions')
    op.drop_index(op.f('ix_questions_timestamp'), table_name='questions')
    op.drop_table('questions')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
