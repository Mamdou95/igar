import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { AdminPermissionGuard } from './AdminPermissionGuard'
import * as adminApi from '../api/admin'

vi.mock('../api/admin', () => ({
  listPermissions: vi.fn(),
}))

describe('AdminPermissionGuard', () => {
  it('autorise l acces quand la verification de permission reussit', async () => {
    vi.mocked(adminApi.listPermissions).mockResolvedValue([])

    render(
      <MemoryRouter initialEntries={['/admin/users']}>
        <Routes>
          <Route path="/documents" element={<div>documents</div>} />
          <Route element={<AdminPermissionGuard />}>
            <Route path="/admin/users" element={<div>zone-admin</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('zone-admin')).toBeInTheDocument()
    })
  })

  it('redirige vers documents si la verification echoue', async () => {
    vi.mocked(adminApi.listPermissions).mockRejectedValue(new Error('forbidden'))

    render(
      <MemoryRouter initialEntries={['/admin/users']}>
        <Routes>
          <Route path="/documents" element={<div>documents</div>} />
          <Route element={<AdminPermissionGuard />}>
            <Route path="/admin/users" element={<div>zone-admin</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByText('documents')).toBeInTheDocument()
    })
  })
})
