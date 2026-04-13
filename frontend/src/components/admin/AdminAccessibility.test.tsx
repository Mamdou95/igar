import { render, waitFor } from '@testing-library/react'
import type { ReactElement } from 'react'
import { describe, expect, it, vi } from 'vitest'
import axe from 'axe-core'
import { AdminUsersPage } from '../../pages/AdminUsersPage'
import { AdminRolesPage } from '../../pages/AdminRolesPage'
import { UserEditModal } from './UserEditModal'
import { AccessGroupsModal } from './AccessGroupsModal'
import '../../i18n'
import * as adminApi from '../../api/admin'

function renderWithAxe(ui: ReactElement) {
  return render(ui)
}

async function expectNoA11yViolations() {
  const results = await axe.run(document.body, {
    rules: {
      'color-contrast': { enabled: false },
    },
  })

  expect(results.violations).toEqual([])
}

vi.mock('../../api/admin', () => ({
  listUsers: vi.fn(),
  getUser: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deactivateUser: vi.fn(),
  resetUserPassword: vi.fn(),
  resetUserTwoFactor: vi.fn(),
  listRoles: vi.fn(),
  listPermissions: vi.fn(),
  listDocumentAccessGroups: vi.fn(),
  deleteRole: vi.fn(),
}))

describe('Admin accessibility', () => {
  it('AdminUsersPage has no obvious axe violations', async () => {
    vi.mocked(adminApi.listRoles).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 1, name: 'Admin', permissions: [] }],
    })
    vi.mocked(adminApi.listUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 7,
          username: 'alice',
          email: 'alice@example.com',
          first_name: 'Alice',
          last_name: 'Durand',
          is_active: true,
          is_staff: true,
          is_readonly: false,
          groups: [1],
          created_at: '2026-04-13T10:00:00Z',
          updated_at: '2026-04-13T10:00:00Z',
        },
      ],
    })

    renderWithAxe(<AdminUsersPage />)

    await waitFor(() => {
      expect(document.body.textContent).toContain('alice')
    })

    await expectNoA11yViolations()
  })

  it('AdminRolesPage has no obvious axe violations', async () => {
    vi.mocked(adminApi.listRoles).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 1, name: 'Admin', permissions: [1] }],
    })
    vi.mocked(adminApi.listPermissions).mockResolvedValue([
      { id: 1, name: 'View users', codename: 'view_user', app: 'auth' },
    ])
    vi.mocked(adminApi.listDocumentAccessGroups).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [{ id: 2, name: 'Finance', description: 'Finance', created_at: '2026-04-13T10:00:00Z' }],
    })

    renderWithAxe(<AdminRolesPage />)

    await waitFor(() => {
      expect(document.body.textContent).toContain('Admin')
    })

    await expectNoA11yViolations()
  })

  it('UserEditModal exposes a valid accessible form structure', async () => {
    renderWithAxe(
      <UserEditModal
        open
        loading={false}
        roles={[{ id: 1, name: 'Admin', permissions: [] }]}
        editingUser={null}
        onCancel={() => undefined}
        onSubmit={async () => undefined}
      />,
    )

    await expectNoA11yViolations()
  })

  it('AccessGroupsModal exposes a valid accessible form structure', async () => {
    renderWithAxe(
      <AccessGroupsModal
        open
        loading={false}
        editingRole={null}
        accessGroups={[
          { id: 1, name: 'Finance', description: 'Finance', created_at: '2026-04-13T10:00:00Z' },
        ]}
        onCancel={() => undefined}
        onSubmit={async () => undefined}
      />,
    )

    await expectNoA11yViolations()
  })
})
