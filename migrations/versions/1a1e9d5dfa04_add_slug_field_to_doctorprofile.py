"""Add slug field to DoctorProfile

Revision ID: 1a1e9d5dfa04
Revises: ce8a91423050
Create Date: 2025-04-18 17:11:41.560595

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from slugify import slugify


# revision identifiers, used by Alembic.
revision = '1a1e9d5dfa04'
down_revision = 'ce8a91423050'
branch_labels = None
depends_on = None


def upgrade():
    # Add column first
    with op.batch_alter_table('doctor_profile', schema=None) as batch_op:
        batch_op.add_column(sa.Column('slug', sa.String(length=150), nullable=True))
        batch_op.create_unique_constraint('uq_doctor_profile_slug', ['slug'])

    # Populate slugs
    bind = op.get_bind()
    session = Session(bind=bind)

    # Reflecting necessary tables
    doctor_profile_table = sa.table(
        'doctor_profile',
        sa.column('id', sa.Integer),
        sa.column('user_id', sa.Integer),
        sa.column('slug', sa.String)
    )

    user_table = sa.table(
        'user',
        sa.column('id', sa.Integer),
        sa.column('username', sa.String)
    )

    # Query doctor profiles with their corresponding user
    doctor_profiles = session.execute(
        sa.select(
            doctor_profile_table.c.id,
            doctor_profile_table.c.user_id,
            user_table.c.username
        ).select_from(
            doctor_profile_table.join(user_table, doctor_profile_table.c.user_id == user_table.c.id)
        )
    ).fetchall()

    for profile in doctor_profiles:
        slug = slugify(f"{profile.username}-{profile.user_id}")
        session.execute(
            doctor_profile_table.update()
            .where(doctor_profile_table.c.id == profile.id)
            .values(slug=slug)
        )

    session.commit()

    # Set slug column to NOT NULL after backfilling
    with op.batch_alter_table('doctor_profile', schema=None) as batch_op:
        batch_op.alter_column('slug', nullable=False)


def downgrade():
    with op.batch_alter_table('doctor_profile', schema=None) as batch_op:
        batch_op.drop_constraint('uq_doctor_profile_slug', type_='unique')
        batch_op.drop_column('slug')
