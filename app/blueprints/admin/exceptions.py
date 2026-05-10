class AdminServiceError(Exception):
    status_code = 500
    default_message = ""
    default_details = ""

    def __init__(self, message=None, details=None):
        self.message = message or self.default_message
        self.details = details or self.default_details
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {self.details}"

    def to_dict(self):
        result = {
                "error": self.message,
                "status_code": self.status_code,
                "details": self.details
        }
        return result


class ProjectCreateError(AdminServiceError):
    default_message = "Something went wrong while trying to create the project, try again"
    default_details = "Failed to create project, DB error"

class ProjectUpdateError(AdminServiceError):
    default_message = "Something went wrong while trying to update the project, try again"
    default_details = "Failed to update project, DB error"

class ProjectDeleteError(AdminServiceError):
    default_message = "Something went wrong while trying to delete the project, try again"
    default_details = "Failed to delete project, DB error"

class ArticleCreateError(AdminServiceError):
    default_message = "Something went wrong while trying to create the article, try again"
    default_details = "Failed to create article, DB error"

class ArticleUpdateError(AdminServiceError):
    default_message = "Something went wrong while trying to update the article, try again"
    default_details = "Failed to update article, DB error"

class ArticleDeleteError(AdminServiceError):
    default_message = "Something went wrong while trying to delete the article, try again"
    default_details = "Failed to delete article, DB error"

class AssetCreateError(AdminServiceError):
    default_message = "Something went wrong while trying to create the asset, try again"
    default_details = "Failed to create asset, DB error"

class AssetUpdateError(AdminServiceError):
    default_message = "Something went wrong while trying to update the asset, try again"
    default_details = "Failed to update asset, DB error"

class TagCreateError(AdminServiceError):
    default_message = "Something went wrong while trying to create the tag, try again"
    default_details = "Failed to create tag, DB error"

class CategoryCreateError(AdminServiceError):
    default_message = "Something went wrong while trying to create the category, try again"
    default_details = "Failed to create category, DB error"
