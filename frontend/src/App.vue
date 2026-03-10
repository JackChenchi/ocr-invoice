<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-left">
            <el-icon class="header-icon"><Document /></el-icon>
            <h1>{{ t('header.title') }}</h1>
          </div>
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
      </el-header>
      <el-main>
        <el-row :gutter="20" justify="center">
          <el-col :span="22">
            <InvoiceStats ref="statsRef" />
          </el-col>
        </el-row>
        <el-row :gutter="20" justify="center">
          <el-col :span="22">
            <InvoiceUpload @upload-success="handleUploadSuccess" />
          </el-col>
        </el-row>
        <el-row :gutter="20" justify="center">
          <el-col :span="22">
            <InvoiceList ref="listRef" />
          </el-col>
        </el-row>
      </el-main>
      <el-footer>
        <div class="footer-content">
          <span>© 2024 Invoice Recognition System</span>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowDown, Document, Setting } from '@element-plus/icons-vue'
import InvoiceStats from './components/InvoiceStats.vue'
import InvoiceUpload from './components/InvoiceUpload.vue'
import InvoiceList from './components/InvoiceList.vue'

const { t, locale } = useI18n()

const statsRef = ref()
const listRef = ref()

const currentLangLabel = computed(() => {
  return locale.value === 'zh' ? '中文' : 'English'
})

const changeLanguage = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
}

const handleUploadSuccess = () => {
  listRef.value?.loadData()
  statsRef.value?.loadStats()
}
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
