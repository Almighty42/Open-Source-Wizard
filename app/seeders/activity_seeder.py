import random
from faker import Faker
from datetime import timedelta

from sqlalchemy.engine import create
from app.models import activity
from app.models.activity import Activity, ActorType, SubjectType, ActivityStatus
from app.models import User, Article, Project, Tag, Category, Asset
from app.extensions import db
from app.seeders.base import BaseSeeder

from app.models.activity import EventType
import inspect

fake = Faker()
Faker.seed(42)

# Maps which subject types are valid for each event
EVENT_SUBJECT_MAP = {
        EventType.login: (None, None),
        EventType.logout: (None, None),
        EventType.login_failed: (None, None),
        EventType.locked_out: (None, None),
        EventType.created: (SubjectType.article, SubjectType.project, SubjectType.tag, SubjectType.category, SubjectType.asset),
        EventType.updated: (SubjectType.article, SubjectType.project, SubjectType.tag, SubjectType.category),
        EventType.deleted: (SubjectType.article, SubjectType.project, SubjectType.asset),
        EventType.published: (SubjectType.article, SubjectType.project),
        EventType.archived: (SubjectType.article, SubjectType.project)
}

# Human-readable messages per event
EVENT_MESSAGES = {
        EventType.login: lambda u, s, sid: f"{u} logged in",
        EventType.logout: lambda u, s, sid: f"{u} logged out",
        EventType.login_failed: lambda u, s, sid: f"Failed login attempt for '{u}'",
        EventType.locked_out: lambda u, s, sid: f"Account '{u}' locked out after repeated failures",
        EventType.created: lambda u, s, sid: f"{u} created {s.value} #{sid}",
        EventType.updated: lambda u, s, sid: f"{u} updated {s.value} #{sid}",
        EventType.deleted: lambda u, s, sid: f"{u} deleted {s.value} #{sid}",
        EventType.published: lambda u, s, sid: f"{u} published {s.value} #{sid}",
        EventType.archived: lambda u, s, sid: f"{u} archived {s.value} #{sid}",
}

def fake_payload(event: EventType, subject_type: SubjectType, subject_id) -> dict | None:
    base = {
            "ip": fake.ipv4(),
            "user-agent": fake.user_agent(),
    }
    if event == EventType.login_failed:
        return { **base, "attempt": random.randint(1, 5) }
    if event == EventType.locked_out:
        return { **base, "locked_until": (fake.date_time_this_month()).isoformat() }
    if event == EventType.updated:
        return { **base,
                "changed_fields": random.sample(
                    ["title", "body", "status", "excerpt", "slug", "seo_title", "seo_description"],
                    k=random.randint(1, 3)
                    )
        }
    if event in (EventType.published, EventType.archived):
        return { **base, "previous_status": "draft" }
    if event in (EventType.created, EventType.deleted):
        return base
    return base

def _subject_ids(subject_type: SubjectType) -> list[int]:
    model_map = {
            SubjectType.article: Article,
            SubjectType.project: Project,
            SubjectType.tag: Tag,
            SubjectType.category: Category,
            SubjectType.asset: Asset,
            SubjectType.user: User,
    }
    model = model_map.get(subject_type)
    if not model:
        return []
    return [row.id for row in db.session.query(model.id).all()]

class ActivitySeeder(BaseSeeder):
    def __init__(self, count: int = 40):
        self.count = count
    def run(self):
        users = db.session.query(User).all()
        if not users:
            print("[ActivitySeeder] No users found. Run UserSeeder first")
            return
        created = 0
        now = fake.date_time_this_year()
        for i in range(self.count):
            user = random.choice(users)
            event = random.choice(list(EventType))
            subject_options = EVENT_SUBJECT_MAP[event]

            # Auth events have no subject
            if subject_options == (None, None):
                subject_type = None
                subject_id = None
            else:
                subject_type = random.choice(subject_options)
                ids = _subject_ids(subject_type)
                subject_id = random.choice(ids) if ids else None
            # Spread timestamps over last 90 days
            created_at = fake.date_time_between(
                    start_date="-90d",
                    end_date="now"
            )
            # Auth failures always fail, the rest mostly succedes
            if event in (EventType.login_failed, EventType.locked_out):
                status = ActivityStatus.failure
            else:
                status = random.choices(
                        [ActivityStatus.success, ActivityStatus.failure],
                        weights=[90, 10]
                )[0]
            message = EVENT_MESSAGES[event](
                    user.username,
                    subject_type,
                    subject_id
            )

            activity = Activity(
                    event_type=event,
                    actor_type=ActorType.user,
                    actor_id=user.id,
                    subject_type=subject_type,
                    subject_id=subject_id,
                    message=message,
                    payload=fake_payload(event, subject_type, subject_id),
                    status=status,
                    created_at=created_at,
                    request_id=fake.uuid4(),
            )
            db.session.add(activity)
            created += 1
        db.session.commit()
        print(f"[ActivitySeeder] {created} activity records created.")
