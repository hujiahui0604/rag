import { test, expect } from '@playwright/test';

test.describe('Chat Functionality', () => {
  const testUser = {
    username: `chattest_${Date.now()}`,
    email: `chat_${Date.now()}@example.com`,
    password: 'testpass123',
  };

  test.beforeAll(async ({ page }) => {
    await page.goto('/register');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="email"]', testUser.email);
    await page.fill('input[name="password"]', testUser.password);
    await page.fill('input[name="confirmPassword"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/login');
  });

  test('should display empty chat', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');

    await expect(page.locator('text=开始一个新对话吧')).toBeVisible();
  });

  test('should create new chat session', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');

    await page.click('button:has-text("+")');

    await expect(page.locator('h2:has-text("新对话")')).toBeVisible();
  });

  test('should send a message', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');

    const messageInput = page.locator('input[placeholder="输入问题..."]');
    await messageInput.fill('Hello, this is a test message');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Hello, this is a test message')).toBeVisible({ timeout: 10000 });
  });

  test('should switch between chat sessions', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/chat');

    await page.click('button:has-text("+")');
    await page.waitForTimeout(500);

    await page.click('button:has-text("+")');
    await page.waitForTimeout(500);

    const sessions = page.locator('.space-y-2 button');
    const count = await sessions.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });
});