import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getSummaryStatistics,
  getTransactions
} from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statistics, setStatistics] = useState(null);
  const [recentTransactions, setRecentTransactions] = useState([]);

  // 통계 및 최근 거래 내역 조회
  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 통계 데이터와 최근 거래 내역을 병렬로 조회
      const [statsResponse, transactionsResponse] = await Promise.all([
        getSummaryStatistics(),
        getTransactions({ limit: 10, sort: 'date', order: 'desc' })
      ]);

      // 통계 데이터 파싱
      const statsData = statsResponse.data || statsResponse;
      setStatistics(statsData);

      // 최근 거래 내역 설정
      setRecentTransactions(transactionsResponse.items || []);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '대시보드 데이터를 불러오는데 실패했습니다.';
      setError(errorMessage);
      console.error('대시보드 데이터 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // 금액 포맷팅
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('ko-KR').format(amount || 0);
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

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading">로딩 중...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="error-message">
          <span>{error}</span>
          <button 
            className="btn btn-sm btn-primary" 
            onClick={fetchDashboardData}
            style={{ marginLeft: '12px' }}
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>대시보드</h1>
        <button 
          className="btn btn-primary" 
          onClick={() => navigate('/transactions')}
        >
          거래 내역 보기
        </button>
      </div>

      {/* 통계 카드 섹션 */}
      <div className="statistics-section">
        <h2>요약 통계</h2>
        <div className="statistics-grid">
          {/* 오늘 지출 카드 */}
          <div className="stat-card expense-card">
            <div className="stat-card-header">
              <h3>오늘 지출</h3>
              <span className="stat-icon">💰</span>
            </div>
            <div className="stat-card-value">
              {formatAmount(statistics?.today?.expense || 0)}원
            </div>
          </div>

          {/* 오늘 수입 카드 */}
          <div className="stat-card income-card">
            <div className="stat-card-header">
              <h3>오늘 수입</h3>
              <span className="stat-icon">💵</span>
            </div>
            <div className="stat-card-value">
              {formatAmount(statistics?.today?.income || 0)}원
            </div>
          </div>

          {/* 이번 달 지출 카드 */}
          <div className="stat-card expense-card">
            <div className="stat-card-header">
              <h3>이번 달 지출</h3>
              <span className="stat-icon">📊</span>
            </div>
            <div className="stat-card-value">
              {formatAmount(statistics?.thisMonth?.expense || 0)}원
            </div>
          </div>

          {/* 이번 달 수입 카드 */}
          <div className="stat-card income-card">
            <div className="stat-card-header">
              <h3>이번 달 수입</h3>
              <span className="stat-icon">📈</span>
            </div>
            <div className="stat-card-value">
              {formatAmount(statistics?.thisMonth?.income || 0)}원
            </div>
          </div>

          {/* 이번 달 순수입 카드 */}
          <div className={`stat-card net-income-card ${(statistics?.thisMonth?.netIncome || 0) >= 0 ? 'positive' : 'negative'}`}>
            <div className="stat-card-header">
              <h3>이번 달 순수입</h3>
              <span className="stat-icon">💹</span>
            </div>
            <div className="stat-card-value">
              {(statistics?.thisMonth?.netIncome || 0) >= 0 ? '+' : ''}
              {formatAmount(statistics?.thisMonth?.netIncome || 0)}원
            </div>
            <div className="stat-card-hint">
              {statistics?.thisMonth?.netIncome >= 0 ? '수입이 지출보다 많습니다' : '지출이 수입보다 많습니다'}
            </div>
          </div>
        </div>
      </div>

      {/* 최근 거래 내역 섹션 */}
      <div className="recent-transactions-section">
        <div className="section-header">
          <h2>최근 거래 내역</h2>
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => navigate('/transactions')}
          >
            전체 보기
          </button>
        </div>

        {recentTransactions.length === 0 ? (
          <div className="empty-state">
            거래 내역이 없습니다. 첫 거래 내역을 추가해보세요!
          </div>
        ) : (
          <div className="transactions-list">
            <table className="transactions-table">
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>타입</th>
                  <th>카테고리</th>
                  <th>금액</th>
                  <th>메모</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.map((transaction) => (
                  <tr 
                    key={transaction.id || transaction._id}
                    onClick={() => navigate('/transactions')}
                    className="transaction-row"
                  >
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
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;

