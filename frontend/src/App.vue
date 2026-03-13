<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-left">
            <el-icon class="header-icon"><Document /></el-icon>
            <h1>{{ t('header.title') }}</h1>
          </div>
          <div class="header-actions">
            <el-button v-if="isAuthed && isAdmin" plain @click="showUserDialog = true">
              {{ t('user.manage') }}
            </el-button>
            <el-button v-if="isAuthed" type="warning" plain @click="handleLogout">
              {{ t('auth.logout') }}
            </el-button>
            <el-dropdown @command="changeLanguage" trigger="click">
              <el-button type="primary" plain class="lang-btn">
                <el-icon><Setting /></el-icon>
                {{ currentLangLabel }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="zh" :class="{ active: locale === 'zh' }">
                    <span class="lang-option">🇨🇳 中文</span>
                  </el-dropdown-item>
                  <el-dropdown-item command="en" :class="{ active: locale === 'en' }">
                    <span class="lang-option">🇺🇸 English</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <el-row v-if="isAuthed" :gutter="20" justify="center">
          <el-col :span="22">
            <InvoiceUpload @upload-success="handleUploadSuccess" />
          </el-col>
        </el-row>
        <el-row v-if="isAuthed" :gutter="20" justify="center">
          <el-col :span="22">
            <InvoiceList ref="listRef" />
          </el-col>
        </el-row>
        <div v-else class="login-overlay">
          <el-card class="login-card">
            <h2>{{ t('auth.title') }}</h2>
            <el-form :model="loginForm" @submit.prevent>
              <el-form-item :label="t('auth.username')">
                <el-input v-model="loginForm.username" autocomplete="username" />
              </el-form-item>
              <el-form-item :label="t('auth.password')">
                <el-input v-model="loginForm.password" type="password" autocomplete="current-password" />
              </el-form-item>
              <el-button type="primary" :loading="loginLoading" @click="handleLogin">
                {{ t('auth.login') }}
              </el-button>
            </el-form>
          </el-card>
        </div>
      </el-main>
      <el-footer>
        <div class="footer-content">
          <span>© 2024 神眼系统</span>
        </div>
      </el-footer>
    </el-container>
  </div>
  <el-dialog v-model="showUserDialog" :title="t('user.title')" width="520px" @opened="userRef?.loadUsers()">
    <UserManagement ref="userRef" />
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDown, Document, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import InvoiceUpload from './components/InvoiceUpload.vue'
import InvoiceList from './components/InvoiceList.vue'
import UserManagement from './components/UserManagement.vue'
import api from './services/api'

const { t, locale } = useI18n()

const listRef = ref()
const isAuthed = ref(false)
const isAdmin = ref(false)
const loginLoading = ref(false)
const loginForm = ref({
  username: '',
  password: ''
})
const showUserDialog = ref(false)
const userRef = ref()

const currentLangLabel = computed(() => {
  return locale.value === 'zh' ? '中文' : 'English'
})

const changeLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
}

const handleUploadSuccess = () => {
  listRef.value?.loadData()
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) return
  loginLoading.value = true
  try {
    const response = await api.login(loginForm.value.username, loginForm.value.password)
    localStorage.setItem('auth_token', response.data.access_token)
    isAuthed.value = true
    try {
      const me = await api.getCurrentUser()
      isAdmin.value = !!me.data?.is_admin
    } catch (error) {
      isAdmin.value = false
    }
    loginForm.value.password = ''
    handleUploadSuccess()
  } catch (error) {
    ElMessage.error(t('auth.loginFailed'))
  } finally {
    loginLoading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('auth_token')
  isAuthed.value = false
  isAdmin.value = false
}

onMounted(async () => {
  window.addEventListener('auth:logout', handleLogout)
  const token = localStorage.getItem('auth_token')
  if (token) {
    try {
      const me = await api.getCurrentUser()
      isAuthed.value = true
      isAdmin.value = !!me.data?.is_admin
    } catch (error) {
      localStorage.removeItem('auth_token')
      isAuthed.value = false
      isAdmin.value = false
    }
  }
})
</script>

<style>
.common-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  height: auto !important;
  padding: 20px 40px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  font-size: 28px;
}

.el-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.lang-btn {
  background: rgba(255, 255, 255, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  color: white !important;
}

.lang-btn:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  border-color: rgba(255, 255, 255, 0.5) !important;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.lang-option {
  font-size: 14px;
}

.el-dropdown-menu__item.active {
  color: #409eff;
  font-weight: bold;
  background-color: #ecf5ff;
}

.el-main {
  padding: 30px 40px;
  background-color: #f0f2f5;
  flex: 1;
}

.login-overlay {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}

.login-card {
  width: 360px;
}

.el-footer {
  background-color: #fff;
  padding: 16px 40px;
  text-align: center;
  border-top: 1px solid #ebeef5;
}

.footer-content {
  color: #909399;
  font-size: 14px;
}
</style>
