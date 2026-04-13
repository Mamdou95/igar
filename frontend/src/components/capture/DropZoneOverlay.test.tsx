import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { DropZoneOverlay } from './DropZoneOverlay'

describe('DropZoneOverlay', () => {
  it('renders overlay when visible', () => {
    render(<DropZoneOverlay visible activeDrag={false} onBrowse={vi.fn()} />)
    expect(screen.getByTestId('dropzone-overlay')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Importer des documents' })).toBeInTheDocument()
  })

  it('does not render when hidden', () => {
    render(<DropZoneOverlay visible={false} activeDrag={false} onBrowse={vi.fn()} />)
    expect(screen.queryByTestId('dropzone-overlay')).not.toBeInTheDocument()
  })
})
