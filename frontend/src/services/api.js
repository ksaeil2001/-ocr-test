/**
 * API 서비스 레이어
 * 백엔드 API를 호출하는 통합 서비스
 */
import axios from 'axios';

// Base URL 설정 (환경 변수에서 가져오기)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8002';

// 디버깅: API Base URL 확인
console.log('API Base URL:', API_BASE_URL);
console.log('Environment VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30초 타임아웃
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 요청 전 처리 (예: 토큰 추가 등)
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    // 디버깅: 요청 URL 로깅
    console.log('API Request:', config.method?.toUpperCase(), config.baseURL + config.url, config.params);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    // 응답 성공 시 처리
    return response;
  },
  (error) => {
    // 응답 에러 처리
    if (error.response) {
      // 서버가 응답했지만 에러 상태 코드
      const { status, data } = error.response;
      
      switch (status) {
        case 400:
          console.error('잘못된 요청:', data.detail || data.message);
          break;
        case 401:
          console.error('인증 실패');
          // 로그인 페이지로 리다이렉트 등 처리
          break;
        case 403:
          console.error('권한 없음');
          break;
        case 404:
          console.error('리소스를 찾을 수 없습니다:', config?.url || error.config?.url);
          console.error('요청 URL:', error.config?.baseURL + error.config?.url);
          break;
        case 500:
          console.error('서버 오류:', data.detail || data.message);
          break;
        default:
          console.error('알 수 없는 오류:', data.detail || data.message);
      }
    } else if (error.request) {
      // 요청은 보냈지만 응답을 받지 못함
      console.error('네트워크 오류: 서버에 연결할 수 없습니다');
    } else {
      // 요청 설정 중 오류 발생
      console.error('요청 설정 오류:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// ==================== Transactions API ====================

/**
 * 거래 내역 목록 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {string} params.dateFrom - 시작 날짜
 * @param {string} params.dateTo - 종료 날짜
 * @param {string} params.category - 카테고리 이름
 * @param {string} params.type - 거래 타입 (expense/income)
 * @param {string} params.search - 검색어
 * @param {number} params.page - 페이지 번호
 * @param {number} params.limit - 페이지당 항목 수
 * @param {string} params.sort - 정렬 필드
 * @param {string} params.order - 정렬 순서 (asc/desc)
 */
export const getTransactions = async (params = {}) => {
  const response = await apiClient.get('/api/transactions', { params });
  return response.data;
};

/**
 * 거래 내역 생성
 * @param {Object} transaction - 거래 내역 데이터
 */
export const createTransaction = async (transaction) => {
  const response = await apiClient.post('/api/transactions', transaction);
  return response.data;
};

/**
 * 거래 내역 조회
 * @param {string} id - 거래 내역 ID
 */
export const getTransaction = async (id) => {
  const response = await apiClient.get(`/api/transactions/${id}`);
  return response.data;
};

/**
 * 거래 내역 수정
 * @param {string} id - 거래 내역 ID
 * @param {Object} transaction - 수정할 거래 내역 데이터
 */
export const updateTransaction = async (id, transaction) => {
  const response = await apiClient.put(`/api/transactions/${id}`, transaction);
  return response.data;
};

/**
 * 거래 내역 삭제
 * @param {string} id - 거래 내역 ID
 */
export const deleteTransaction = async (id) => {
  const response = await apiClient.delete(`/api/transactions/${id}`);
  return response.data;
};

// ==================== Categories API ====================

/**
 * 카테고리 목록 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {string} params.type - 카테고리 타입 (expense/income)
 */
export const getCategories = async (params = {}) => {
  const response = await apiClient.get('/api/categories', { params });
  return response.data;
};

/**
 * 카테고리 생성
 * @param {Object} category - 카테고리 데이터
 */
export const createCategory = async (category) => {
  const response = await apiClient.post('/api/categories', category);
  return response.data;
};

/**
 * 카테고리 조회
 * @param {string} id - 카테고리 ID
 */
export const getCategory = async (id) => {
  const response = await apiClient.get(`/api/categories/${id}`);
  return response.data;
};

/**
 * 카테고리 수정
 * @param {string} id - 카테고리 ID
 * @param {Object} category - 수정할 카테고리 데이터
 */
export const updateCategory = async (id, category) => {
  const response = await apiClient.put(`/api/categories/${id}`, category);
  return response.data;
};

/**
 * 카테고리 삭제
 * @param {string} id - 카테고리 ID
 */
export const deleteCategory = async (id) => {
  const response = await apiClient.delete(`/api/categories/${id}`);
  return response.data;
};

// ==================== Receipts API ====================

/**
 * 영수증 이미지 업로드 및 OCR 처리
 * @param {File} file - 업로드할 이미지 파일
 */
export const processReceiptOCR = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await apiClient.post('/api/receipt/ocr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * OCR 결과를 거래 내역으로 저장
 * @param {Object} receiptData - 영수증 데이터
 */
export const saveReceiptTransaction = async (receiptData) => {
  const response = await apiClient.post('/api/receipt/save', receiptData);
  return response.data;
};

// ==================== Statistics API ====================

/**
 * 요약 통계 조회
 * @param {Object} params - 쿼리 파라미터
 * @param {string} params.date - 기준 날짜 (ISO 형식 또는 YYYY-MM-DD)
 */
export const getSummaryStatistics = async (params = {}) => {
  const response = await apiClient.get('/api/statistics/summary', { params });
  return response.data;
};

// ==================== Export ====================

export default apiClient;

