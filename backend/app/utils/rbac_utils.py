# utils/rbac_utils.py
#from app.utils.logging_config import app_logger, security_logger
from flask import current_app
from flask_jwt_extended import get_jwt

JWT_KEY_ORG_ID = 'org_id'
JWT_KEY_ROLES = 'roles'
JWT_KEY_SUB = 'sub'
JWT_KEY_PERMISSIONS = 'permissions'

def get_user_permissions(org_id, user_id):
    from app import db
    from app.models import Authorization, Resource, Action, SecurityRole, User, Organization, user_securityroles, securityrole_authorizations
    # A function to fetch all authorizations/permissions the user has.
    try:
        user_permissions_query = db.session.query(Action.name.label('action'), Resource.name.label('resource')) \
            .join(Authorization, Action.id == Authorization.action_id) \
            .join(Resource, Authorization.resource_id == Resource.id) \
            .join(securityrole_authorizations, Authorization.id == securityrole_authorizations.c.authorization_id) \
            .join(SecurityRole, securityrole_authorizations.c.securityrole_id == SecurityRole.id) \
            .join(user_securityroles, SecurityRole.id == user_securityroles.c.securityrole_id) \
            .join(User, (User.id == user_securityroles.c.user_id) & (User.org_id == user_securityroles.c.org_id)) \
            .filter(User.id == user_id, User.org_id == org_id) \
            .all()
        # Map the permissions as a list of dicts
        permissions = [{"resource": permission.resource, "action": permission.action} for permission in user_permissions_query]
        return permissions

    except Exception as e:
        current_app.app_logger.error(f'Error fetching user permissions: {str(e)}')
        return []

def has_permission(org_id, user_id, resource_name, action_name):
    print(f'has_permission - org_id: {org_id} /// user_id:{user_id} /// resource_name:{resource_name} /// action_name:{action_name}')

    try:
        # Extract JWT claims (org_id and permissions)
        jwt_data = get_jwt()
        
        # Extract permissions from the JWT claims
        jwt_org_id = jwt_data.get(JWT_KEY_ORG_ID)
        jwt_user_id = jwt_data.get(JWT_KEY_SUB)  # 'sub' is the standard claim for user identity (user_id)
        permissions = jwt_data.get(JWT_KEY_PERMISSIONS, [])
        # Check if the token contains the correct org_id and user_id
        if jwt_org_id != org_id or jwt_user_id != user_id:
            current_app.security_logger.critical(f'JWT org_id/user_id mismatch: Expected org_id {org_id}, user_id {user_id}, but found org_id {jwt_org_id}, user_id {jwt_user_id}')
            return False

        # Check if the required permission exists in the JWT permissions
        for permission in permissions:
            if permission['resource'] == resource_name and permission['action'] == action_name:
                print(f'[SUCCESS] JWT authorization found for user {user_id}')
                return True

        # If no matching permission is found
        current_app.security_logger.critical(f'Permission error: User: {user_id} Resource: {resource_name} Action: {action_name}')
        return False

    except Exception as e:
        current_app.app_logger.critical(f'has_permission: Exception occurred: {str(e)}')
        return False

def has_permission_db(org_id, user_id, resource_name, action_name):
    from app import db
    from app.models import User, Resource, Action, Authorization, SecurityRole, user_securityroles, securityrole_authorizations
    print(f'has_permission_db - org_id: {org_id} /// user_id:{user_id} /// resource_name:{resource_name} /// action_name:{action_name}')
    
    try:
        # query parameter follow the sequence defined in model 
        user = User.query.get((user_id, org_id))
        if not user:
            print(f'user NOT found: {user_id}')
            current_app.security_logger.critical(f'has_permission: User not found - org_id: {org_id} user_id: {user_id} trying to access resource: {resource_name} to actoin {action_name}.')
            return False 
        else:
            print(f'user found: {user.firstname}')
        
        # Query the Resource and Action from the database
        resource = Resource.query.filter_by(name=resource_name).first()
        action = Action.query.filter_by(name=action_name).first()

        if not resource:
            current_app.app_logger.critical(f'has_permission: Resource not found: {resource_name}')
            return False
        if not action:
            current_app.app_logger.critical(f'has_permission: Action not found: {action_name}')
            return False
        
        query = db.session.query(User.username) \
            .join(user_securityroles, (User.id == user_securityroles.c.user_id) & (User.org_id == user_securityroles.c.org_id)) \
            .join(SecurityRole, (user_securityroles.c.securityrole_id == SecurityRole.id) & (user_securityroles.c.org_id == SecurityRole.org_id)) \
            .join(securityrole_authorizations, (SecurityRole.id == securityrole_authorizations.c.securityrole_id) & (SecurityRole.org_id == securityrole_authorizations.c.org_id)) \
            .join(Authorization, securityrole_authorizations.c.authorization_id == Authorization.id) \
            .join(Action, Authorization.action_id == action.id) \
            .join(Resource, Authorization.resource_id == resource.id) \
            .filter(Resource.name == resource_name) \
            .filter(Action.name == action_name) \
            .filter(User.org_id == org_id)
        #print(str(query.statement))
        authorizations = query.all()
        #print(f'[INFO] authorizations returned from query: {authorizations}')

        # Return True if the user has at least one authorization for the resource and action
        if len(authorizations) > 0:
            #print(f'[SUCCESS] Authorization found for user {user_id}')
            return True
        else:
            #print(f'[FAILURE] No authorization found for user {user_id}')
            return False
    
    except Exception as e:
        current_app.app_logger.critical(f'has_permission: Exception occurred: {str(e)}')
        return False

def get_user_roles(org_id, user_id):
    from app import db
    from app.models import SecurityRole, user_securityroles

    """
    Retrieve all roles associated with a user for the given organization.
    """
    try:
        # Query the roles for the user based on org_id and user_id
        roles = db.session.query(SecurityRole.name).join(
            user_securityroles, 
            (SecurityRole.org_id == user_securityroles.c.org_id) & 
            (SecurityRole.id == user_securityroles.c.securityrole_id)
        ).filter(
            user_securityroles.c.org_id == org_id,
            user_securityroles.c.user_id == user_id
        ).all()

        # Return role names as a list
        return [role.name for role in roles]
    
    except Exception as e:
        current_app.app_logger.error(f"get_user_roles error: user_id: {user_id} org_id: {org_id}: {str(e)}")
        return []

