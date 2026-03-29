import axios, { type InternalAxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as (InternalAxiosRequestConfig & { _retry?: boolean }) | undefined
    const path = originalRequest?.url ?? ''
    const isAuthEndpoint = path.includes('/auth/login') || path.includes('/auth/refresh')

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true

      try {
        const refreshResponse = await apiClient.post('/auth/refresh/')
        const refreshedAccessToken = refreshResponse.data?.access as string | undefined

        if (refreshedAccessToken) {
          useAuthStore.getState().setAccessToken(refreshedAccessToken)
          originalRequest.headers.Authorization = `Bearer ${refreshedAccessToken}`
          return apiClient(originalRequest)
        }
      } catch {
        useAuthStore.getState().clear()
      }
    }

    return Promise.reject(error)
  },
)
