<template>
  <el-upload
    class="upload-demo"
    drag
    action="#"
    :http-request="uploadFile"
    :before-upload="beforeUpload"
    multiple
    list-type="picture"
    :show-file-list="false"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      Drop file here or <em>click to upload</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        jpg/png files with a size less than 10MB
      </div>
    </template>
  </el-upload>
</template>

<script setup>
import { UploadFilled } from '@element-plus/icons-vue'
import api from '../services/api'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['upload-success'])

const beforeUpload = (rawFile) => {
  if (rawFile.size / 1024 / 1024 > 10) {
    ElMessage.error('Avatar picture size can not exceed 10MB!')
    return false
  }
  return true
}

const uploadFile = async (param) => {
  try {
    const response = await api.uploadImage(param.file)
    // response.data is the OCRResult object
    emit('upload-success', response.data)
  } catch (error) {
    console.error(error)
    ElMessage.error('Upload failed')
  }
}
</script>

<style scoped>
.upload-demo {
  width: 100%;
}
</style>
