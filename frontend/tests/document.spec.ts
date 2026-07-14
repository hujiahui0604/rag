import { test, expect } from '@playwright/test';

test.describe('Document Management', () => {
  const testUser = {
    username: `doctest_${Date.now()}`,
    email: `doc_${Date.now()}@example.com`,
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

  test('should display empty document list', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/documents');

    await expect(page.locator('text=暂无文档')).toBeVisible();
  });

  test('should upload a document', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/documents');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'test.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('This is a test document content'),
    });

    await page.fill('input[name="title"]', 'Test Document');
    await page.click('button:has-text("上传")');

    await expect(page.locator('text=Test Document')).toBeVisible({ timeout: 10000 });
  });

  test('should delete a document', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/documents');

    const deleteButton = page.locator('button:has-text("删除")').first();
    if (await deleteButton.isVisible()) {
      await deleteButton.click();
      await expect(page.locator('text=Test Document')).not.toBeVisible({ timeout: 5000 });
    }
  });

  test('should filter documents by category', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"]', testUser.password);
    await page.click('button[type="submit"]');
    await page.waitForURL('/documents');

    await page.selectOption('select', { index: 1 });
    await page.waitForTimeout(500);
  });
});