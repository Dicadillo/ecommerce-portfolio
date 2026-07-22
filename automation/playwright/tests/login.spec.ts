import { expect, test } from '@playwright/test';

test('muestra la página de inicio de sesión', async ({ page }) => {
  await page.goto('http://localhost:5173/login');

  await expect(
    page.getByRole('heading', { name: /iniciar sesión/i }),
  ).toBeVisible();
});
