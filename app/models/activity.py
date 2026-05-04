from enum import Enum
from datetime import datetime
from app.utils import utc_now
from app.extensions import db
import sqlalchemy as sql
import sqlalchemy.orm as orm

class EventType(str, Enum):
    # Auth
    login           = "login"
    logout          = "logout"
    login_failed    = "login_failed"
    locked_out      = "locked_out"
    # Content
    created         = "created"
    updated         = "updated"
    deleted         = "deleted"
    published       = "published"
    archived        = "archived"

class ActorType(str, Enum):
    user    = "user"
    system  = "system"
    cli     = "cli"

class SubjectType(str, Enum):
    article = "article"
    project = "project"
    tag     = "tag"
    category = "category"
    asset   = "asset"
    user    = "user"

class ActivityStatus(str, Enum):
    success = "success"
    failure = "failure"

class Activity(db.Model):
    __tablename__ = "activities"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    event_type: orm.Mapped[EventType] = orm.mapped_column(sql.Enum(EventType, name="activity_event_type"), nullable=False, index=True)
    actor_type: orm.Mapped[ActorType] = orm.mapped_column(sql.Enum(ActorType, name="activity_actor_type"), nullable=False)
    actor_id: orm.Mapped[int | None] = orm.mapped_column(nullable=True)
    subject_type: orm.Mapped[SubjectType | None] = orm.mapped_column(sql.Enum(SubjectType, name="activity_subject_type"),nullable=True)
    subject_id: orm.Mapped[int | None] = orm.mapped_column(nullable=True)
    message: orm.Mapped[str | None] = orm.mapped_column(sql.String(256), nullable=True)
    payload: orm.Mapped[dict | None] = orm.mapped_column(sql.JSON, nullable=True)
    status: orm.Mapped[ActivityStatus] = orm.mapped_column(sql.Enum(ActivityStatus, name="activity_status"),nullable=False,index=True)
    created_at: orm.Mapped[datetime] = orm.mapped_column(sql.DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    request_id: orm.Mapped[str | None] = orm.mapped_column(sql.String(64), nullable=True, index=True)

# EXAMPLE USAGE
# Activity(
#     event_type=EventType.login_failed,
#     actor_type=ActorType.user,
#     actor_id=user.id,
#     subject_type=None,
#     subject_id=None,
#     status=ActivityStatus.failure,
#     message="Invalid password",
#     payload={
#         "ip": request.remote_addr,
#         "user_agent": request.user_agent.string,
#         "attempt": user.login_attempts,
#     }
# )
