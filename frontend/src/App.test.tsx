import { render, screen } from '@testing-library/react'
import { ConfigProvider } from 'antd'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { oceanDeepTheme } from './theme/oceanDeep'
import { DocumentsPage } from './pages/DocumentsPage'
import './i18n'

describe('App smoke', () => {
  it('renders documents page placeholder', () => {
    const queryClient = new QueryClient()

    render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <ConfigProvider componentSize="small" theme={oceanDeepTheme}>
            <DocumentsPage />
          </ConfigProvider>
        </QueryClientProvider>
      </MemoryRouter>,
    )

    expect(screen.getByText('Espace documents')).toBeInTheDocument()
  })
})
