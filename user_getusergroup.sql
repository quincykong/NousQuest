SELECT securityrole.name as securityrole_name FROM securityrole
	JOIN user_securityroles ON securityrole.org_id = user_securityroles.org_id 
		AND securityrole.id = user_securityroles.securityrole_id
WHERE user_securityroles.org_id = '906e3dcd-4612-4b99-b57c-e0541f276dc7' 
	AND user_securityroles.user_id = '7380b82f-ec26-4ed7-a936-8146497fe2e7';
