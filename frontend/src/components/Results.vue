<template>
  <div class="results-container">
    <el-table :data="tasks" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="file_name" label="File Name" width="180" />
      <el-table-column prop="status" label="Status" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Time" width="160">
        <template #default="scope">
          {{ scope.row.transaction_date }} {{ scope.row.transaction_time }}
        </template>
      </el-table-column>
      <el-table-column prop="transaction_reference" label="Reference" width="150" />
      <el-table-column label="Amount" width="150">
        <template #default="scope">
          <span v-if="scope.row.total_amount">{{ scope.row.currency || '' }} {{ scope.row.total_amount }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="80">
        <template #default="scope">
          <el-button size="small" @click="viewDetails(scope.row)">View</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailsVisible" title="OCR Result Details" width="50%">
      <div v-if="currentTask">
        <h3>{{ currentTask.file_name }}</h3>
        <p><strong>Status:</strong> <el-tag :type="getStatusType(currentTask.status)">{{ currentTask.status }}</el-tag></p>
        
        <div style="margin-top: 20px;">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="Time">{{ currentTask.transaction_date }} {{ currentTask.transaction_time }}</el-descriptions-item>
            <el-descriptions-item label="Reference">{{ currentTask.transaction_reference }}</el-descriptions-item>
            <el-descriptions-item label="Amount">{{ currentTask.currency }} {{ currentTask.total_amount }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div v-if="currentTask.error_msg" style="color: red; margin-top: 10px;">
          <strong>Error:</strong> {{ currentTask.error_msg }}
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '../services/api'

const props = defineProps({
  newTasks: {
    type: Array,
    default: () => []
  }
})

const tasks = ref([])
const detailsVisible = ref(false)
const currentTask = ref(null)
let pollTimer = null

const fetchTasks = async () => {
  try {
    const response = await api.getResults(0, 50)
    tasks.value = response.data
  } catch (error) {
    console.error("Failed to fetch tasks", error)
  }
}

const getStatusType = (status) => {
  switch (status) {
    case 'completed': return 'success'
    case 'processing': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const viewDetails = (task) => {
  currentTask.value = task
  detailsVisible.value = true
}

const startPolling = () => {
  pollTimer = setInterval(fetchTasks, 3000)
}

onMounted(() => {
  fetchTasks()
  startPolling()
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

watch(() => props.newTasks, (newVal) => {
  if (newVal && newVal.length > 0) {
    fetchTasks()
  }
}, { deep: true })
</script>

<style scoped>
.results-container {
  margin-top: 20px;
}
</style>
