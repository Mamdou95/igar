import { LogoutOutlined, SearchOutlined } from '@ant-design/icons'
import { ProLayout } from '@ant-design/pro-components'
import { Button, Input } from 'antd'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../api/client'
import { useAuthStore } from '../stores/authStore.ts'
import { useUiStore } from '../stores/uiStore.ts'

const menuRoutes = [
  { path: '/documents', name: 'routes.documents' },
  { path: '/import', name: 'routes.import' },
  { path: '/conformite', name: 'routes.conformite' },
  { path: '/admin', name: 'routes.admin' },
]

export function AppLayout() {
  const { t } = useTranslation()
  const location = useLocation()
  const navigate = useNavigate()
  const clearAuth = useAuthStore((state) => state.clear)
  const sidebarCollapsed = useUiStore((state) => state.sidebarCollapsed)
  const setSidebarCollapsed = useUiStore((state) => state.setSidebarCollapsed)

  const handleLogout = async () => {
    try {
      await apiClient.get('/auth/csrf/')
      await apiClient.post('/auth/logout/')
    } catch {
      // Even if backend logout fails, local state must be cleared to prevent stale session.
    } finally {
      clearAuth()
      navigate('/login', { replace: true })
    }
  }

  return (
    <ProLayout
      title="Igar"
      fixedHeader
      siderWidth={220}
      collapsed={sidebarCollapsed}
      onCollapse={setSidebarCollapsed}
      location={{ pathname: location.pathname }}
      route={{ routes: menuRoutes }}
      menuItemRender={(item, dom) => (
        <a href={item.path} aria-label={String(item.name)}>
          {dom}
        </a>
      )}
      menu={{
        locale: false,
      }}
      postMenuData={(menuData) =>
        (menuData ?? []).map((item) => ({
          ...item,
          name: t(String(item.name)),
        }))
      }
      actionsRender={() => [
        <Input
          key="header-search"
          prefix={<SearchOutlined />}
          placeholder={t('layout.searchPlaceholder')}
          style={{ width: 240 }}
        />,
        <Button key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
          {t('layout.logout')}
        </Button>,
      ]}
      contentStyle={{ background: '#f8fafc' }}
    >
      <div className="igar-content">
        <Outlet />
      </div>
    </ProLayout>
  )
}
