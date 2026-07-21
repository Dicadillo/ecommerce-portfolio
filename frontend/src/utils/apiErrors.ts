import axios from 'axios';

interface ApiErrorBody {
  error?: {
    codigo?: string;
    mensaje?: string;
    detalles?: Record<string, unknown>;
  };
}

export interface ParsedApiError {
  fieldErrors: Record<string, string>;
  message: string;
}

function firstMessage(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }

  if (Array.isArray(value)) {
    return value.map(firstMessage).find(Boolean);
  }

  return undefined;
}

export function parseApiError(error: unknown, fallbackMessage: string): ParsedApiError {
  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return { fieldErrors: {}, message: fallbackMessage };
  }

  const apiError = error.response?.data?.error;
  const fieldErrors = Object.fromEntries(
    Object.entries(apiError?.detalles ?? {}).flatMap(([field, value]) => {
      const message = firstMessage(value);
      return message ? [[field, message]] : [];
    }),
  );

  return {
    fieldErrors,
    message: apiError?.mensaje ?? fallbackMessage,
  };
}
