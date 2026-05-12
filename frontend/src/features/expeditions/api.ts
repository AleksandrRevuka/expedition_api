/**
 * Expeditions API functions
 */

import { apiClient } from '@/shared/api/client';
import { Expedition, ExpeditionStatus } from '@/shared/types';

/**
 * Fetch all expeditions
 */
export async function fetchExpeditions(): Promise<Expedition[]> {
  const response = await apiClient.get<Expedition[]>('/expeditions');
  return response.data;
}

/**
 * Fetch all expeditions for a user
 */
export async function fetchMyExpeditions(): Promise<Expedition[]> {
  const response = await apiClient.get<Expedition[]>('/chief/expeditions');
  return response.data;
}


/**
 * Fetch a single expedition by ID
 */
export async function fetchExpedition(id: string): Promise<Expedition> {
  const response = await apiClient.get<Expedition>(`/expeditions/${id}`);
  return response.data;
}

/**
 * Create a new expedition
 */
export interface CreateExpeditionPayload {
  title: string;
  description: string;
  start_at: string;
  capacity: number;
}

export async function createExpedition(payload: CreateExpeditionPayload): Promise<Expedition> {
  const response = await apiClient.post<Expedition>('/expeditions', payload);
  return response.data;
}

/**
 * Update an expedition
 */
export interface UpdateExpeditionPayload {
  title?: string;
  description?: string;
}

export async function updateExpedition(id: string, payload: UpdateExpeditionPayload): Promise<Expedition> {
  const response = await apiClient.patch<Expedition>(`/chief/expeditions/${id}`, payload);
  return response.data;
}

/**
 * Delete an expedition
 */
export async function deleteExpedition(id: string): Promise<void> {
  await apiClient.delete(`/chief/expeditions/${id}`);
}

/**
 * Change expedition status
 */
export interface ChangeExpeditionStatusPayload {
  status: ExpeditionStatus;
}

export async function changeExpeditionStatus(
  id: string,
  status: ExpeditionStatus
): Promise<Expedition> {
  const response = await apiClient.patch<Expedition>(`/chief/expeditions/${id}/status`, {
    status,
  });
  return response.data;
}

/**
 * Invite a member to an expedition
 */
export interface InviteMemberPayload {
  user_id: string;
}

export async function inviteMember(expeditionId: string, userId: string): Promise<Expedition> {
  const response = await apiClient.post<Expedition>(
    `/expeditions/${expeditionId}/members/invite`,
    { user_id: userId }
  );
  return response.data;
}

/**
 * Confirm membership in an expedition
 */
export async function confirmMembership(expeditionId: string): Promise<Expedition> {
  const response = await apiClient.post<Expedition>(
    `/expeditions/${expeditionId}/members/confirm`,
    {}
  );
  return response.data;
}

/**
 * Remove a member from an expedition
 */
export async function removeMember(expeditionId: string, userId: string): Promise<Expedition> {
  const response = await apiClient.delete<Expedition>(
    `/chief/expeditions/${expeditionId}/members/${userId}`
  );
  return response.data;
}
