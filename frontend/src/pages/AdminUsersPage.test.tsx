import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { AdminUsersPage } from './AdminUsersPage'
import * as adminApi from '../api/admin'
import '../i18n'

vi.mock('antd', async () => {
  const actual = await vi.importActual<typeof import('antd')>('antd')

  const MockTable = ({
    dataSource,
    columns,
  }: {
    dataSource: Array<{ id: number; username: string; email: string }>
    columns: Array<{ key?: string; render?: (value: unknown, row: unknown) => React.ReactNode }>
  }) => (
    <div>
      {dataSource.map((user) => (
        <div key={user.id}>
          <span>{user.username}</span>
          <span>{user.email}</span>
          <div>
            {columns
              .filter((column) => column.key === 'actions' && column.render)
              .map((column, index) => (
                <span key={`${user.id}-action-${index}`}>{column.render?.(null, user)}</span>
              ))}
          </div>
        </div>
      ))}
    </div>
  )

  return {
    ...actual,
    Table: MockTable,
    Popconfirm: ({ children, onConfirm }: { children: React.ReactNode; onConfirm?: () => void }) => (
      <div
        role="button"
        tabIndex={0}
        onClick={() => onConfirm?.()}
        onKeyDown={(event) => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault()
            onConfirm?.()
          }
        }}
      >
        {children}
      </div>
    ),
  }
})

vi.mock('../components/admin/UserEditModal', () => ({
  UserEditModal: ({
    open,
    editingUser,
    onSubmit,
  }: {
    open: boolean
    editingUser: { id: number } | null
    onSubmit: (values: Record<string, unknown>) => Promise<void>
  }) => (
    <div>
      <span>{open ? 'user-modal-open' : 'user-modal-closed'}</span>
      {open ? (
        <button
          type="button"
          onClick={() => {
            if (editingUser) {
              void onSubmit({ groups: [1, 2], is_readonly: false })
            } else {
              void onSubmit({
                username: 'new.user',
                email: 'new.user@example.com',
                password: 'StrongPass123!',
                groups: [1],
                is_active: true,
                is_readonly: false,
              })
            }
          }}
        >
          submit-user-modal
        </button>
      ) : null}
    </div>
  ),
}))

vi.mock('../api/admin', () => ({
  listUsers: vi.fn(),
  getUser: vi.fn(),
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deactivateUser: vi.fn(),
  resetUserPassword: vi.fn(),
  resetUserTwoFactor: vi.fn(),
  listRoles: vi.fn(),
}))

describe('AdminUsersPage', () => {
  beforeEach(() => {
    vi.resetAllMocks()

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

    vi.mocked(adminApi.getUser).mockResolvedValue({
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
    })

    vi.mocked(adminApi.createUser).mockResolvedValue({
      id: 11,
      username: 'new.user',
      email: 'new.user@example.com',
      first_name: '',
      last_name: '',
      is_active: true,
      is_staff: false,
      is_readonly: false,
      groups: [1],
      created_at: '2026-04-13T10:00:00Z',
      updated_at: '2026-04-13T10:00:00Z',
    })

    vi.mocked(adminApi.updateUser).mockResolvedValue({
      id: 7,
      username: 'alice',
      email: 'alice@example.com',
      first_name: 'Alice',
      last_name: 'Durand',
      is_active: true,
      is_staff: true,
      is_readonly: false,
      groups: [1, 2],
      created_at: '2026-04-13T10:00:00Z',
      updated_at: '2026-04-13T10:00:00Z',
    })

    vi.mocked(adminApi.deactivateUser).mockResolvedValue({
      id: 7,
      username: 'alice',
      email: 'alice@example.com',
      first_name: 'Alice',
      last_name: 'Durand',
      is_active: false,
      is_staff: true,
      is_readonly: false,
      groups: [1],
      created_at: '2026-04-13T10:00:00Z',
      updated_at: '2026-04-13T10:00:00Z',
    })
  })

  it('affiche la table des utilisateurs', async () => {
    render(<AdminUsersPage />)

    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })
    expect(screen.getByText('alice@example.com')).toBeInTheDocument()
  })

  it('ouvre la modale de creation', async () => {
    render(<AdminUsersPage />)

    fireEvent.click(screen.getByRole('button', { name: /Creer un utilisateur/i }))

    await waitFor(() => {
      expect(screen.getByText('user-modal-open')).toBeInTheDocument()
    })
  })

  it('soumet la creation utilisateur depuis la modale', async () => {
    render(<AdminUsersPage />)

    fireEvent.click(screen.getByRole('button', { name: /Creer un utilisateur/i }))

    await waitFor(() => {
      expect(screen.getByText('submit-user-modal')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText('submit-user-modal'))

    await waitFor(() => {
      expect(adminApi.createUser).toHaveBeenCalledWith(
        expect.objectContaining({
          username: 'new.user',
          groups: [1],
        }),
      )
    })
  })

  it('met a jour les groupes lors de la modification utilisateur', async () => {
    render(<AdminUsersPage />)

    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole('button', { name: /Modifier/i }))

    await waitFor(() => {
      expect(adminApi.getUser).toHaveBeenCalledWith(7)
    })

    await waitFor(() => {
      expect(screen.getByText('submit-user-modal')).toBeInTheDocument()
    })
    fireEvent.click(screen.getByText('submit-user-modal'))

    await waitFor(() => {
      expect(adminApi.updateUser).toHaveBeenCalledWith(
        7,
        expect.objectContaining({
          groups: [1, 2],
        }),
      )
    })
  })

  it('demande confirmation de desactivation puis appelle API', async () => {
    render(<AdminUsersPage />)

    await waitFor(() => {
      expect(screen.getByText('alice')).toBeInTheDocument()
    })

    fireEvent.click(screen.getAllByRole('button', { name: /Desactiver/i })[0])

    await waitFor(() => {
      expect(adminApi.deactivateUser).toHaveBeenCalledWith(7)
    })
  })

  it('desactive le bouton modifier pour un utilisateur en lecture seule', async () => {
    vi.mocked(adminApi.listUsers).mockResolvedValue({
      count: 1,
      next: null,
      previous: null,
      results: [
        {
          id: 9,
          username: 'readonly-user',
          email: 'readonly@example.com',
          first_name: 'Read',
          last_name: 'Only',
          is_active: true,
          is_staff: false,
          is_readonly: true,
          groups: [1],
          created_at: '2026-04-13T10:00:00Z',
          updated_at: '2026-04-13T10:00:00Z',
        },
      ],
    })

    render(<AdminUsersPage />)

    await waitFor(() => {
      expect(screen.getByText('readonly-user')).toBeInTheDocument()
    })
    expect(screen.getByRole('button', { name: /Modifier/i })).toBeDisabled()
  })
})
