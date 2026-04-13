import { expect, test } from '@playwright/test'

type MockUploadFile = {
  name: string
  type: string
  content: string
}

test.describe('Story 2.1 - import flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/v1/auth/csrf/', async (route) => {
      await route.fulfill({ status: 204 })
    })

    await page.route('**/api/v1/auth/login/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access: 'test-access-token',
          user: { id: 1, username: 'fatima' },
          '2fa_required': false,
          '2fa_verified': false,
          next_action: null,
        }),
      })
    })

    await page.route('http://localhost/uploads/**', async (route, request) => {
      const method = request.method()

      if (method === 'OPTIONS') {
        await route.fulfill({
          status: 204,
          headers: {
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'OPTIONS, POST, PATCH, HEAD',
            'access-control-allow-headers': 'Tus-Resumable, Upload-Length, Upload-Offset, Upload-Metadata, Content-Type',
            'tus-resumable': '1.0.0',
          },
        })
        return
      }

      if (method === 'POST') {
        await route.fulfill({
          status: 201,
          headers: {
            location: 'http://localhost/uploads/mock-upload-id',
            'tus-resumable': '1.0.0',
            'upload-offset': '0',
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Location, Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      if (method === 'HEAD') {
        await route.fulfill({
          status: 200,
          headers: {
            'tus-resumable': '1.0.0',
            'upload-offset': '0',
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      if (method === 'PATCH') {
        const headers = request.headers()
        const previousOffset = Number(headers['upload-offset'] ?? '0')
        const chunkSize = Number(headers['content-length'] ?? '0')
        const nextOffset = previousOffset + chunkSize

        await route.fulfill({
          status: 204,
          headers: {
            'tus-resumable': '1.0.0',
            'upload-offset': String(nextOffset),
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      await route.continue()
    })
  })

  test('upload via bouton alternatif + drag and drop lot, puis badge import', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Identifiant').fill('fatima')
    await page.getByLabel('Mot de passe').fill('test-password')
    await page.getByRole('button', { name: 'Se connecter' }).click()

    await expect(page.getByRole('heading', { name: 'Espace documents' })).toBeVisible()

    await page.getByRole('link', { name: 'Import' }).click()
    await expect(page.getByRole('heading', { name: 'Import' })).toBeVisible()

    const importButton = page.getByRole('button', { name: 'Importer' }).first()
    await importButton.focus()
    const chooserPromise = page.waitForEvent('filechooser')
    await importButton.press('Enter')
    await chooserPromise

    const dragFiles: MockUploadFile[] = Array.from({ length: 50 }).map((_, index) => ({
      name: `batch-${index + 1}.pdf`,
      type: 'application/pdf',
      content: `mock-content-${index + 1}`,
    }))

    const dataTransfer = await page.evaluateHandle((files) => {
      const transfer = new DataTransfer()
      files.forEach((file) => {
        transfer.items.add(new File([file.content], file.name, { type: file.type }))
      })
      return transfer
    }, dragFiles)

    await page.dispatchEvent('[data-testid="import-drop-area"]', 'dragenter', { dataTransfer })
    await expect(page.getByTestId('dropzone-overlay')).toBeVisible()
    await page.dispatchEvent('[data-testid="import-drop-area"]', 'drop', { dataTransfer })

    await expect(page.getByText('Import en cours: 50 fichier(s)')).toBeVisible()
    await expect(page.getByText('batch-1.pdf')).toBeVisible()

    const importBadge = page.getByTestId('import-badge')
    await expect(importBadge).toBeVisible()
    await expect(importBadge).toContainText('50')
  })

  test('story 2.2: interruption reseau simulee puis reprise sans perte avec navigation non bloquante', async ({ page }) => {
    let patchAttempts = 0

    await page.route('http://localhost/uploads/**', async (route, request) => {
      const method = request.method()

      if (method === 'OPTIONS') {
        await route.fulfill({
          status: 204,
          headers: {
            'access-control-allow-origin': '*',
            'access-control-allow-methods': 'OPTIONS, POST, PATCH, HEAD',
            'access-control-allow-headers': 'Tus-Resumable, Upload-Length, Upload-Offset, Upload-Metadata, Content-Type',
            'tus-resumable': '1.0.0',
          },
        })
        return
      }

      if (method === 'POST') {
        await route.fulfill({
          status: 201,
          headers: {
            location: 'http://localhost/uploads/mock-resume-id',
            'tus-resumable': '1.0.0',
            'upload-offset': '0',
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Location, Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      if (method === 'HEAD') {
        await route.fulfill({
          status: 200,
          headers: {
            'tus-resumable': '1.0.0',
            'upload-offset': '0',
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      if (method === 'PATCH') {
        patchAttempts += 1

        if (patchAttempts === 1) {
          await route.fulfill({ status: 500, body: 'temporary network failure' })
          return
        }

        const headers = request.headers()
        const previousOffset = Number(headers['upload-offset'] ?? '0')
        const chunkSize = Number(headers['content-length'] ?? '0')
        const nextOffset = previousOffset + chunkSize

        await new Promise((resolve) => setTimeout(resolve, 150))
        await route.fulfill({
          status: 204,
          headers: {
            'tus-resumable': '1.0.0',
            'upload-offset': String(nextOffset),
            'access-control-allow-origin': '*',
            'access-control-expose-headers': 'Upload-Offset, Tus-Resumable',
          },
        })
        return
      }

      await route.continue()
    })

    await page.goto('/login')
    await page.getByLabel('Identifiant').fill('fatima')
    await page.getByLabel('Mot de passe').fill('test-password')
    await page.getByRole('button', { name: 'Se connecter' }).click()

    await page.getByRole('link', { name: 'Import' }).click()
    await expect(page.getByRole('heading', { name: 'Import' })).toBeVisible()

    const dataTransfer = await page.evaluateHandle(() => {
      const transfer = new DataTransfer()
      transfer.items.add(new File(['resume-content'], 'resume.pdf', { type: 'application/pdf' }))
      return transfer
    })

    await page.dispatchEvent('[data-testid="import-drop-area"]', 'drop', { dataTransfer })

    await expect(page.getByText('Reconnexion en cours...')).toBeVisible()

    await page.getByRole('link', { name: 'Documents' }).click()
    await expect(page.getByRole('heading', { name: 'Espace documents' })).toBeVisible()

    await page.getByRole('link', { name: 'Import' }).click()
    await expect(page.getByRole('heading', { name: 'Import' })).toBeVisible()
    await expect(page.getByText('resume.pdf')).toBeVisible()
    await expect(page.locator('.ant-message')).toContainText('Upload repris - aucun fichier perdu')
  })
})
