import '@testing-library/jest-dom/vitest';

import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

import { clearAuthSession } from '../features/auth/authStorage';
import { clearPaymentRegistry } from '../features/payments/paymentRegistry';

afterEach(() => {
  cleanup();
  clearAuthSession();
  clearPaymentRegistry();
});
