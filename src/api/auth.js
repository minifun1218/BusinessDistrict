import { http } from '../utils/request'

// 认证相关API
export const authApi = {
  // 登录
  login(params) {
    return http.post('/auth/login', params)
  },

  // 注册
  register(params) {
    return http.post('/auth/register', params)
  },

  // 刷新token
  refreshToken(refreshToken) {
    return http.post('/auth/refresh', { refreshToken })
  },

  // 退出登录
  logout() {
    return http.post('/auth/logout')
  },

  // 获取用户信息
  getUserInfo() {
    return http.get('/auth/user')
  },

  // 更新用户信息
  updateUserInfo(params) {
    return http.put('/auth/user', params)
  },

  // 修改密码
  changePassword(params) {
    return http.put('/auth/password', params)
  },

  // 发送验证码
  sendVerificationCode(phone, type = 'login') {
    return http.post('/auth/verification-code', { phone, type })
  },

  // 验证手机号
  verifyPhone(params) {
    return http.post('/auth/verify-phone', params)
  },

  // 绑定第三方账号
  bindThirdParty(params) {
    return http.post('/auth/bind-third-party', params)
  },

  // 解绑第三方账号
  unbindThirdParty(provider) {
    return http.delete(`/auth/bind-third-party/${provider}`)
  },

  // 获取验证码图片
  getCaptcha() {
    return http.get('/auth/captcha')
  },

  // 找回密码
  forgotPassword(params) {
    return http.post('/auth/forgot-password', params)
  },

  // 重置密码
  resetPassword(params) {
    return http.post('/auth/reset-password', params)
  }
}
