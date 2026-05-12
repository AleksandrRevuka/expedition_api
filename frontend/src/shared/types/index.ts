/**
 * Shared TypeScript types for the Expedition API frontend
 */

export enum Role {
  Chief = 'chief',
  Member = 'member',
}

export enum ExpeditionStatus {
  Draft = 'draft',
  Ready = 'ready',
  Active = 'active',
  Finished = 'finished',
}

export enum MemberState {
  Invited = 'invited',
  Confirmed = 'confirmed',
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: Role;
  created_at: string;
  updated_at: string;
}

export interface Member {
  user_id: string;
  expedition_id: string;
  state: MemberState;
  created_at: string;
  updated_at: string;
}

export interface Expedition {
  id: string;
  title: string;
  description: string;
  status: ExpeditionStatus;
  chief_id: string;
  capacity: number;
  start_at: string;
  created_at: string;
  updated_at: string;
  members?: Member[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface WsMessage<T = unknown> {
  type: string;
  data: T;
  timestamp: string;
}
