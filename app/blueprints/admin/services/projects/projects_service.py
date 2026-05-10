from app import db
from app.models import (
                Project
        )

from app.blueprints.admin.exceptions import  (
                ProjectCreateError,
                ProjectDeleteError,
                ProjectUpdateError,
        )

from app.blueprints.admin.services.form_resolvers import ( 
        get_attachment_assets, get_cover_asset, get_inline_assets, get_selected_category, get_selected_tags
        )
from app.blueprints.admin.services.assets.asset_storage import delete_asset_if_unused
from app.blueprints.admin.services.projects.projects_builders import (
        build_project,
        add_project_assets,
        add_project_category,
        add_project_tags
        )

def create_project(form_data) -> Project :
    try:
        project = build_project(form_data)
        selected_category = get_selected_category(form_data)
        selected_tags = get_selected_tags(form_data)
        cover_asset = get_cover_asset(form_data)
        inline_assets = get_inline_assets(form_data)
        attachment_assets = get_attachment_assets(form_data)

        db.session.add(project)
        db.session.flush()

        add_project_category(project, selected_category)
        add_project_tags(project, selected_tags)
        add_project_assets(project, cover_asset, inline_assets, attachment_assets)

        db.session.commit()

        return project

    except Exception:
        db.session.rollback()
        raise ProjectCreateError()

def update_project(project, form_data):
    try:
        selected_category = get_selected_category(form_data)
        selected_tags = get_selected_tags(form_data)
        cover_asset = get_cover_asset(form_data)
        attachment_assets = get_attachment_assets(form_data)
        inline_assets = get_inline_assets(form_data)

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

        add_project_category(project, selected_category)
        add_project_tags(project, selected_tags)
        add_project_assets(project, cover_asset,inline_assets, attachment_assets)

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
            delete_asset_if_unused(asset)

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise ProjectDeleteError()
