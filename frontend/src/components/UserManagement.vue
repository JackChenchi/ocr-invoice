<template>
  <div class="user-card">
    <el-form :model="form" @submit.prevent>
      <el-form-item :label="t('user.username')">
        <el-input v-model="form.username" autocomplete="off" />
      </el-form-item>
      <el-form-item :label="t('user.password')">
        <el-input v-model="form.password" type="password" autocomplete="new-password" />
      </el-form-item>
      <el-form-item>
        <el-switch v-model="form.is_admin" :active-text="t('user.isAdmin')" />
      </el-form-item>
      <el-button type="primary" :loading="saving" @click="createUser">
        {{ t('user.create') }}
      </el-button>
    </el-form>

    <div class="user-list-title">{{ t('user.list') }}</div>
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="username" :label="t('user.username')" />
      <el-table-column prop="is_admin" :label="t('user.isAdmin')" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_admin ? 'success' : 'info'">
            {{ scope.row.is_admin ? t('common.yes') : t('common.no') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="120">
        <template #default="scope">
          <el-button type="danger" link size="small" @click="confirmDelete(scope.row)">
            {{ t('user.delete') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../services/api'

const { t } = useI18n()

const form = ref({
  username: '',
  password: '',
  is_admin: false
})

const saving = ref(false)
const users = ref([])

const createUser = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning(t('user.fillAll'))
    return
  }
  saving.value = true
  try {
    await api.createUser(form.value)
    ElMessage.success(t('common.success'))
    form.value.password = ''
    await loadUsers()
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || t('common.failed'))
  } finally {
    saving.value = false
  }
}

const loadUsers = async () => {
  try {
    const response = await api.listUsers()
    users.value = response.data.items || []
  } catch (error) {
    users.value = []
  }
}

const confirmDelete = async (user) => {
  try {
    await ElMessageBox.confirm(t('user.confirmDelete'), t('common.confirm'), { type: 'warning' })
    await api.deleteUser(user.id)
    ElMessage.success(t('common.success'))
    await loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || t('common.failed'))
    }
  }
}

defineExpose({ loadUsers })
</script>

<style scoped>
.user-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.user-list-title {
  font-weight: 600;
  margin-top: 8px;
}
</style>
