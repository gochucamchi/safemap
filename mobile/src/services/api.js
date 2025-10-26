import axios from 'axios';

// 백엔드 API URL 설정
// Codespaces에서 실행 시: Codespaces URL 사용
// 로컬 개발 시: localhost 사용

// export const API_BASE_URL = __DEV__ 
//   ? 'https://nightmarish-vampire-pqxqw7gv7v7hrq7p-8000.app.github.dev'  // 개발 환경 (나중에 Codespaces URL로 변경)
//   : 'https://your-production-api.com';  // 프로덕션 환경

export const API_BASE_URL = 'https://nightmarish-vampire-pqxqw7gv7v7hrq7p-8000.app.github.dev';

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API 함수들
export const api = {
  // 실종자 목록 조회
  getMissingPersons: async (params = {}) => {
    try {
      const response = await apiClient.get('/api/v1/missing-persons', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching missing persons:', error);
      throw error;
    }
  },

  // 실종자 통계 조회
  getStatistics: async (days = 30) => {
    try {
      const response = await apiClient.get('/api/v1/missing-persons/stats', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching statistics:', error);
      throw error;
    }
  },

  // 안전시설 목록 조회
  getSafetyFacilities: async (params = {}) => {
    try {
      const response = await apiClient.get('/api/v1/safety-facilities', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching safety facilities:', error);
      throw error;
    }
  },

  // 헬스 체크
  healthCheck: async () => {
    try {
      const response = await apiClient.get('/api/v1/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
};

export default apiClient;
