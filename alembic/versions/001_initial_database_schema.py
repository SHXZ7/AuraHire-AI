"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-09-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create resumes table
    op.create_table('resumes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('candidate_name', sa.String(length=255), nullable=True),
        sa.Column('emails', sa.JSON(), nullable=True),
        sa.Column('phones', sa.JSON(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('education', sa.JSON(), nullable=True),
        sa.Column('sections', sa.JSON(), nullable=True),
        sa.Column('total_characters', sa.Integer(), nullable=True),
        sa.Column('total_words', sa.Integer(), nullable=True),
        sa.Column('total_lines', sa.Integer(), nullable=True),
        sa.Column('skills_count', sa.Integer(), nullable=True),
        sa.Column('education_count', sa.Integer(), nullable=True),
        sa.Column('certifications_count', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resumes_id'), 'resumes', ['id'], unique=False)

    # Create job_descriptions table
    op.create_table('job_descriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('job_type', sa.String(length=50), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('cleaned_text', sa.Text(), nullable=True),
        sa.Column('role', sa.String(length=255), nullable=True),
        sa.Column('must_have_skills', sa.JSON(), nullable=True),
        sa.Column('nice_to_have_skills', sa.JSON(), nullable=True),
        sa.Column('qualifications', sa.JSON(), nullable=True),
        sa.Column('experience_required', sa.String(length=100), nullable=True),
        sa.Column('sections', sa.JSON(), nullable=True),
        sa.Column('total_characters', sa.Integer(), nullable=True),
        sa.Column('total_words', sa.Integer(), nullable=True),
        sa.Column('total_lines', sa.Integer(), nullable=True),
        sa.Column('must_have_skills_count', sa.Integer(), nullable=True),
        sa.Column('nice_to_have_skills_count', sa.Integer(), nullable=True),
        sa.Column('qualifications_count', sa.Integer(), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('job_url', sa.String(length=500), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_descriptions_id'), 'job_descriptions', ['id'], unique=False)

    # Create match_results table
    op.create_table('match_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('job_description_id', sa.Integer(), nullable=False),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('hard_score', sa.Float(), nullable=False),
        sa.Column('soft_score', sa.Float(), nullable=False),
        sa.Column('verdict', sa.String(length=50), nullable=False),
        sa.Column('hard_weight', sa.Float(), nullable=True),
        sa.Column('soft_weight', sa.Float(), nullable=True),
        sa.Column('matched_skills', sa.JSON(), nullable=True),
        sa.Column('missing_skills', sa.JSON(), nullable=True),
        sa.Column('extracted_resume_skills', sa.JSON(), nullable=True),
        sa.Column('common_keywords', sa.JSON(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column('algorithm_version', sa.String(length=50), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('skill_gap_analysis', sa.JSON(), nullable=True),
        sa.Column('improvement_suggestions', sa.JSON(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('is_bookmarked', sa.Boolean(), nullable=True),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('matched_by', sa.String(length=255), nullable=True),
        sa.Column('match_context', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['job_description_id'], ['job_descriptions.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_match_results_id'), 'match_results', ['id'], unique=False)

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('endpoint', sa.String(length=255), nullable=True),
        sa.Column('http_method', sa.String(length=10), nullable=True),
        sa.Column('request_params', sa.JSON(), nullable=True),
        sa.Column('request_body_hash', sa.String(length=64), nullable=True),
        sa.Column('response_status', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processing_details', sa.JSON(), nullable=True),
        sa.Column('file_details', sa.JSON(), nullable=True),
        sa.Column('business_event', sa.String(length=255), nullable=True),
        sa.Column('correlation_id', sa.String(length=255), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changed_fields', sa.JSON(), nullable=True),
        sa.Column('server_instance', sa.String(length=100), nullable=True),
        sa.Column('api_version', sa.String(length=20), nullable=True),
        sa.Column('client_version', sa.String(length=20), nullable=True),
        sa.Column('data_classification', sa.String(length=50), nullable=True),
        sa.Column('retention_policy', sa.String(length=50), nullable=True),
        sa.Column('compliance_flags', sa.JSON(), nullable=True),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_match_results_id'), table_name='match_results')
    op.drop_table('match_results')
    op.drop_index(op.f('ix_job_descriptions_id'), table_name='job_descriptions')
    op.drop_table('job_descriptions')
    op.drop_index(op.f('ix_resumes_id'), table_name='resumes')
    op.drop_table('resumes')