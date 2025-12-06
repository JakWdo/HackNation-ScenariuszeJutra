import { test, expect } from '@playwright/test';

test('Chain of Thought cards expand on click', async ({ page }) => {
  // 1. Go to home page
  await page.goto('/');

  // 2. Start analysis
  // The button text is "Uruchom analizę"
  const startButton = page.getByRole('button', { name: /Uruchom analizę/i });
  await startButton.click();

  // 3. Wait for the first thought step to appear
  // Title is "Analiza zapytania"
  const firstStepTitle = page.getByText('Analiza zapytania');
  await expect(firstStepTitle).toBeVisible({ timeout: 10000 });

  // 4. Locate the content paragraph within the step
  // The content is "Rozpoznaję zapytanie:..."
  const contentText = 'Rozpoznaję zapytanie:';
  const contentParagraph = page.getByText(contentText).first();

  // 5. Verify initial state (should be clamped)
  // We check for the class 'line-clamp-2'
  await expect(contentParagraph).toHaveClass(/line-clamp-2/);

  // 6. Click the step header/container to expand
  // We can click the title or the paragraph itself since the whole container is clickable
  await firstStepTitle.click();

  // 7. Verify expanded state (should NOT be clamped)
  await expect(contentParagraph).not.toHaveClass(/line-clamp-2/);
});
