import type { ThemeConfig } from 'antd'

export const oceanDeepTheme: ThemeConfig = {
  token: {
    colorPrimary: '#1B3A5C',
    colorInfo: '#1B3A5C',
    colorSuccess: '#10B981',
    colorWarning: '#F59E0B',
    colorError: '#DC2626',
    colorBgBase: '#F8FAFC',
    colorBgContainer: '#FFFFFF',
    colorBorder: '#D1DEE8',
    colorText: '#0F2A43',
    colorTextHeading: '#0B2239',
    borderRadius: 8,
    fontFamily: 'Inter, sans-serif',
    wireframe: false,
  },
  components: {
    Layout: {
      bodyBg: '#EAF1F7',
      headerBg: '#FFFFFF',
      siderBg: '#0E2B47',
      triggerBg: '#113658',
    },
    Card: {
      colorBorderSecondary: '#D1DEE8',
      borderRadiusLG: 12,
      boxShadowTertiary: '0 8px 24px rgba(15, 42, 67, 0.08)',
    },
    Table: {
      headerBg: '#E8F0F8',
      headerColor: '#0F2A43',
      rowHoverBg: '#F2F7FC',
      borderColor: '#D1DEE8',
    },
    Input: {
      activeBorderColor: '#1B3A5C',
      hoverBorderColor: '#2A4D72',
    },
    Select: {
      optionSelectedBg: '#E8F0F8',
      activeBorderColor: '#1B3A5C',
    },
    Button: {
      primaryShadow: '0 8px 18px rgba(27, 58, 92, 0.25)',
    },
  },
}
