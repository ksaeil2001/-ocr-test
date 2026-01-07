import { useState, useEffect } from 'react';
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory
} from '../services/api';
import './Categories.css';

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState(''); // 'expense', 'income', or ''
  
  // 폼 상태
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'expense',
    color: '#FF6B6B',
    icon: ''
  });
  
  // 삭제 확인 다이얼로그
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  // 카테고리 목록 조회
  const fetchCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = filterType ? { type: filterType } : {};
      const response = await getCategories(params);
      setCategories(response.items || []);
    } catch (err) {
      setError('카테고리 목록을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, [filterType]);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      type: 'expense',
      color: '#FF6B6B',
      icon: ''
    });
    setEditingCategory(null);
    setShowForm(false);
  };

  // 폼 제출 (생성/수정)
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setError(null);
      
      if (editingCategory) {
        // 수정
        await updateCategory(editingCategory.id, formData);
      } else {
        // 생성
        await createCategory(formData);
      }
      
      resetForm();
      fetchCategories();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '카테고리 저장에 실패했습니다.';
      setError(errorMessage);
    }
  };

  // 수정 시작
  const handleEdit = (category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      type: category.type,
      color: category.color,
      icon: category.icon || ''
    });
    setShowForm(true);
  };

  // 삭제 확인
  const handleDeleteClick = (category) => {
    setDeleteConfirm(category);
  };

  // 삭제 실행
  const handleDeleteConfirm = async () => {
    if (!deleteConfirm) return;
    
    try {
      setError(null);
      await deleteCategory(deleteConfirm.id);
      setDeleteConfirm(null);
      fetchCategories();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '카테고리 삭제에 실패했습니다.';
      setError(errorMessage);
      setDeleteConfirm(null);
    }
  };

  // 색상 선택 옵션 (일반적인 색상들)
  const colorOptions = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B88B', '#82E0AA',
    '#F1948A', '#85C1E9', '#F7DC6F', '#D7BDE2', '#AED6F1'
  ];

  return (
    <div className="categories-page">
      <div className="categories-header">
        <h1>카테고리 관리</h1>
        <button 
          className="btn btn-primary" 
          onClick={() => setShowForm(true)}
        >
          + 카테고리 추가
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 필터 */}
      <div className="filter-section">
        <label>타입 필터:</label>
        <select 
          value={filterType} 
          onChange={(e) => setFilterType(e.target.value)}
          className="filter-select"
        >
          <option value="">전체</option>
          <option value="expense">지출</option>
          <option value="income">수입</option>
        </select>
      </div>

      {/* 카테고리 추가/수정 폼 */}
      {showForm && (
        <div className="modal-overlay" onClick={resetForm}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingCategory ? '카테고리 수정' : '카테고리 추가'}</h2>
              <button className="close-btn" onClick={resetForm}>×</button>
            </div>
            
            <form onSubmit={handleSubmit} className="category-form">
              <div className="form-group">
                <label>이름 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  maxLength={50}
                  placeholder="카테고리 이름"
                />
              </div>

              <div className="form-group">
                <label>타입 *</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  required
                >
                  <option value="expense">지출</option>
                  <option value="income">수입</option>
                </select>
              </div>

              <div className="form-group">
                <label>색상 *</label>
                <div className="color-picker">
                  <input
                    type="color"
                    value={formData.color}
                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                    required
                  />
                  <div className="color-options">
                    {colorOptions.map((color) => (
                      <button
                        key={color}
                        type="button"
                        className={`color-option ${formData.color === color ? 'active' : ''}`}
                        style={{ backgroundColor: color }}
                        onClick={() => setFormData({ ...formData, color })}
                        title={color}
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label>아이콘</label>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                  maxLength={50}
                  placeholder="아이콘 이름 (선택)"
                />
              </div>

              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={resetForm}>
                  취소
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingCategory ? '수정' : '추가'}
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
            <h3>카테고리 삭제</h3>
            <p>
              '{deleteConfirm.name}' 카테고리를 삭제하시겠습니까?
              <br />
              <small>이 카테고리를 사용하는 거래 내역이 있으면 삭제할 수 없습니다.</small>
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

      {/* 카테고리 목록 */}
      {loading ? (
        <div className="loading">로딩 중...</div>
      ) : categories.length === 0 ? (
        <div className="empty-state">
          카테고리가 없습니다. 카테고리를 추가해주세요.
        </div>
      ) : (
        <div className="categories-list">
          {categories.map((category) => (
            <div key={category.id} className="category-card">
              <div 
                className="category-color" 
                style={{ backgroundColor: category.color }}
              />
              <div className="category-info">
                <h3>{category.name}</h3>
                <div className="category-meta">
                  <span className={`type-badge ${category.type}`}>
                    {category.type === 'expense' ? '지출' : '수입'}
                  </span>
                  {category.icon && (
                    <span className="icon-badge">{category.icon}</span>
                  )}
                </div>
              </div>
              <div className="category-actions">
                <button 
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleEdit(category)}
                >
                  수정
                </button>
                <button 
                  className="btn btn-sm btn-danger"
                  onClick={() => handleDeleteClick(category)}
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Categories;

