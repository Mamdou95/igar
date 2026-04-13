import { apiClient } from './client'

export interface User {
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

export interface UserCreate {
  username: string
  email: string
  password: string
  first_name?: string
  last_name?: string
  groups: number[]
  is_active?: boolean
  is_readonly?: boolean
}

export interface UserUpdate {
  email?: string
  first_name?: string
  last_name?: string
  is_active?: boolean
  is_readonly?: boolean
  groups?: number[]
}

export interface Group {
  id: number
  name: string
  permissions: number[]
  allowed_document_groups?: number[]
}

export interface Permission {
  id: number
  name: string
  codename: string
  content_type?: number
  app?: string
}

export interface DocumentAccessGroup {
  id: number
  name: string
  description: string
  parent?: number | null
  created_at: string
}

export interface AuditLogEntry {
  id: number
  action: string
  resource_type: string
  resource_id: number
  user: {
    id: number
    username: string
  }
  old_values: Record<string, unknown>
  new_values: Record<string, unknown>
  ip_address: string
  created_at: string
  reason?: string
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

interface ListUsersOptions {
  page?: number
  limit?: number
  search?: string
  groupId?: number
  isActive?: boolean
  ordering?: string
}

export async function listUsers(options: ListUsersOptions = {}) {
  const { page = 1, limit = 25, search, groupId, isActive, ordering } = options
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  })
  if (search) params.append('search', search)
  if (typeof groupId === 'number') params.append('group', String(groupId))
  if (typeof isActive === 'boolean') params.append('is_active', String(isActive))
  if (ordering) params.append('ordering', ordering)

  const response = await apiClient.get<PaginatedResponse<User>>(`/admin/users/?${params.toString()}`)
  return response.data
}

export async function getUser(id: number) {
  const response = await apiClient.get<User>(`/admin/users/${id}/`)
  return response.data
}

export async function createUser(data: UserCreate) {
  const response = await apiClient.post<User>('/admin/users/', data)
  return response.data
}

export async function updateUser(id: number, data: UserUpdate) {
  const response = await apiClient.patch<User>(`/admin/users/${id}/`, data)
  return response.data
}

export async function deactivateUser(id: number) {
  return updateUser(id, { is_active: false })
}

export async function activateUser(id: number) {
  return updateUser(id, { is_active: true })
}

export async function resetUserPassword(id: number) {
  const response = await apiClient.post(`/admin/users/${id}/reset_password/`)
  return response.data
}

export async function resetUserTwoFactor(id: number) {
  const response = await apiClient.post(`/admin/users/${id}/reset_2fa/`)
  return response.data
}

export async function listRoles(page = 1, limit = 25) {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  })
  const response = await apiClient.get<PaginatedResponse<Group>>(`/admin/roles/?${params.toString()}`)
  return response.data
}

export async function getRole(id: number) {
  const response = await apiClient.get<Group>(`/admin/roles/${id}/`)
  return response.data
}

export async function createRole(data: {
  name: string
  permissions: number[]
  allowed_document_groups?: number[]
}) {
  const response = await apiClient.post<Group>('/admin/roles/', data)
  return response.data
}

export async function updateRole(
  id: number,
  data: { name?: string; permissions?: number[]; allowed_document_groups?: number[] },
) {
  const response = await apiClient.patch<Group>(`/admin/roles/${id}/`, data)
  return response.data
}

export async function deleteRole(id: number) {
  const response = await apiClient.delete<{ status: string }>(`/admin/roles/${id}/`)
  return response.data
}

export async function listPermissions() {
  const response = await apiClient.get<{ results: Permission[] }>('/admin/permissions/')
  return response.data.results
}

export async function listDocumentAccessGroups(page = 1, limit = 100) {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  })
  const response = await apiClient.get<PaginatedResponse<DocumentAccessGroup>>(
    `/admin/document-groups/?${params.toString()}`,
  )
  return response.data
}

export async function getDocumentAccessGroup(id: number) {
  const response = await apiClient.get<DocumentAccessGroup>(`/admin/document-groups/${id}/`)
  return response.data
}

export async function listAuditLogs(
  page = 1,
  limit = 25,
  action?: string,
  resourceType?: string,
  userId?: number,
) {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  })
  if (action) params.append('action', action)
  if (resourceType) params.append('resource_type', resourceType)
  if (userId) params.append('user', String(userId))

  const response = await apiClient.get<PaginatedResponse<AuditLogEntry>>(
    `/admin/audit-logs/?${params.toString()}`,
  )
  return response.data
}

export async function getAuditLog(id: number) {
  const response = await apiClient.get<AuditLogEntry>(`/admin/audit-logs/${id}/`)
  return response.data
}
