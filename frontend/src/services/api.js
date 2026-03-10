import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default {
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
  
  getInvoiceList(page = 1, pageSize = 20, status = null, isInvoice = null) {
    let url = `/invoice/?page=${page}&page_size=${pageSize}`;
    if (status) url += `&status=${status}`;
    if (isInvoice !== null) url += `&is_invoice=${isInvoice}`;
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
  
  exportInvoices(invoiceIds = null, exportAll = false) {
    return apiClient.post('/invoice/export', {
      invoice_ids: invoiceIds,
      export_all: exportAll
    }, {
      responseType: 'blob'
    });
  },
  
  getStatistics() {
    return apiClient.get('/invoice/statistics/summary');
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
