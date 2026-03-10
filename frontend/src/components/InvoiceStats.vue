<template>
  <el-card class="stats-card">
    <template #header>
      <div class="card-header">
        <span>{{ t('stats.title') }}</span>
        <el-button link @click="loadStats">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </template>
    
    <el-row :gutter="20" v-if="stats">
      <el-col :span="6">
        <div class="stat-item">
          <div class="stat-value">{{ stats.total_count }}</div>
          <div class="stat-label">{{ t('stats.totalCount') }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item success">
          <div class="stat-value">{{ stats.completed_count }}</div>
          <div class="stat-label">{{ t('stats.completedCount') }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item primary">
          <div class="stat-value">{{ formatCurrency(stats.total_amount) }}</div>
          <div class="stat-label">{{ t('stats.totalAmount') }}</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-item warning">
          <div class="stat-value">{{ formatCurrency(stats.total_tax) }}</div>
          <div class="stat-label">{{ t('stats.totalTax') }}</div>
        </div>
      </el-col>
    </el-row>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Refresh } from '@element-plus/icons-vue'
import api from '../services/api'

const { t } = useI18n()

const stats = ref(null)

const loadStats = async () => {
  try {
    const response = await api.getStatistics()
    stats.value = response.data
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return amount.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

onMounted(() => {
  loadStats()
})

defineExpose({ loadStats })
</script>

<style scoped>
.stats-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.stats-card :deep(.el-card__header) {
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

.stat-item {
  text-align: center;
  padding: 20px 15px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 10px;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-item.success {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.stat-item.primary {
  background: linear-gradient(135deg, #ecf5ff 0%, #d9ecff 100%);
}

.stat-item.warning {
  background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-item.success .stat-value {
  color: #67c23a;
}

.stat-item.primary .stat-value {
  color: #409eff;
}

.stat-item.warning .stat-value {
  color: #e6a23c;
}

.stat-label {
  margin-top: 10px;
  font-size: 14px;
  color: #909399;
  font-weight: 500;
}
</style>
