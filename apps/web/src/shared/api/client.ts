import { z } from 'zod';
import { API_BASE } from '@/shared/config';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function request<T>(path: string, schema: z.ZodType<T>, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      // тело не JSON — оставляем statusText
    }
    throw new ApiError(res.status, detail);
  }
  const data = await res.json();
  return schema.parse(data);
}

export const api = {
  get: <T>(path: string, schema: z.ZodType<T>) => request(path, schema),
  post: <T>(path: string, schema: z.ZodType<T>, body?: unknown) =>
    request(path, schema, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, schema: z.ZodType<T>, body?: unknown) =>
    request(path, schema, { method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
};
