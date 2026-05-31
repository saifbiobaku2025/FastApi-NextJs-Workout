const DEFAULT_PASSWORD = "testpass123";

function uniqueUsername() {
  return `e2e_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

async function registerUser(page, username = uniqueUsername(), password = DEFAULT_PASSWORD) {
  await page.goto("/login");
  await page.locator("#registerUsername").fill(username);
  await page.locator("#registerPassword").fill(password);
  await page.getByRole("button", { name: "Register" }).click();
  await page.getByRole("heading", { name: "Welcome!" }).waitFor();
  return { username, password };
}

async function loginUser(page, username, password = DEFAULT_PASSWORD) {
  await page.goto("/login");
  await page.locator("#username").fill(username);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: "Login" }).click();
  await page.getByRole("heading", { name: "Welcome!" }).waitFor();
}

module.exports = {
  DEFAULT_PASSWORD,
  uniqueUsername,
  registerUser,
  loginUser,
};
