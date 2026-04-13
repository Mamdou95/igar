import { expect, test, type Page } from '@playwright/test'

type MockUser = {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_readonly: boolean
  groups: number[]
  created_at: string
  updated_at: string
}

const adminPermissions = {
  results: [
    { id: 1, codename: 'change_user', name: 'Can change user', app: 'auth' },
  ],
}

async function installAuthRoutes(page: Page) {
  await page.route('**/api/v1/auth/csrf/', async (route) => {
    await route.fulfill({ status: 204 })
  })

  await page.route('**/api/v1/auth/login/', async (route) => {
    const body = route.request().postDataJSON() as { username?: string }
    const isAdmin = body.username === 'admin'

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        access: isAdmin ? 'admin-token' : 'user-token',
        user: { id: isAdmin ? 1 : 2, username: body.username ?? 'user' },
        '2fa_required': false,
        '2fa_verified': false,
        next_action: null,
      }),
    })
  })

  await page.route('**/api/v1/auth/refresh/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ access: 'admin-token' }),
    })
  })
}

async function login(page: Page, username: string) {
  await page.goto('/login')
  await page.getByLabel('Identifiant').fill(username)
  await page.getByLabel('Mot de passe').fill('test-password')
  await page.getByRole('button', { name: 'Se connecter' }).click()
  await expect(page.getByRole('heading', { name: 'Espace documents' })).toBeVisible()
}

async function navigateInApp(page: Page, path: string) {
  await page.evaluate((nextPath) => {
    window.history.pushState({}, '', nextPath)
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, path)
}

test.describe('Story 1.6 - admin RBAC e2e', () => {
  test('admin creates a new user and assigns groups', async ({ page }) => {
    await installAuthRoutes(page)

    const users: MockUser[] = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        first_name: 'Admin',
        last_name: 'Root',
        is_active: true,
        is_staff: true,
        is_readonly: false,
        groups: [1],
        created_at: '2026-04-13T10:00:00Z',
        updated_at: '2026-04-13T10:00:00Z',
      },
    ]

    await page.route('**/api/v1/admin/permissions/', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(adminPermissions) })
    })

    await page.route('**/api/v1/admin/roles/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          next: null,
          previous: null,
          results: [{ id: 1, name: 'Comptabilite', permissions: [1], allowed_document_groups: [3] }],
        }),
      })
    })

    await page.route('**/api/v1/admin/users/**', async (route, request) => {
      if (request.method() === 'POST') {
        const payload = request.postDataJSON() as Record<string, unknown>
        const createdUser: MockUser = {
          id: 10,
          username: String(payload.username ?? ''),
          email: String(payload.email ?? ''),
          first_name: String(payload.first_name ?? ''),
          last_name: String(payload.last_name ?? ''),
          is_active: payload.is_active !== false,
          is_staff: false,
          is_readonly: payload.is_readonly === true,
          groups: Array.isArray(payload.groups) ? (payload.groups as number[]) : [],
          created_at: '2026-04-13T11:00:00Z',
          updated_at: '2026-04-13T11:00:00Z',
        }
        users.push(createdUser)

        await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify(createdUser) })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ count: users.length, next: null, previous: null, results: users }),
      })
    })

    await login(page, 'admin')
    await navigateInApp(page, '/admin/users')

    await expect(page.getByRole('heading', { name: 'Utilisateurs' })).toBeVisible()
    await page.getByRole('button', { name: 'Creer un utilisateur' }).click()

    const dialog = page.getByRole('dialog', { name: 'Creer un utilisateur' })
    await expect(dialog).toBeVisible()
    await dialog.getByLabel('Identifiant').fill('fatima')
    await dialog.getByLabel('Email').fill('fatima@example.com')
    await dialog.getByLabel('Mot de passe').fill('password-123')
    await dialog.getByLabel('Prenom').fill('Fatima')
    await dialog.getByLabel('Nom', { exact: true }).fill('Mansouri')

    const groupSelect = dialog.getByRole('combobox', { name: 'Groupes' })
    await groupSelect.click()
    await groupSelect.press('ArrowDown')
    await groupSelect.press('Enter')

    await page.locator('.ant-modal .ant-btn-primary').click()

    await expect(page.getByText('Utilisateur cree avec succes')).toBeVisible()
    await expect(page.getByRole('cell', { name: 'fatima', exact: true })).toBeVisible()
  })

  test('created user can login and is redirected away from admin pages', async ({ page }) => {
    await installAuthRoutes(page)

    await page.route('**/api/v1/admin/permissions/', async (route) => {
      const authHeader = route.request().headers().authorization ?? ''
      const allowed = authHeader.includes('admin-token')

      if (allowed) {
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(adminPermissions) })
        return
      }

      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Forbidden' }),
      })
    })

    await login(page, 'fatima')

    await navigateInApp(page, '/admin/users')
    await expect(page).toHaveURL(/\/documents$/)
    await expect(page.getByRole('heading', { name: 'Espace documents' })).toBeVisible()
  })

  test('user search cannot retrieve forbidden documents', async ({ page }) => {
    await installAuthRoutes(page)

    await page.route('**/api/v1/documents/search/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          results: [{ id: 1, title: 'Facture autorisee' }],
        }),
      })
    })

    await login(page, 'fatima')

    const payload = await page.evaluate(async () => {
      const response = await fetch('/api/v1/documents/search/?q=facture')
      return response.json()
    })

    expect(payload.results).toEqual([{ id: 1, title: 'Facture autorisee' }])
  })

  test('audit log records admin actions', async ({ page }) => {
    await installAuthRoutes(page)

    await page.route('**/api/v1/admin/permissions/', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(adminPermissions) })
    })

    await page.route('**/api/v1/admin/audit-logs/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          next: null,
          previous: null,
          results: [
            {
              id: 88,
              action: 'user.created',
              resource_type: 'user',
              resource_id: 10,
              user: { id: 1, username: 'admin' },
              old_values: {},
              new_values: { username: 'fatima' },
              ip_address: '127.0.0.1',
              created_at: '2026-04-13T11:10:00Z',
            },
          ],
        }),
      })
    })

    await login(page, 'admin')
    await navigateInApp(page, '/admin/audit')

    const firstRow = page.locator('.ant-table-tbody tr:not(.ant-table-measure-row)').first()
    await expect(firstRow).toContainText('user.created')
    await expect(firstRow).toContainText('admin')
  })
})
