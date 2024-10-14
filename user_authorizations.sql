/* 
SELECT username
FROM user
JOIN user_securityroles ON user.id = user_securityroles.user_id
JOIN securityrole ON user_securityroles.securityrole_id = securityrole.id
JOIN securityrole_authorizations ON securityrole.id = securityrole_authorizations.securityrole_id
JOIN authorization ON securityrole_authorizations.authorization_id = authorization.id
JOIN action ON authorization.action_id = action.id
JOIN resource ON authorization.resource_id = resource.id
WHERE resource.name = 'usergroup' AND action.name = 'create';
*/

select resource.id from resource where name='usergroup';
select action.id from action where name='create';

select authorization.id 
	from authorization 
	where resource_id in (select resource.id from resource where name='usergroup')
	and action_id = (select action.id from action where name='read');
/* bdbc9039-8162-4698-8236-bdf7ff7919c4 */

select securityrole_id from securityrole_authorizations 
	where authorization_id in (
		select authorization.id 
			from authorization 
			where resource_id in (select resource.id from resource where name='usergroup')
			and action_id = (select action.id from action where name='read')
	);
/*
aaf874f4-1f04-4bce-ae34-b4839e18e441
e69baad0-4aac-4ac6-b7ec-f9801ad0d585
fcfc81f3-9cfe-404a-a064-a2d18727c223
*/
select id from securityrole 
	where id in (
		select securityrole_id from securityrole_authorizations 
		where authorization_id in (
			select authorization.id 
				from authorization 
				where resource_id in (select resource.id from resource where name='usergroup')
				and action_id = (select action.id from action where name='read')
		)
	);
/*
aaf874f4-1f04-4bce-ae34-b4839e18e441
e69baad0-4aac-4ac6-b7ec-f9801ad0d585
fcfc81f3-9cfe-404a-a064-a2d18727c223
*/
select * from user_securityroles where securityrole_id in (
	select id from securityrole where id in ('aaf874f4-1f04-4bce-ae34-b4839e18e441', 'e69baad0-4aac-4ac6-b7ec-f9801ad0d585', 'fcfc81f3-9cfe-404a-a064-a2d18727c223')
)

select id from organization;

/* query user authorization by organization, resource, and action */
SELECT username 
FROM user
JOIN user_securityroles ON user.id = user_securityroles.user_id AND user.org_id = user_securityroles.org_id
JOIN securityrole ON user_securityroles.securityrole_id = securityrole.id AND user_securityroles.org_id = securityrole.org_id
JOIN securityrole_authorizations ON securityrole.id = securityrole_authorizations.securityrole_id AND securityrole.org_id = securityrole_authorizations.org_id
JOIN authorization ON securityrole_authorizations.authorization_id = authorization.id
JOIN action ON authorization.action_id = action.id
JOIN resource ON authorization.resource_id = resource.id
WHERE resource.name = 'usergroup' AND action.name = 'delete' AND user.org_id in (select id from organization);

/* debug */
SELECT "user".username
FROM "user" 
JOIN user_securityroles ON "user".id = user_securityroles.user_id AND "user".org_id = user_securityroles.org_id 
JOIN securityrole ON user_securityroles.securityrole_id = securityrole.id AND user_securityroles.org_id = securityrole.org_id 
JOIN securityrole_authorizations ON securityrole.id = securityrole_authorizations.securityrole_id AND securityrole.org_id = securityrole_authorizations.org_id 
JOIN "authorization" ON securityrole_authorizations.authorization_id = "authorization".id 
JOIN action ON "authorization".action_id = :action_id_1 
JOIN resource ON "authorization".resource_id = :resource_id_1        
WHERE resource.name = :name_1 AND action.name = :name_2 AND "user".org_id = :org_id_1




/* Ger resource and action for specific user */
SELECT action.name AS action_name, resource.name AS resource_name 
FROM user
JOIN user_securityroles ON user.id = user_securityroles.user_id AND user.org_id = user_securityroles.org_id
JOIN securityrole ON user_securityroles.securityrole_id = securityrole.id AND user_securityroles.org_id = securityrole.org_id
JOIN securityrole_authorizations ON securityrole.id = securityrole_authorizations.securityrole_id AND securityrole.org_id = securityrole_authorizations.org_id
JOIN authorization ON securityrole_authorizations.authorization_id = authorization.id
JOIN action ON authorization.action_id = action.id
JOIN resource ON authorization.resource_id = resource.id
WHERE user.username = 'student'
AND resource.name = 'usergroup'
AND user.org_id in (select id from organization);

SELECT * 
FROM authorization 
JOIN resource ON authorization.resource_id = resource.id
JOIN action ON authorization.action_id = action.id
WHERE resource.name = 'usergroup' 
  AND action.name = 'read';
