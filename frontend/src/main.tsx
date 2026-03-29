import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ConfigProvider } from 'antd'
import './index.css'
import App from './App.tsx'
import './i18n'
import { oceanDeepTheme } from './theme/oceanDeep'

const queryClient = new QueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ConfigProvider componentSize="small" theme={oceanDeepTheme}>
        <App />
      </ConfigProvider>
    </QueryClientProvider>
  </StrictMode>,
)
