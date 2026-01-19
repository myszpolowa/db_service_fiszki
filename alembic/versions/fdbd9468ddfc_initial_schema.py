"""initial_schema

Revision ID: fdbd9468ddfc
Revises:
Create Date: 2026-01-15 10:20:32.413903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdbd9468ddfc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admins table
    op.create_table(
        'admins',
        sa.Column('id_admin', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id_admin'),
        sa.UniqueConstraint('login')
    )
    op.create_index(op.f('ix_admins_id_admin'), 'admins', ['id_admin'], unique=False)

    # Create levels table
    op.create_table(
        'levels',
        sa.Column('level_id', sa.Integer(), nullable=False),
        sa.Column('level_name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('level_id'),
        sa.UniqueConstraint('level_name')
    )
    op.create_index(op.f('ix_levels_level_id'), 'levels', ['level_id'], unique=False)

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('login', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('login')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)

    # Create questions table (depends on levels)
    op.create_table(
        'questions',
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(), nullable=False),
        sa.Column('level_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['level_id'], ['levels.level_id'], ),
        sa.PrimaryKeyConstraint('question_id')
    )
    op.create_index(op.f('ix_questions_question_id'), 'questions', ['question_id'], unique=False)

    # Create answers table (depends on questions)
    op.create_table(
        'answers',
        sa.Column('answer_id', sa.Integer(), nullable=False),
        sa.Column('answer', sa.String(), nullable=False),
        sa.Column('is_good', sa.Integer(), nullable=True),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['questions.question_id'], ),
        sa.PrimaryKeyConstraint('answer_id')
    )
    op.create_index(op.f('ix_answers_answer_id'), 'answers', ['answer_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order (respect foreign keys)
    op.drop_index(op.f('ix_answers_answer_id'), table_name='answers')
    op.drop_table('answers')

    op.drop_index(op.f('ix_questions_question_id'), table_name='questions')
    op.drop_table('questions')

    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_levels_level_id'), table_name='levels')
    op.drop_table('levels')

    op.drop_index(op.f('ix_admins_id_admin'), table_name='admins')
    op.drop_table('admins')
