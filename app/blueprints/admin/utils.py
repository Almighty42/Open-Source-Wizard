def build_category_choices(categories):
    return [("", "Select category")] + [
        (category.slug, category.name) for category in categories
    ]

def build_tag_choices(tags):
    return [
        (tag.slug, tag.name) for tag in tags
    ]

def build_cover_asset_choices(assets):
    return [(None, "No cover")] + [
        (asset.id, asset.path) for asset in assets
    ]

def build_attachment_asset_choices(assets):
    return [
        (asset.id, asset.path) for asset in assets
    ]

def build_inline_asset_choices(assets):
    return [
        (asset.id, asset.path) for asset in assets
    ]

