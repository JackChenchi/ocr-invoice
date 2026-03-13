import axios from 'axios';

const baseURL = import.meta.env?.VITE_API_URL || '/api'

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }
    return Promise.reject(error);
  }
);

export default {
  login(username, password) {
    return apiClient.post('/auth/login', { username, password });
  },

  getCurrentUser() {
    return apiClient.get('/auth/me');
  },

  createUser(payload) {
    return apiClient.post('/auth/users', payload);
  },

  listUsers() {
    return apiClient.get('/auth/users');
  },

  deleteUser(userId) {
    return apiClient.delete(`/auth/users/${userId}`);
  },

  uploadInvoice(file) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/invoice/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  batchUploadInvoices(files) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return apiClient.post('/invoice/batch-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getInvoiceList(page = 1, pageSize = 20, status = null, isInvoice = null, dateRange = null) {
    let url = `/invoice/?page=${page}&page_size=${pageSize}`;
    if (status) url += `&status=${status}`;
    if (isInvoice !== null) url += `&is_invoice=${isInvoice}`;
    if (dateRange && dateRange.length === 2) {
      url += `&date_from=${encodeURIComponent(dateRange[0])}&date_to=${encodeURIComponent(dateRange[1])}`;
    }
    return apiClient.get(url);
  },
  
  getInvoice(id) {
    return apiClient.get(`/invoice/${id}`);
  },
  
  deleteInvoice(id) {
    return apiClient.delete(`/invoice/${id}`);
  },
  
  deleteAllInvoices() {
    return apiClient.delete('/invoice/batch/all');
  },
  
  exportInvoices(invoiceIds = null, exportAll = false, fields = null, dateRange = null, includeImages = false) {
    return apiClient.post('/invoice/export', {
      invoice_ids: invoiceIds,
      export_all: exportAll,
      fields,
      date_from: dateRange?.[0] || null,
      date_to: dateRange?.[1] || null,
      include_images: includeImages
    }, {
      responseType: 'blob'
    });
  },
  
  getStatistics() {
    return apiClient.get('/invoice/statistics/summary');
  },

  getFieldStatistics() {
    return apiClient.get('/invoice/statistics/fields');
  },
  
  uploadImage(file) {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/ocr/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getTaskStatus(id) {
    return apiClient.get(`/ocr/${id}`);
  },
  
  getResults(skip = 0, limit = 100) {
    return apiClient.get(`/ocr/?skip=${skip}&limit=${limit}`);
  }
};
