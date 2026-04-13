import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { UserEditModal } from './UserEditModal'
import '../../i18n'

describe('UserEditModal', () => {
  it('affiche les champs du formulaire', () => {
    render(
      <UserEditModal
        open
        loading={false}
        roles={[{ id: 1, name: 'Admin', permissions: [] }]}
        editingUser={null}
        onCancel={() => {}}
        onSubmit={async () => {}}
      />,
    )

    expect(screen.getByLabelText('Identifiant')).toBeInTheDocument()
    expect(screen.getByLabelText('Email')).toBeInTheDocument()
    expect(screen.getByLabelText('Mot de passe')).toBeInTheDocument()
    expect(screen.getByLabelText('Groupes')).toBeInTheDocument()
  })

  it('exige au moins un groupe', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    render(
      <UserEditModal
        open
        loading={false}
        roles={[{ id: 1, name: 'Admin', permissions: [] }]}
        editingUser={null}
        onCancel={() => {}}
        onSubmit={onSubmit}
      />,
    )

    fireEvent.change(screen.getByLabelText('Identifiant'), { target: { value: 'alice' } })
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'alice@example.com' } })
    fireEvent.change(screen.getByLabelText('Mot de passe'), { target: { value: 'StrongPass123!' } })

    fireEvent.click(screen.getByRole('button', { name: 'OK' }))

    await waitFor(() => {
      expect(screen.getAllByText('Selectionnez au moins un groupe').length).toBeGreaterThan(0)
    })
    expect(onSubmit).not.toHaveBeenCalled()
  })
})
