import { useState, useEffect } from 'react';
import {
  getTransactions,
  createTransaction,
  updateTransaction,
  deleteTransaction,
  getCategories
} from '../services/api';
import './Transactions.css';

const Transactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 페이징 상태
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  });
  
  // 필터 상태
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    category: '',
    type: '',
    search: ''
  });
  
  // 정렬 상태
  const [sort, setSort] = useState('date');
  const [order, setOrder] = useState('desc');
  
  // 폼 상태
  const [showForm, setShowForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [formData, setFormData] = useState({
    type: 'expense',
    date: new Date().toISOString().split('T')[0] + 'T00:00:00',
    amount: '',
    category: '',
    memo: '',
    receiptImagePath: ''
  });
  
  // 삭제 확인 다이얼로그
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // 카테고리 목록 조회
  const fetchCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.items || []);
    } catch (err) {
      console.error('카테고리 목록 조회 실패:', err);
    }
  };

  // 거래 내역 목록 조회
  const fetchTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: pagination.page,
        limit: pagination.limit,
        sort: sort,
        order: order,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, value]) => value !== '')
        )
      };
      
      const response = await getTransactions(params);
      setTransactions(response.items || []);
      setPagination({
        page: response.page || 1,
        limit: response.limit || 20,
        total: response.total || 0,
        totalPages: response.total_pages || 0
      });
    } catch (err) {
      let errorMessage = '거래 내역 목록을 불러오는데 실패했습니다.';
      
      // 상세한 에러 정보 로깅
      console.error('거래 내역 조회 오류 상세:', {
        message: err.message,
        response: err.response,
        request: err.request,
        config: err.config
      });
      
      if (err.response) {
        // 서버가 응답했지만 에러 상태 코드
        const status = err.response.status;
        const detail = err.response.data?.detail || err.response.data?.message;
        const requestUrl = err.config?.baseURL + err.config?.url;
        
        console.error(`API 요청 실패 [${status}]:`, requestUrl);
        
        if (status === 500) {
          errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        } else if (status === 404) {
          errorMessage = `API 엔드포인트를 찾을 수 없습니다. (${requestUrl})`;
        } else if (status === 400) {
          errorMessage = detail || '잘못된 요청입니다. 필터 조건을 확인해주세요.';
        } else {
          errorMessage = detail || `서버 오류가 발생했습니다. (${status})`;
        }
      } else if (err.request) {
        // 요청은 보냈지만 응답을 받지 못함 (네트워크 오류)
        const requestUrl = err.config?.baseURL + err.config?.url;
        console.error('네트워크 오류 - 요청 URL:', requestUrl);
        errorMessage = `서버에 연결할 수 없습니다. (${requestUrl}) 백엔드 서버가 실행 중인지 확인해주세요.`;
      } else {
        // 요청 설정 중 오류 발생
        errorMessage = `요청 중 오류가 발생했습니다: ${err.message}`;
      }
      
      setError(errorMessage);
      console.error('거래 내역 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [pagination.page, pagination.limit, sort, order, filters]);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      type: 'expense',
      date: new Date().toISOString().split('T')[0] + 'T00:00:00',
      amount: '',
      category: '',
      memo: '',
      receiptImagePath: ''
    });
    setEditingTransaction(null);
    setShowForm(false);
  };

  // 폼 제출 (생성/수정)
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setError(null);
      
      const transactionData = {
        ...formData,
        date: new Date(formData.date).toISOString(),
        amount: parseFloat(formData.amount)
      };
      
      if (editingTransaction) {
        // 수정
        const transactionId = editingTransaction.id || editingTransaction._id;
        if (!transactionId) {
          setError('거래 내역 ID를 찾을 수 없습니다.');
          return;
        }
        await updateTransaction(transactionId, transactionData);
      } else {
        // 생성
        await createTransaction(transactionData);
      }
      
      resetForm();
      fetchTransactions();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '거래 내역 저장에 실패했습니다.';
      setError(errorMessage);
    }
  };

  // 수정 시작
  const handleEdit = (transaction) => {
    setEditingTransaction(transaction);
    const date = new Date(transaction.date);
    setFormData({
      type: transaction.type,
      date: date.toISOString().slice(0, 16),
      amount: transaction.amount.toString(),
      category: transaction.category,
      memo: transaction.memo || '',
      receiptImagePath: transaction.receiptImagePath || ''
    });
    setShowForm(true);
  };

  // 삭제 확인
  const handleDeleteClick = (transaction) => {
    setDeleteConfirm(transaction);
  };

  // 삭제 실행
  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return;
    
    try {
      setError(null);
      const transactionId = deleteConfirm.id || deleteConfirm._id;
      if (!transactionId) {
        setError('거래 내역 ID를 찾을 수 없습니다.');
        return;
      }
      await deleteTransaction(transactionId);
      setDeleteConfirm(null);
      fetchTransactions();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '거래 내역 삭제에 실패했습니다.';
      setError(errorMessage);
      setDeleteConfirm(null);
    }
  };

  // 필터 변경
  const handleFilterChange = (key, value) => {
    setFilters({ ...filters, [key]: value });
    setPagination({ ...pagination, page: 1 }); // 필터 변경 시 첫 페이지로
  };

  // 필터 초기화
  const resetFilters = () => {
    setFilters({
      dateFrom: '',
      dateTo: '',
      category: '',
      type: '',
      search: ''
    });
    setPagination({ ...pagination, page: 1 });
  };

  // 정렬 변경
  const handleSortChange = (newSort) => {
    if (sort === newSort) {
      setOrder(order === 'desc' ? 'asc' : 'desc');
    } else {
      setSort(newSort);
      setOrder('desc');
    }
  };

  // 페이지 변경
  const handlePageChange = (newPage) => {
    setPagination({ ...pagination, page: newPage });
  };

  // 금액 포맷팅
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('ko-KR').format(amount);
  };

  // 날짜 포맷팅
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // 해당 타입의 카테고리만 필터링
  const filteredCategories = categories.filter(
    cat => !formData.type || cat.type === formData.type
  );

  return (
    <div className="transactions-page">
      <div className="transactions-header">
        <h1>거래 내역</h1>
        <button 
          className="btn btn-primary" 
          onClick={() => setShowForm(true)}
        >
          + 거래 내역 추가
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button 
            className="btn btn-sm btn-primary" 
            onClick={fetchTransactions}
            style={{ marginLeft: '12px' }}
          >
            다시 시도
          </button>
        </div>
      )}

      {/* 필터 섹션 */}
      <div className="filters-section">
        <div className="filter-row">
          <div className="filter-group">
            <label>시작 날짜</label>
            <input
              type="date"
              value={filters.dateFrom}
              onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>종료 날짜</label>
            <input
              type="date"
              value={filters.dateTo}
              onChange={(e) => handleFilterChange('dateTo', e.target.value)}
            />
          </div>
          
          <div className="filter-group">
            <label>카테고리</label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
            >
              <option value="">전체</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.name}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          
          <div className="filter-group">
            <label>타입</label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">전체</option>
              <option value="expense">지출</option>
              <option value="income">수입</option>
            </select>
          </div>
          
          <div className="filter-group">
            <label>검색</label>
            <input
              type="text"
              placeholder="메모 검색..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
            />
          </div>
          
          <button 
            className="btn btn-secondary"
            onClick={resetFilters}
          >
            필터 초기화
          </button>
        </div>
      </div>

      {/* 거래 내역 추가/수정 폼 */}
      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingTransaction ? '거래 내역 수정' : '거래 내역 추가'}</h2>
              <button className="close-btn" onClick={resetForm}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="transaction-form">
              <div className="form-group">
                <label>타입 *</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value, category: '' })}
                  required
                >
                  <option value="expense">지출</option>
                  <option value="income">수입</option>
                </select>
              </div>

              <div className="form-group">
                <label>날짜 *</label>
                <input
                  type="datetime-local"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>금액 *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  required
                  placeholder="0.00"
                />
              </div>

              <div className="form-group">
                <label>카테고리 *</label>
                <select
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  required
                >
                  <option value="">선택하세요</option>
                  {filteredCategories.map((cat) => (
                    <option key={cat.id} value={cat.name}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>메모</label>
                <textarea
                  value={formData.memo}
                  onChange={(e) => setFormData({ ...formData, memo: e.target.value })}
                  maxLength={500}
                  rows={3}
                  placeholder="메모를 입력하세요 (최대 500자)"
                />
              </div>

              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={resetForm}>
                  취소
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingTransaction ? '수정' : '추가'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 삭제 확인 다이얼로그 */}
      {deleteConfirm && (
        <div className="modal-overlay" onClick={() => setDeleteConfirm(null)}>
          <div className="modal-content delete-confirm" onClick={(e) => e.stopPropagation()}>
            <h3>거래 내역 삭제</h3>
            <p>
              이 거래 내역을 삭제하시겠습니까?
              <br />
              <small>이 작업은 되돌릴 수 없습니다.</small>
            </p>
            <div className="form-actions">
              <button 
                className="btn btn-secondary" 
                onClick={() => setDeleteConfirm(null)}
              >
                취소
              </button>
              <button 
                className="btn btn-danger" 
                onClick={handleDeleteConfirm}
              >
                삭제
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 정렬 및 페이징 정보 */}
      <div className="table-controls">
        <div className="sort-controls">
          <span>정렬:</span>
          <button 
            className={`sort-btn ${sort === 'date' ? 'active' : ''}`}
            onClick={() => handleSortChange('date')}
          >
            날짜 {sort === 'date' && (order === 'desc' ? '↓' : '↑')}
          </button>
          <button 
            className={`sort-btn ${sort === 'amount' ? 'active' : ''}`}
            onClick={() => handleSortChange('amount')}
          >
            금액 {sort === 'amount' && (order === 'desc' ? '↓' : '↑')}
          </button>
          <button 
            className={`sort-btn ${sort === 'category' ? 'active' : ''}`}
            onClick={() => handleSortChange('category')}
          >
            카테고리 {sort === 'category' && (order === 'desc' ? '↓' : '↑')}
          </button>
        </div>
        
        <div className="pagination-info">
          전체 {pagination.total}건 (페이지 {pagination.page}/{pagination.totalPages || 1})
        </div>
      </div>

      {/* 거래 내역 목록 */}
      {loading ? (
        <div className="loading">로딩 중...</div>
      ) : transactions.length === 0 ? (
        <div className="empty-state">
          거래 내역이 없습니다. 거래 내역을 추가해주세요.
        </div>
      ) : (
        <>
          <div className="transactions-table-container">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>타입</th>
                  <th>카테고리</th>
                  <th>금액</th>
                  <th>메모</th>
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id || transaction._id}>
                    <td>{formatDate(transaction.date)}</td>
                    <td>
                      <span className={`type-badge ${transaction.type}`}>
                        {transaction.type === 'expense' ? '지출' : '수입'}
                      </span>
                    </td>
                    <td>{transaction.category}</td>
                    <td className={`amount ${transaction.type}`}>
                      {transaction.type === 'expense' ? '-' : '+'}
                      {formatAmount(transaction.amount)}원
                    </td>
                    <td className="memo-cell">
                      {transaction.memo || '-'}
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          className="btn btn-sm btn-secondary"
                          onClick={() => handleEdit(transaction)}
                        >
                          수정
                        </button>
                        <button 
                          className="btn btn-sm btn-danger"
                          onClick={() => handleDeleteClick(transaction)}
                        >
                          삭제
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 페이징 */}
          {pagination.totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-secondary"
                onClick={() => handlePageChange(pagination.page - 1)}
                disabled={pagination.page === 1}
              >
                이전
              </button>
              
              {Array.from({ length: pagination.totalPages }, (_, i) => i + 1)
                .filter(page => {
                  // 현재 페이지 주변 5개 페이지만 표시
                  return Math.abs(page - pagination.page) <= 2 || 
                         page === 1 || 
                         page === pagination.totalPages;
                })
                .map((page, index, array) => {
                  // 생략 표시
                  if (index > 0 && page - array[index - 1] > 1) {
                    return (
                      <span key={`ellipsis-${page}`} className="pagination-ellipsis">
                        ...
                      </span>
                    );
                  }
                  return (
                    <button
                      key={page}
                      className={`btn ${pagination.page === page ? 'btn-primary' : 'btn-secondary'}`}
                      onClick={() => handlePageChange(page)}
                    >
                      {page}
                    </button>
                  );
                })}
              
              <button
                className="btn btn-secondary"
                onClick={() => handlePageChange(pagination.page + 1)}
                disabled={pagination.page === pagination.totalPages}
              >
                다음
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Transactions;

