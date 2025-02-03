# models.py
import uuid
import enum
from sqlalchemy import (
    Column,
    String,
    Boolean,
    Text,
    DateTime,
    func,
    ForeignKey,
    Enum as SQLAEnum,
    event,
    DDL,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# --- Table: upload_details ---
class UploadDetails(Base):
    __tablename__ = "upload_details"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String, unique=True, nullable=False)
    # define other columns as needed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# --- Table: ai_assess_complaints ---
class AIAssessComplaints(Base):
    __tablename__ = "ai_assess_complaints"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Note: The foreign key is to upload_details.contact_id.
    contact_id = Column(String, ForeignKey("public.upload_details.contact_id"), nullable=False)
    physical_disability_flag = Column(Boolean, nullable=False, default=False)
    complaints_flag = Column(Boolean, nullable=False, default=False)
    physical_disability_reasoning = Column(Text)
    complaints_reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    relevant_snippet_ids = Column(ARRAY(String), default=list)
    complaints_list = Column(ARRAY(String), default=list)
    overall_summary = Column(Text)
    detailed_summary_points = Column(ARRAY(String), default=list)


# --- Table: ai_assess_vulnerability ---
class AIAssessVulnerability(Base):
    __tablename__ = "ai_assess_vulnerability"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String, ForeignKey("public.upload_details.contact_id"), nullable=False)
    vulnerability_flag = Column(Boolean, nullable=False, default=False)
    vulnerability_reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    relevant_snippet_ids = Column(ARRAY(String), default=list)
    vulnerabilities_list = Column(ARRAY(String), default=list)


# --- Table: contact_assessments ---
class ContactAssessments(Base):
    __tablename__ = "contact_assessments"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String, ForeignKey("public.upload_details.contact_id"), nullable=False)
    has_physical_disability = Column(Boolean, default=False)
    complaints = Column(ARRAY(String), default=list)
    vulnerabilities = Column(ARRAY(String), default=list)
    complaints_rationale = Column(Text)
    vulnerability_rationale = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# --- Table: contact_conversations ---
class ContactConversations(Base):
    __tablename__ = "contact_conversations"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String, ForeignKey("public.upload_details.contact_id"), nullable=False)
    transcript = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    snippets_metadata = Column(JSONB, default=list)


# --- Table: quality_assessor_feedback ---
class QualityAssessorFeedback(Base):
    __tablename__ = "quality_assessor_feedback"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id = Column(String, ForeignKey("public.upload_details.contact_id"), nullable=False)
    evaluator = Column(String, nullable=False)
    complaints_flag = Column(Boolean, nullable=False, default=False)
    vulnerability_flag = Column(Boolean, nullable=False, default=False)
    complaints_reasoning = Column(Text)
    vulnerability_reasoning = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


# --- Table: user_roles ---
# Define the ENUM type for roles.
class AppRole(enum.Enum):
    admin = "admin"
    user = "user"


class UserRoles(Base):
    __tablename__ = "user_roles"
    __table_args__ = {"schema": "public"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Note: The "auth.users" table should exist.
    user_id = Column(UUID(as_uuid=True), ForeignKey("auth.users.id"))
    role = Column(SQLAEnum(AppRole, name="app_role"), nullable=False, default=AppRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class AuthUsers(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}
    id = Column(UUID(as_uuid=True), primary_key=True)
    # define other columns as needed
    username = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# --- Create the view: conversation_snippets_view ---
# SQLAlchemy does not have built-in view support, but we can issue a DDL event.
view_ddl = DDL(
    """
    CREATE OR REPLACE VIEW public.conversation_snippets_view AS
    SELECT 
        contact_id,
        jsonb_array_elements(snippets_metadata) as snippet
    FROM public.contact_conversations;
    """
)

# We attach the view DDL to the ContactConversations table after creation.
event.listen(ContactConversations.__table__, "after_create", view_ddl)
