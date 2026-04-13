import { LogoutOutlined, SearchOutlined } from '@ant-design/icons'
import { Badge, Button, Input, Layout, Menu, Typography } from 'antd'
import { NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { apiClient } from '../api/client'
import { useAuthStore } from '../stores/authStore.ts'
import { useUiStore } from '../stores/uiStore.ts'
import { useCaptureStore } from '../stores/captureStore'

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
  const importPendingCount = useCaptureStore(
    (state) => state.files.filter((file) => file.status === 'queued' || file.status === 'uploading').length,
  )

  const menuItems = menuRoutes.map((item) => ({
    key: item.path,
    label: (
      <NavLink to={item.path} aria-label={t(item.name)}>
        {item.path === '/import' ? (
          <span data-testid="import-badge">
            <Badge count={importPendingCount}>{t(item.name)}</Badge>
          </span>
        ) : (
          t(item.name)
        )}
      </NavLink>
    ),
  }))

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
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Sider
        collapsible
        collapsed={sidebarCollapsed}
        onCollapse={setSidebarCollapsed}
        width={240}
        theme="dark"
      >
        <div style={{ padding: '20px 16px 12px' }}>
          <Typography.Title level={4} style={{ color: '#ffffff', margin: 0 }}>
            Igar
          </Typography.Title>
          {!sidebarCollapsed ? (
            <Typography.Text style={{ color: 'rgba(255, 255, 255, 0.72)' }}>
              {t('layout.searchPlaceholder')}
            </Typography.Text>
          ) : null}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
        />
      </Layout.Sider>
      <Layout>
        <Layout.Header style={{ display: 'flex', alignItems: 'center', gap: 12, background: '#fff', padding: '0 24px' }}>
          <Input
            prefix={<SearchOutlined />}
            placeholder={t('layout.searchPlaceholder')}
            style={{ width: 260 }}
          />
          <div style={{ marginLeft: 'auto' }}>
            <Button key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
              {t('layout.logout')}
            </Button>
          </div>
        </Layout.Header>
        <Layout.Content style={{ padding: 24, background: '#f8fafc' }}>
          <div className="igar-content">
            <Outlet />
          </div>
        </Layout.Content>
      </Layout>
    </Layout>
  )
}
