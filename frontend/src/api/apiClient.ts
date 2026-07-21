import axios from 'axios';

const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
  throw new Error('La variable VITE_API_URL no está configurada.');
}

export const apiClient = axios.create({
  baseURL: apiUrl,
  headers: {
    Accept: 'application/json',
  },
  timeout: 10_000,
});
