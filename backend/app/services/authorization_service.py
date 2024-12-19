from flask import current_app
from app.extensions import db
from app.models import SecurityRole, Authorization, Resource, Action, user_securityroles, securityrole_authorizations

def get_user_authorizations(user_id, org_id, resources=None):
    """
    Retrieves all authorizations for the specified user and organization, or for specific resources if provided.

    Args:
        user_id (str): ID of the logged-in user.
        org_id (str): ID of the organization the user belongs to.
        resources (list, optional): List of resource names to filter the authorizations (e.g., ['StudentGroup', 'Quiz']).

    Returns:
        dict: Dictionary with resources as keys and authorization actions as values.
    """
    try:
        # Fetch the user's roles, explicitly joining the user_securityroles table
        roles = (
            db.session.query(SecurityRole)
            .join(user_securityroles, user_securityroles.c.securityrole_id == SecurityRole.id)
            .filter(user_securityroles.c.user_id == user_id, SecurityRole.org_id == org_id)
            .all()
        )

        # Fetch the list of resources (filter by provided resources if any)
        if resources:
            resource_records = Resource.query.filter(Resource.name.in_(resources)).all()
        else:
            resource_records = Resource.query.all()

        # Prepare the result dictionary
        result = {}

        # Loop through each resource and determine the user's actions (permissions)
        for resource in resource_records:
            resource_permissions = {}

            # Fetch authorizations for each resource based on the user's roles
            authorizations = (
                Authorization.query
                .join(securityrole_authorizations, securityrole_authorizations.c.authorization_id == Authorization.id)
                .join(SecurityRole, SecurityRole.id == securityrole_authorizations.c.securityrole_id)
                .filter(SecurityRole.id.in_([role.id for role in roles]), Authorization.resource_id == resource.id)
                .all()
            )

            for auth in authorizations:
                action = Action.query.get(auth.action_id)
                resource_permissions[action.name] = True

            # Add the resource's permissions to the result
            result[resource.name] = resource_permissions

        return result
    except Exception as e:
        # Log the error and re-raise it to be handled by the caller
        current_app.logger.error(f"Error in get_user_authorizations: {str(e)}")
        raise
