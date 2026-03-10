<template>
  <el-card class="upload-card">
    <template #header>
      <div class="card-header">
        <span>{{ t('upload.title') }}</span>
        <el-tag type="info">{{ t('upload.batchSupport') }}</el-tag>
      </div>
    </template>
    
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      multiple
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :file-list="fileList"
      accept="image/jpeg,image/png,image/bmp,image/tiff,image/webp"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        {{ t('upload.dragText') }}<em>{{ t('upload.clickUpload') }}</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          {{ t('upload.tip') }}
        </div>
      </template>
    </el-upload>
    
    <div class="upload-actions" v-if="fileList.length > 0">
      <el-button type="primary" @click="submitUpload" :loading="uploading">
        {{ t('upload.startRecognize') }} ({{ fileList.length }} {{ t('upload.images') }})
      </el-button>
      <el-button @click="clearFiles">{{ t('upload.clear') }}</el-button>
    </div>
    
    <el-dialog v-model="showResultDialog" :title="t('upload.resultTitle')" width="80%">
      <div v-if="batchResult">
        <el-alert
          :title="`${t('upload.resultSuccess')} ${batchResult.success_count} ${t('upload.images')}，${t('upload.resultFailed')} ${batchResult.failed_count} ${t('upload.images')}`"
          :type="batchResult.failed_count > 0 ? 'warning' : 'success'"
          show-icon
          class="result-alert"
        />
        
        <el-table :data="batchResult.results" style="width: 100%; margin-top: 20px" max-height="400">
          <el-table-column prop="file_name" :label="t('invoice.invoiceNumber')" width="180" />
          <el-table-column prop="invoice_type" :label="t('invoice.invoiceType')" width="150" />
          <el-table-column prop="invoice_number" :label="t('invoice.invoiceNumber')" width="120" />
          <el-table-column prop="invoice_date" :label="t('invoice.invoiceDate')" width="110" />
          <el-table-column prop="buyer_name" :label="t('invoice.buyer')" width="150" show-overflow-tooltip />
          <el-table-column prop="seller_name" :label="t('invoice.seller')" width="150" show-overflow-tooltip />
          <el-table-column prop="total_amount" :label="t('invoice.totalAmount')" width="100">
            <template #default="scope">
              {{ scope.row.total_amount ? `${scope.row.total_amount.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="validation_score" :label="t('invoice.confidence')" width="80">
            <template #default="scope">
              <el-tag :type="getScoreType(scope.row.validation_score)">
                {{ (scope.row.validation_score * 100).toFixed(0) }}%
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" :label="t('invoice.status')" width="100">
            <template #default="scope">
              <el-tag :type="getStatusType(scope.row.status)">
                {{ getStatusText(scope.row.status) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '../services/api'

const { t } = useI18n()

const uploadRef = ref()
const fileList = ref([])
const uploading = ref(false)
const showResultDialog = ref(false)
const batchResult = ref(null)

const emit = defineEmits(['upload-success'])

const handleFileChange = (file, files) => {
  fileList.value = files
}

const handleFileRemove = (file, files) => {
  fileList.value = files
}

const submitUpload = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning(t('upload.tip'))
    return
  }
  
  uploading.value = true
  
  try {
    const files = fileList.value.map(f => f.raw)
    const response = await api.batchUploadInvoices(files)
    
    batchResult.value = response.data
    showResultDialog.value = true
    
    emit('upload-success', response.data)
    
    clearFiles()
    ElMessage.success(`${t('upload.resultSuccess')} ${response.data.success_count} ${t('upload.images')}`)
  } catch (error) {
    console.error('Upload error:', error)
    ElMessage.error(t('common.failed') + '：' + (error.response?.data?.detail || error.message))
  } finally {
    uploading.value = false
  }
}

const clearFiles = () => {
  fileList.value = []
  uploadRef.value?.clearFiles()
}

const getStatusType = (status) => {
  const types = {
    'completed': 'success',
    'processing': 'warning',
    'failed': 'danger',
    'not_invoice': 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    'completed': t('list.recognizeSuccess'),
    'processing': t('list.processing'),
    'failed': t('list.recognizeFailed'),
    'not_invoice': t('list.notInvoice')
  }
  return texts[status] || status
}

const getScoreType = (score) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return 'warning'
  return 'danger'
}
</script>

<style scoped>
.upload-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.upload-card :deep(.el-card__header) {
  padding: 16px 20px;
  border-bottom: 1px solid #ebeef5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 16px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  border-radius: 10px;
  border: 2px dashed #d9d9d9;
  transition: all 0.3s ease;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background-color: #f5f7fa;
}

.upload-area :deep(.el-icon--upload) {
  font-size: 67px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-actions {
  margin-top: 20px;
  text-align: center;
}

.result-alert {
  margin-bottom: 10px;
}
</style>
