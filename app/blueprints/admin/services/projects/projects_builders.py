from app.models import Project, ProjectTag, ProjectAsset, ProjectCategory
from flask_login import current_user

def build_project(form_data):
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

def add_project_tags(project, selected_tags):
    if not selected_tags:
        return

    for tag in selected_tags:
        project.project_tags.append(
            ProjectTag(project=project, tag=tag)
        )

def add_project_assets(project, cover_asset, inline_assets, attachment_assets):
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

def add_project_category(project, selected_category):
    if not selected_category:
        return

    project.project_categories.append(
        ProjectCategory(project=project, category=selected_category)
    )
