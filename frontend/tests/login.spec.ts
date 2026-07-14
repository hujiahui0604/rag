import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  const testUser = {
    username: `testuser_${Date.now()}`,
    email: `test_${Date.now()}@example.com`,
    password: 'testpass123',
  };

  test('should register a new user', async ({ page }) => {
    await page.goto('/register');

    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="email"]', testUser.email);
    await page.fill('input[name="password"]', testUser.password);
    await page.fill('input[name="confirmPassword"]', testUser.password);

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/login', { timeout: 10000 });
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);

    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/documents', { timeout: 10000 });

    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="username"]', 'nonexistent');
    await page.fill('input[name="password"]', 'wrongpassword');

    await page.click('button[type="submit"]');

    await expect(page.locator('.text-red-500')).toBeVisible({ timeout: 5000 });
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    await page.goto('/documents');

    await expect(page).toHaveURL('/login');
  });
});