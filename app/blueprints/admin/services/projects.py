from app import db
from app.blueprints.admin.services.common import \
        (
                _get_selected_category,
                _get_selected_tags,
                _get_cover_asset,
                _get_inline_assets,
                _get_attachment_assets
        )
from app.models import \
        (
                Project, 
                ProjectTag, 
                ProjectAsset, 
                ProjectCategory
        )

from app.blueprints.admin.exceptions import  \
        (
                ProjectCreateError,
                ProjectDeleteError,
                ProjectUpdateError,
        )

# NOTE: Main functions
def create_project(form_data) -> Project :
    try:
        project = _build_project(form_data)
        selected_category = _get_selected_category(form_data)
        selected_tags = _get_selected_tags(form_data)
        cover_asset = _get_cover_asset(form_data)
        inline_assets = _get_inline_assets(form_data)
        attachment_assets = _get_attachment_assets(form_data)

        db.session.add(project)
        db.session.flush()

        _add_project_category(project, selected_category)
        _add_project_tags(project, selected_tags)
        _add_project_assets(project, cover_asset, inline_assets, attachment_assets)

        db.session.commit()

        return project

    except Exception:
        db.session.rollback()
        raise ProjectCreateError()

def update_project(project, form_data):
    try:
        selected_category = common._get_selected_category(form_data)
        selected_tags = common._get_selected_tags(form_data)
        cover_asset = common._get_cover_asset(form_data)
        attachment_assets = common._get_attachment_assets(form_data)
        inline_assets = common._get_inline_assets(form_data)

        project.title = form_data.title.data.strip()
        project.slug = form_data.slug.data.strip()
        project.status = form_data.status.data
        project.project_state = form_data.project_state.data
        project.platform = form_data.platform.data.strip() if form_data.platform.data else None
        project.repo_url = form_data.repo_url.data.strip() if form_data.repo_url.data else None
        project.demo_url = form_data.demo_url.data.strip() if form_data.demo_url.data else None
        project.is_featured = bool(form_data.is_featured.data)

        project.excerpt = form_data.excerpt.data.strip()
        project.body = form_data.body.data

        project.published_at = form_data.published_at.data or None
        project.started_at = form_data.started_at.data or None
        project.completed_at = form_data.completed_at.data or None

        project.seo_title = form_data.title.data.strip()
        project.seo_description = form_data.excerpt.data.strip()

        project.project_categories.clear()
        project.project_tags.clear()
        project.project_assets.clear()

        _add_project_category(project, selected_category)
        _add_project_tags(project, selected_tags)
        _add_project_assets(project, cover_asset,inline_assets, attachment_assets)

        db.session.commit()
        return project

    except Exception:
        db.session.rollback()
        raise ProjectUpdateError()

def remove_project(project) -> None:
    try:
        linked_assets = [pa.asset for pa in project.project_assets]

        db.session.delete(project)
        db.session.flush()

        for asset in linked_assets:
            common._delete_asset_if_unused(asset)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise ProjectDeleteError()

# NOTE: Helper Functions
def _build_project(form_data):
    return Project(
        title=form_data.title.data.strip(),
        slug=form_data.slug.data.strip(),
        status=form_data.status.data,
        project_state=form_data.project_state.data,
        platform=form_data.platform.data.strip() if form_data.platform.data else None,
        repo_url=form_data.repo_url.data.strip() if form_data.repo_url.data else None,
        demo_url=form_data.demo_url.data.strip() if form_data.demo_url.data else None,
        is_featured=bool(form_data.is_featured.data),
        excerpt=form_data.excerpt.data.strip(),
        body=form_data.body.data,
        published_at=form_data.published_at.data or None,
        started_at=form_data.started_at.data or None,
        completed_at=form_data.completed_at.data or None,
        author_id=current_user.id,
        seo_title=form_data.title.data.strip(),
        seo_description=form_data.excerpt.data.strip(),
    )

def _add_project_tags(project, selected_tags):
    if not selected_tags:
        return

    for tag in selected_tags:
        project.project_tags.append(
            ProjectTag(project=project, tag=tag)
        )

def _add_project_assets(project, cover_asset, inline_assets, attachment_assets):
    used_asset_ids = set()

    if cover_asset:
        project.project_assets.append(
            ProjectAsset(
                project=project,
                asset=cover_asset,
                is_cover=True,
                role="cover",
            )
        )
        used_asset_ids.add(cover_asset.id)

    for asset in inline_assets:
        if asset.id in used_asset_ids:
            continue

        project.project_assets.append(
            ProjectAsset(
                project=project,
                asset=asset,
                is_cover=False,
                role="inline",
            )
        )
        used_asset_ids.add(asset.id)

    for asset in attachment_assets:
        if asset.id in used_asset_ids:
            continue

        project.project_assets.append(
            ProjectAsset(
                project=project,
                asset=asset,
                is_cover=False,
                role="attachment",
            )
        )
        used_asset_ids.add(asset.id)

def _add_project_category(project, selected_category):
    if not selected_category:
        return

    project.project_categories.append(
        ProjectCategory(project=project, category=selected_category)
    )
