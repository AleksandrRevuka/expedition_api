/**
 * WebSocket Manager for expedition real-time updates
 * Handles connection, reconnection with exponential backoff, and message routing
 */

import { WsMessage } from '@/shared/types';

export type WsMessageHandler = (message: WsMessage) => void;

interface WsManagerConfig {
  expeditionId: string;
  token: string;
  onAuthError?: () => void;
}

/**
 * ExpeditionWsManager manages a WebSocket connection to expedition updates
 * - Connects to ws://<origin>/api/ws/expeditions/{id}?token=<jwt>
 * - Reconnects with exponential backoff (1s initial, doubles each attempt, max 30s)
 * - On 1008 (unauthorized): calls onAuthError and stops reconnect attempts
 * - Provides subscribe/unsubscribe for message handlers
 */
export class ExpeditionWsManager {
  private ws: WebSocket | null = null;
  private config: WsManagerConfig;
  private handlers: Set<WsMessageHandler> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private stopped = false;

  constructor(config: WsManagerConfig) {
    this.config = config;
  }

  /**
   * Connect to the WebSocket server
   */
  async connect(): Promise<void> {
    if (this.stopped) {
      return;
    }

    try {
      const wsUrl = this.buildWsUrl();
      this.ws = new WebSocket(wsUrl);

      this.ws.addEventListener('open', this.handleOpen);
      this.ws.addEventListener('message', this.handleMessage);
      this.ws.addEventListener('close', this.handleClose);
      this.ws.addEventListener('error', this.handleError);
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server and prevent reconnect attempts
   */
  disconnect(): void {
    this.stopped = true;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Subscribe to WebSocket messages
   */
  subscribe(handler: WsMessageHandler): () => void {
    this.handlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.handlers.delete(handler);
    };
  }

  /**
   * Build WebSocket URL with authentication token
   */
  private buildWsUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const token = encodeURIComponent(this.config.token);
    return `${protocol}//${host}/api/ws/expeditions/${this.config.expeditionId}?token=${token}`;
  }

  /**
   * Handle WebSocket open event
   */
  private handleOpen = (): void => {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
  };

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage = (event: MessageEvent): void => {
    try {
      const message = JSON.parse(event.data) as WsMessage;
      this.handlers.forEach((handler) => {
        try {
          handler(message);
        } catch (error) {
          console.error('Error in message handler:', error);
        }
      });
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  };

  /**
   * Handle WebSocket close event
   */
  private handleClose = (event: CloseEvent): void => {
    console.log(`WebSocket closed with code ${event.code}`);

    // 1008 = Policy Violation (unauthorized)
    if (event.code === 1008) {
      console.log('Authorization failed, not attempting to reconnect');
      this.config.onAuthError?.();
      return;
    }

    // Reconnect on any other close code
    this.scheduleReconnect();
  };

  /**
   * Handle WebSocket errors
   */
  private handleError = (event: Event): void => {
    console.error('WebSocket error:', event);
  };

  /**
   * Schedule reconnection with exponential backoff
   */
  private scheduleReconnect(): void {
    if (this.stopped) {
      return;
    }

    const delayMs = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts += 1;

    console.log(`Scheduling WebSocket reconnect in ${delayMs}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delayMs);
  }
}
