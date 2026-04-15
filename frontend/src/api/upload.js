import request from '../utils/request'

export const uploadApi = {
  // 上传单张图片
  uploadImage(file) {
    const formData = new FormData()
    formData.append('file', file)

    return request.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 批量上传图片
  uploadImages(files) {
    const formData = new FormData()
    files.forEach((file, index) => {
      formData.append('files', file)
    })

    return request.post('/api/upload/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // 删除图片
  deleteImage(filename) {
    return request.delete(`/api/upload/image/${filename}`)
  }
}
