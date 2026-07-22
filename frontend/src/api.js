import axios from 'axios'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api' })
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
api.interceptors.response.use((r) => r, async (error) => {
  const original = error.config
  if (error.response?.status === 401 && !original._retry && localStorage.getItem('refresh_token')) {
    original._retry = true
    try {
      const { data } = await axios.post(`${api.defaults.baseURL}/auth/token/refresh/`, { refresh: localStorage.getItem('refresh_token') })
      localStorage.setItem('access_token', data.access); original.headers.Authorization = `Bearer ${data.access}`
      return api(original)
    } catch { localStorage.removeItem('access_token'); localStorage.removeItem('refresh_token') }
  }
  return Promise.reject(error)
})
export default api

