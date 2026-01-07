import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  processReceiptOCR,
  saveReceiptTransaction,
  getCategories
} from '../services/api';
import './Receipt.css';

const Receipt = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);
  const [ocrResult, setOcrResult] = useState(null);
  
  // 폼 데이터
  const [formData, setFormData] = useState({
    date: '',
    store: '',
    total: '',
    category: '',
    memo: '',
    type: 'expense',
    items: []
  });

  // 카테고리 목록 조회
  const fetchCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.items || []);
    } catch (err) {
      console.error('카테고리 목록 조회 실패:', err);
    }
  };

  // 컴포넌트 마운트 시 카테고리 조회
  useEffect(() => {
    fetchCategories();
  }, []);

  // 파일 선택 핸들러
  const handleFileSelect = (file) => {
    if (!file) return;

    // 파일 형식 검증
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/heic', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('지원하지 않는 파일 형식입니다. (jpg, jpeg, png, heic, webp만 가능)');
      return;
    }

    // 파일 크기 검증 (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('파일 크기는 10MB 이하여야 합니다.');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setOcrResult(null);

    // 미리보기 생성
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // 파일 입력 변경 핸들러
  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // 드래그 앤 드롭 핸들러
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // OCR 처리
  const handleOCR = async () => {
    if (!selectedFile) {
      setError('파일을 선택해주세요.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const result = await processReceiptOCR(selectedFile);
      setOcrResult(result);

      // OCR 결과를 폼 데이터에 반영
      const date = result.date ? new Date(result.date).toISOString().split('T')[0] : new Date().toISOString().split('T')[0];
      const time = result.date ? new Date(result.date).toTimeString().split(' ')[0].slice(0, 5) : '00:00';
      
      setFormData({
        date: `${date}T${time}`,
        store: result.store || '',
        total: result.total?.toString() || '',
        category: result.category || '',
        memo: result.store ? `${result.store} - ${result.items.map(i => i.name).join(', ')}` : '',
        type: 'expense',
        items: result.items || []
      });
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          'OCR 처리에 실패했습니다.';
      setError(errorMessage);
      console.error('OCR 처리 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  // 저장 핸들러
  const handleSave = async () => {
    if (!formData.date || !formData.total || !formData.category) {
      setError('날짜, 금액, 카테고리를 모두 입력해주세요.');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const saveData = {
        date: new Date(formData.date).toISOString().split('T')[0],
        store: formData.store || undefined,
        items: formData.items,
        total: parseFloat(formData.total),
        category: formData.category,
        memo: formData.memo || undefined,
        receiptImagePath: ocrResult?.receiptImagePath || undefined,
        type: formData.type
      };

      await saveReceiptTransaction(saveData);
      
      // 성공 시 거래 내역 페이지로 이동
      navigate('/transactions');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          '거래 내역 저장에 실패했습니다.';
      setError(errorMessage);
      console.error('저장 오류:', err);
    } finally {
      setLoading(false);
    }
  };

  // 초기화
  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setOcrResult(null);
    setFormData({
      date: '',
      store: '',
      total: '',
      category: '',
      memo: '',
      type: 'expense',
      items: []
    });
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // 해당 타입의 카테고리만 필터링
  const filteredCategories = categories.filter(
    cat => cat.type === formData.type
  );

  return (
    <div className="receipt-page">
      <div className="receipt-header">
        <h1>영수증 업로드</h1>
        <button 
          className="btn btn-secondary" 
          onClick={() => navigate('/transactions')}
        >
          거래 내역으로 이동
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button 
            className="btn btn-sm btn-primary" 
            onClick={() => setError(null)}
            style={{ marginLeft: '12px' }}
          >
            닫기
          </button>
        </div>
      )}

      <div className="receipt-content">
        {/* 파일 업로드 영역 */}
        <div className="upload-section">
          <h2>1. 영수증 이미지 업로드</h2>
          
          {!previewUrl ? (
            <div
              className="upload-area"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="upload-placeholder">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p>클릭하거나 드래그하여 영수증 이미지를 업로드하세요</p>
                <p className="upload-hint">지원 형식: JPG, PNG, HEIC, WEBP (최대 10MB)</p>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/heic,image/webp"
                onChange={handleFileInputChange}
                style={{ display: 'none' }}
              />
            </div>
          ) : (
            <div className="preview-section">
              <div className="preview-image-container">
                <img src={previewUrl} alt="영수증 미리보기" className="preview-image" />
                <button 
                  className="btn btn-sm btn-danger remove-image-btn"
                  onClick={handleReset}
                >
                  ×
                </button>
              </div>
              <div className="preview-actions">
                <button 
                  className="btn btn-secondary"
                  onClick={() => fileInputRef.current?.click()}
                >
                  다른 파일 선택
                </button>
                <button 
                  className="btn btn-primary"
                  onClick={handleOCR}
                  disabled={loading}
                >
                  {loading ? 'OCR 처리 중...' : 'OCR 처리 시작'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* OCR 결과 및 수정 폼 */}
        {ocrResult && (
          <div className="ocr-result-section">
            <h2>2. OCR 결과 확인 및 수정</h2>
            
            {ocrResult.confidence > 0 && (
              <div className="confidence-badge">
                신뢰도: {(ocrResult.confidence * 100).toFixed(1)}%
              </div>
            )}

            <form className="receipt-form" onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
              <div className="form-row">
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
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>상호명</label>
                  <input
                    type="text"
                    value={formData.store}
                    onChange={(e) => setFormData({ ...formData, store: e.target.value })}
                    placeholder="상호명을 입력하세요"
                  />
                </div>

                <div className="form-group">
                  <label>총액 *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={formData.total}
                    onChange={(e) => setFormData({ ...formData, total: e.target.value })}
                    required
                    placeholder="0.00"
                  />
                </div>
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
                    <option key={cat.id || cat._id} value={cat.name}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              {formData.items && formData.items.length > 0 && (
                <div className="form-group">
                  <label>상품 목록</label>
                  <div className="items-list">
                    {formData.items.map((item, index) => (
                      <div key={index} className="item-row">
                        <span className="item-name">{item.name}</span>
                        <span className="item-price">
                          {new Intl.NumberFormat('ko-KR').format(item.price)}원
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

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

              {ocrResult.rawText && (
                <div className="form-group">
                  <label>OCR 원본 텍스트</label>
                  <div className="raw-text">
                    {ocrResult.rawText}
                  </div>
                </div>
              )}

              <div className="form-actions">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={handleReset}
                >
                  초기화
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? '저장 중...' : '거래 내역으로 저장'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Receipt;

