/**
 * TypeScript client for the matrx-orm API server.
 *
 * Copy this file into your Electron / Tauri / web frontend project.
 * No external dependencies — uses the Fetch API and native WebSocket.
 *
 * Usage:
 *   const client = new MatrxClient("http://127.0.0.1:8745", "your-secret");
 *   await client.authenticate();
 *
 *   const users = await client.call("users.load_items", { status: "active" });
 *   const user = await client.call("users.create_item", {
 *     username: "alice",
 *     email: "alice@example.com",
 *   });
 */

// ── Types ─────────────────────────────────────────────────────────────────

interface RPCRequest {
  method: string;
  params: Record<string, unknown>;
  id: number;
}

interface RPCError {
  code: number;
  message: string;
  data?: Record<string, unknown>;
}

interface RPCResponse<T = unknown> {
  result: T | null;
  error: RPCError | null;
  id: number | null;
}

interface AuthResponse {
  token: string;
  expires_in: number;
}

interface HealthResponse {
  status: string;
  managers: string[];
}

// ── Error codes ───────────────────────────────────────────────────────────

export enum ErrorCode {
  PARSE_ERROR = -32700,
  INVALID_REQUEST = -32600,
  METHOD_NOT_FOUND = -32601,
  INVALID_PARAMS = -32602,
  INTERNAL_ERROR = -32603,
  NOT_FOUND = 1001,
  VALIDATION_ERROR = 1002,
  INTEGRITY_ERROR = 1003,
  AUTH_REQUIRED = 1004,
  AUTH_INVALID = 1005,
  PERMISSION_DENIED = 1006,
  RATE_LIMITED = 1007,
  CONNECTION_ERROR = 1008,
  QUERY_ERROR = 1009,
}

// ── Client error ──────────────────────────────────────────────────────────

export class MatrxRPCError extends Error {
  code: number;
  data?: Record<string, unknown>;

  constructor(error: RPCError) {
    super(error.message);
    this.name = "MatrxRPCError";
    this.code = error.code;
    this.data = error.data;
  }
}

// ── HTTP Client ───────────────────────────────────────────────────────────

export class MatrxClient {
  private baseUrl: string;
  private secret: string;
  private token: string | null = null;
  private tokenExpiry: number = 0;
  private requestId = 0;

  constructor(baseUrl: string, secret: string) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.secret = secret;
  }

  /**
   * Exchange the shared secret for a bearer token.
   * Call this before making any RPC calls.
   */
  async authenticate(clientId = "desktop"): Promise<void> {
    const resp = await fetch(`${this.baseUrl}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        secret: this.secret,
        client_id: clientId,
      }),
    });

    if (!resp.ok) {
      throw new Error(`Authentication failed: ${resp.status}`);
    }

    const data: AuthResponse = await resp.json();
    this.token = data.token;
    this.tokenExpiry = Date.now() + data.expires_in * 1000;
  }

  /**
   * Check if the current token is still valid.
   */
  get isAuthenticated(): boolean {
    return this.token !== null && Date.now() < this.tokenExpiry;
  }

  /**
   * Re-authenticate if the token has expired.
   */
  private async ensureAuth(): Promise<void> {
    if (!this.isAuthenticated) {
      await this.authenticate();
    }
  }

  /**
   * Make a single RPC call.
   *
   * @param method - The RPC method (e.g. "users.load_item")
   * @param params - Keyword arguments as an object
   * @returns The result from the server
   * @throws MatrxRPCError on RPC errors
   */
  async call<T = unknown>(
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<T> {
    await this.ensureAuth();
    this.requestId++;

    const payload: RPCRequest = {
      method,
      params,
      id: this.requestId,
    };

    const resp = await fetch(`${this.baseUrl}/rpc`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(payload),
    });

    const data: RPCResponse<T> = JSON.parse(await resp.text());

    if (data.error) {
      throw new MatrxRPCError(data.error);
    }

    return data.result as T;
  }

  /**
   * Make multiple RPC calls in a single HTTP request.
   *
   * @param calls - Array of [method, params] tuples
   * @returns Array of results in the same order
   */
  async callBatch(
    calls: Array<[string, Record<string, unknown>]>
  ): Promise<unknown[]> {
    await this.ensureAuth();

    const batch: RPCRequest[] = calls.map(([method, params]) => {
      this.requestId++;
      return { method, params, id: this.requestId };
    });

    const resp = await fetch(`${this.baseUrl}/rpc`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.token}`,
      },
      body: JSON.stringify(batch),
    });

    const responses: RPCResponse[] = JSON.parse(await resp.text());
    return responses.map((r) => {
      if (r.error) throw new MatrxRPCError(r.error);
      return r.result;
    });
  }

  /**
   * Health check (no auth required).
   */
  async health(): Promise<HealthResponse> {
    const resp = await fetch(`${this.baseUrl}/health`);
    return resp.json();
  }
}

// ── WebSocket Client ──────────────────────────────────────────────────────

type WSMessageHandler = (response: RPCResponse) => void;

export class MatrxWSClient {
  private baseUrl: string;
  private token: string;
  private ws: WebSocket | null = null;
  private requestId = 0;
  private pending = new Map<number, {
    resolve: (value: unknown) => void;
    reject: (error: Error) => void;
  }>();
  private onMessage?: WSMessageHandler;

  constructor(baseUrl: string, token: string) {
    // Convert http:// to ws://
    this.baseUrl = baseUrl.replace(/^http/, "ws");
    this.token = token;
  }

  /**
   * Connect and authenticate via WebSocket.
   */
  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(`${this.baseUrl}/ws`);

      this.ws.onopen = () => {
        // Send auth token as first message
        this.ws!.send(JSON.stringify({ token: this.token }));
      };

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Auth response
        if (data.type === "auth_ok") {
          resolve();
          return;
        }
        if (data.type === "auth_error") {
          reject(new Error(data.error));
          return;
        }

        // RPC response
        const response = data as RPCResponse;
        const id = response.id as number;
        const handler = this.pending.get(id);
        if (handler) {
          this.pending.delete(id);
          if (response.error) {
            handler.reject(new MatrxRPCError(response.error));
          } else {
            handler.resolve(response.result);
          }
        }

        // General message handler
        this.onMessage?.(response);
      };

      this.ws.onerror = () => reject(new Error("WebSocket connection failed"));
      this.ws.onclose = () => {
        // Reject all pending requests
        for (const [, handler] of this.pending) {
          handler.reject(new Error("WebSocket closed"));
        }
        this.pending.clear();
      };
    });
  }

  /**
   * Make an RPC call over the WebSocket.
   */
  async call<T = unknown>(
    method: string,
    params: Record<string, unknown> = {}
  ): Promise<T> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not connected");
    }

    this.requestId++;
    const id = this.requestId;

    const payload: RPCRequest = { method, params, id };

    return new Promise((resolve, reject) => {
      this.pending.set(id, {
        resolve: resolve as (value: unknown) => void,
        reject,
      });
      this.ws!.send(JSON.stringify(payload));
    });
  }

  /**
   * Close the WebSocket connection.
   */
  close(): void {
    this.ws?.close();
    this.ws = null;
  }
}

// ── Example usage ─────────────────────────────────────────────────────────

/*
// In your Electron renderer or Tauri frontend:

const client = new MatrxClient("http://127.0.0.1:8745", "your-secret");
await client.authenticate();

// CRUD operations
const user = await client.call<{ id: string; username: string }>(
  "users.create_item",
  { username: "alice", email: "alice@example.com" }
);

const users = await client.call<Array<{ id: string; username: string }>>(
  "users.load_items",
  { is_active: true }
);

// Batch operations
const [userCount, noteCount] = await client.callBatch([
  ["users.count", {}],
  ["notes.count", {}],
]);

// WebSocket for real-time updates
const wsClient = new MatrxWSClient("http://127.0.0.1:8745", client.token);
await wsClient.connect();
const result = await wsClient.call("users.load_items");
wsClient.close();
*/
