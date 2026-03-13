<template>
  <el-card class="list-card">
    <template #header>
      <div class="card-header">
        <span>{{ t('list.title') }}</span>
        <div class="header-actions">
          <el-button type="danger" @click="handleDeleteAll">
            {{ t('list.deleteAll') }}
          </el-button>
          <el-button type="success" @click="exportSelected" :disabled="selectedInvoices.length === 0">
            {{ t('list.exportSelected') }} ({{ selectedInvoices.length }})
          </el-button>
          <el-button type="primary" @click="exportAll">
            {{ t('list.exportAll') }}
          </el-button>
          <el-button @click="loadData">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </div>
    </template>
    
    <div class="filter-bar">
      <el-popover placement="bottom-start" width="240" trigger="click">
        <template #reference>
          <el-button>{{ t('list.exportFields') }}</el-button>
        </template>
        <el-checkbox-group v-model="exportFields">
          <el-checkbox label="transaction_reference">{{ t('list.transactionCode') }}</el-checkbox>
          <el-checkbox label="transaction_date">{{ t('list.transactionDate') }}</el-checkbox>
          <el-checkbox label="receiver_account">{{ t('list.receiverAccount') }}</el-checkbox>
          <el-checkbox label="total_amount">{{ t('list.amount') }}</el-checkbox>
          <el-checkbox label="currency">{{ t('list.currency') }}</el-checkbox>
          <el-checkbox label="image_url">{{ t('list.image') }}</el-checkbox>
          <el-checkbox label="needs_review">{{ t('list.needsReview') }}</el-checkbox>
        </el-checkbox-group>
        <div class="export-options">
          <el-checkbox v-model="includeImages">{{ t('list.includeImages') }}</el-checkbox>
        </div>
      </el-popover>
      <el-date-picker
        v-model="filters.dateRange"
        type="daterange"
        range-separator="-"
        :start-placeholder="t('list.startDate')"
        :end-placeholder="t('list.endDate')"
        value-format="YYYY-MM-DD"
        style="margin-left: 10px; width: 260px"
      />
      <el-select v-model="filters.status" :placeholder="t('list.statusFilter')" clearable @change="loadData" style="width: 150px">
        <el-option :label="t('list.recognizeSuccess')" value="completed" />
        <el-option :label="t('list.recognizeFailed')" value="failed" />
        <el-option :label="t('list.notInvoice')" value="not_invoice" />
      </el-select>
      <el-select v-model="filters.isInvoice" :placeholder="t('list.invoiceType')" clearable @change="loadData" style="width: 150px; margin-left: 10px">
        <el-option :label="t('list.isInvoice')" :value="true" />
        <el-option :label="t('list.notInvoice')" :value="false" />
      </el-select>
      <el-button style="margin-left: 10px" @click="loadData">{{ t('common.search') }}</el-button>
    </div>
    
    <el-table
      :data="invoices"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" align="left" />
      <el-table-column prop="id" label="ID" width="80" align="left" />
      <el-table-column :label="t('list.image')" width="100" align="left">
        <template #default="scope">
          <div 
            v-if="scope.row.image_url"
            class="thumbnail-wrapper"
            @click="openImageViewer(getImageIndex(scope.row.image_url))"
          >
            <el-image 
              :src="getImageUrl(scope.row.image_url)"
              fit="cover"
              style="width: 60px; height: 60px; cursor: pointer;"
            >
              <template #error>
                <div class="thumbnail-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </div>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column prop="transaction_reference" :label="t('list.transactionCode')" min-width="180" align="left" show-overflow-tooltip>
        <template #default="scope">
          <span v-if="scope.row.transaction_reference">{{ scope.row.transaction_reference }}</span>
          <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('list.transactionDate')" min-width="140" align="left">
        <template #default="scope">
          <span v-if="scope.row.transaction_date">{{ scope.row.transaction_date }}</span>
          <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('list.receiverAccount')" min-width="180" align="left" show-overflow-tooltip>
        <template #default="scope">
          <span v-if="scope.row.receiver_account">{{ scope.row.receiver_account }}</span>
          <span v-else-if="scope.row.receiver_account_name">{{ scope.row.receiver_account_name }}</span>
          <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('list.needsReview')" min-width="120" align="left">
        <template #default="scope">
          <el-tag :type="scope.row.needs_review ? 'danger' : 'success'">
            {{ scope.row.needs_review ? t('list.reviewYes') : t('list.reviewNo') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('list.amount')" min-width="150" align="left">
        <template #default="scope">
          <span v-if="scope.row.total_amount">{{ scope.row.currency || 'ETB' }} {{ scope.row.total_amount }}</span>
          <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="120" align="left" fixed="right">
        <template #default="scope">
          <el-button type="primary" link size="small" @click="showDetail(scope.row)">
            {{ t('common.detail') }}
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
            {{ t('common.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
    
    <el-dialog v-model="showDetailDialog" :title="t('common.detail')" width="500px">
      <div v-if="currentInvoice">
        <div v-if="currentInvoice.image_url" style="text-align: center; margin-bottom: 20px;">
          <el-image 
            :src="getImageUrl(currentInvoice.image_url)" 
            fit="contain"
            style="max-width: 100%; max-height: 350px; cursor: pointer;"
            @click="openImageViewer(getImageIndex(currentInvoice.image_url))"
          >
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>{{ t('list.imageLoadFailed') }}</span>
              </div>
            </template>
          </el-image>
        </div>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="ID">
            <span>{{ currentInvoice.id }}</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('list.transactionCode')">
            <span v-if="currentInvoice.transaction_reference">{{ currentInvoice.transaction_reference }}</span>
            <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('list.transactionDate')">
            <span v-if="currentInvoice.transaction_date">{{ currentInvoice.transaction_date }}</span>
            <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('list.receiverAccount')">
            <span v-if="currentInvoice.receiver_account">{{ currentInvoice.receiver_account }}</span>
            <span v-else-if="currentInvoice.receiver_account_name">{{ currentInvoice.receiver_account_name }}</span>
            <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
          </el-descriptions-item>
          <el-descriptions-item :label="t('list.needsReview')">
            <el-tag :type="currentInvoice.needs_review ? 'danger' : 'success'">
              {{ currentInvoice.needs_review ? t('list.reviewYes') : t('list.reviewNo') }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('list.amount')">
            <span v-if="currentInvoice.total_amount">{{ currentInvoice.currency || 'ETB' }} {{ currentInvoice.total_amount }}</span>
            <span v-else style="color: #999;">[{{ t('list.missing') }}]</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
    
    <el-image-viewer
      v-if="showImageViewer"
      :url-list="allImageUrls"
      :initial-index="currentImageIndex"
      @close="closeImageViewer"
      teleported
    />
  </el-card>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Refresh, Picture } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../services/api'

const { t } = useI18n()

const API_BASE = (import.meta.env?.VITE_API_URL && import.meta.env.VITE_API_URL.trim())
  ? import.meta.env.VITE_API_URL.replace(/\/+$/, '')
  : (window.location.origin + '/api')

const getImageUrl = (imagePath) => {
  if (!imagePath) return ''
  if (imagePath.startsWith('http')) return imagePath
  const filename = imagePath.split(/[/\\]/).pop()
  return `${API_BASE}/uploads/${filename}`
}

const invoices = ref([])
const loading = ref(false)
const selectedInvoices = ref([])
const showDetailDialog = ref(false)
const currentInvoice = ref(null)
const showImageViewer = ref(false)
const currentImageIndex = ref(0)

const allImageUrls = computed(() => {
  return invoices.value
    .filter(inv => inv.image_url)
    .map(inv => getImageUrl(inv.image_url))
})

const getImageIndex = (imagePath) => {
  const url = getImageUrl(imagePath)
  return allImageUrls.value.indexOf(url)
}

const openImageViewer = (index) => {
  currentImageIndex.value = index >= 0 ? index : 0
  showImageViewer.value = true
}

const closeImageViewer = () => {
  showImageViewer.value = false
}

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const filters = ref({
  status: null,
  isInvoice: null,
  dateRange: []
})

const exportFields = ref([
  'transaction_reference',
  'transaction_date',
  'receiver_account',
  'total_amount',
  'currency',
  'image_url'
])
const includeImages = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.getInvoiceList(
      pagination.value.page,
      pagination.value.pageSize,
      filters.value.status,
      filters.value.isInvoice,
      filters.value.dateRange
    )
    invoices.value = response.data.items
    pagination.value.total = response.data.total
  } catch (error) {
    console.error('Load error:', error)
    ElMessage.error(t('list.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedInvoices.value = selection
}

const showDetail = (invoice) => {
  currentInvoice.value = invoice
  showDetailDialog.value = true
}

const handleDelete = async (invoice) => {
  try {
    await ElMessageBox.confirm(t('list.confirmDelete'), t('common.confirm'), {
      type: 'warning'
    })
    await api.deleteInvoice(invoice.id)
    ElMessage.success(t('common.success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('common.failed'))
    }
  }
}

const handleDeleteAll = async () => {
  try {
    await ElMessageBox.confirm(
      t('list.confirmDeleteAll'),
      t('common.confirm'),
      {
        type: 'warning',
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      }
    )
    await api.deleteAllInvoices()
    ElMessage.success(t('common.success'))
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(t('common.failed'))
    }
  }
}

const exportSelected = async () => {
  if (selectedInvoices.value.length === 0) {
    ElMessage.warning(t('list.selectFirst'))
    return
  }
  
  try {
    const ids = selectedInvoices.value.map(inv => inv.id)
    const response = await api.exportInvoices(
      ids,
      false,
      exportFields.value,
      filters.value.dateRange,
      includeImages.value
    )
    downloadExcel(response.data, t('list.invoiceData') + '.xlsx')
    ElMessage.success(t('common.success'))
  } catch (error) {
    ElMessage.error(t('common.failed'))
  }
}

const exportAll = async () => {
  try {
    const response = await api.exportInvoices(
      null,
      true,
      exportFields.value,
      filters.value.dateRange,
      includeImages.value
    )
    downloadExcel(response.data, t('list.invoiceData') + '_' + t('list.all') + '.xlsx')
    ElMessage.success(t('common.success'))
  } catch (error) {
    ElMessage.error(t('common.failed'))
  }
}

const downloadExcel = (blob, filename) => {
  const fileBlob = blob instanceof Blob
    ? blob
    : new Blob([blob], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = window.URL.createObjectURL(fileBlob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
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

onMounted(() => {
  loadData()
})

defineExpose({ loadData })
</script>

<style scoped>
.list-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.list-card :deep(.el-card__header) {
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

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 200px;
  background: #f5f7fa;
  color: #909399;
}

.image-error .el-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.thumbnail-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: #f5f7fa;
  color: #909399;
}

.thumbnail-wrapper {
  display: inline-block;
  cursor: pointer;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.filter-bar {
  margin-bottom: 15px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.export-options {
  margin-top: 10px;
}
</style>

<style>
.el-image-viewer__wrapper {
  z-index: 3000 !important;
}
</style>
