// central routes path
const routes = {
    frontendlog: '/frontendlog',
    studenthome: '/home/student',
    instructorhome: 'home/student',
    login: '/login',
    forgotPassword: '/forgot-password',
    api: {
      frontendlog: 'api/frontendlog',
      home: 'api/home',
      studenthome: 'api/studenthome',
      instructorhome: 'api/instructorhome',
      login: '/api/login',
      resetPassword: '/api/reset-password',
      studentgroup: '/api/usergroups',
      userGroupStudents: 'api/userGroupStudents',
      userGroupTags: 'api/userGroupTags',
      groupTags: 'api/groupTags',
      massUpdateGroups: 'api/massUpdateGroupStatus',
      massDeleteGroups: 'api/massDeleteGroups',
      jwt_refresh: 'api/refresh',
    },
  };

export default routes;
