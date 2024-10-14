// services/fetchStudentsAndTags.js
import { ensureValidToken } from '../utils/jwtUtils';
import { triggerToast } from '../components/ToastProvider';
import routes from '../contexts/Routes';

export const fetchStudentsAndTags = async (groupId) => {
    // const token = await ensureValidToken();
    // if (!token) {
    //   triggerToast({ type: 'warning', content: 'Session expired. Please log in again.' });
    //   return { students: [], tags: [] };
    // }
    try {
      const [studentResponse, tagResponse] = await Promise.all([
        fetch(routes.api.userGroupStudents + `/${groupId}`, { credentials: 'include' }),
        fetch(routes.api.userGroupTags + `/${groupId}`, { credentials: 'include' })
      ]);
  
      const studentData = await studentResponse.json();
      const tagData = await tagResponse.json();
      
      return {
        students: studentData.students || [],
        tags: tagData.tags || [],
      };
    } catch (error) {
      triggerToast({ type: 'critical', content: `fetchStudentsAndTags error: ${error.message}`, logToBackend: true });
      return { students: [], tags: [] };
    }
  };
  