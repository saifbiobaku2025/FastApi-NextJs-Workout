const { test, expect } = require("@playwright/test");
const { registerUser, loginUser, uniqueUsername, DEFAULT_PASSWORD } = require("../fixtures/auth");

test.describe("Authentication", () => {
  test("register and reach home page", async ({ page }) => {
    await registerUser(page);
    await expect(page.getByRole("heading", { name: "Welcome!" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Logout" })).toBeVisible();
  });

  test("login with existing user", async ({ page }) => {
    const username = uniqueUsername();
    await registerUser(page, username);
    await page.getByRole("button", { name: "Logout" }).click();
    await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();

    await loginUser(page, username, DEFAULT_PASSWORD);
    await expect(page.getByRole("heading", { name: "Welcome!" })).toBeVisible();
  });

  test("logout redirects to login", async ({ page }) => {
    await registerUser(page);
    await page.getByRole("button", { name: "Logout" }).click();
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole("heading", { name: "Login" })).toBeVisible();
  });
});
