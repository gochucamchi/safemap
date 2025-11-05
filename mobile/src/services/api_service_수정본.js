// mobile/src/services/api.js (또는 api.ts)

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const api = {
  /**
   * 실종자 목록 조회
   * @param {Object} params - 쿼리 파라미터
   * @param {number} params.limit - 최대 개수
   * @param {number} params.days - 최근 N일 (✅ 추가)
   */
  async getMissingPersons(params = {}) {
    const { limit = 100, days } = params;
    
    // ✅ days 파라미터 추가
    let url = `${API_BASE_URL}/missing-persons?limit=${limit}`;
    if (days) {
      url += `&days=${days}`;
    }
    
    try {
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  /**
   * 통계 조회
   * @param {number} days - 최근 N일
   */
  async getStatistics(days = 30) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/missing-persons/stats?days=${days}`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  /**
   * 데이터 동기화
   * @param {number} maxPages - 최대 페이지 수
   */
  async syncData(maxPages = 10) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/sync/missing-persons?max_pages=${maxPages}`,
        { method: 'POST' }
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
};
