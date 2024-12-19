// central routes path
const routes = {
    defaultHOME: '/home',
    frontendlog: '/frontendlog',
    forgotPassword: '/forgot-password',
    api: {
      authorizations: '/api/authorizations',
      frontendlog: '/api/frontendlog',
      login: '/api/login',
      resetPassword: '/api/reset-password',
      studentgroup: '/api/usergroups',
      userGroupStudents: '/api/userGroupStudents',
      userGroupTags: '/api/userGroupTags',
      groupTags: '/api/groupTags',
      massUpdateGroups: '/api/massUpdateGroupStatus',
      massDeleteGroups: '/api/massDeleteGroups',
      jwt_refresh: '/api/refresh',
    },
  };

export default routes;
