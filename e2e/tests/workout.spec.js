const { test, expect } = require("@playwright/test");
const { registerUser } = require("../fixtures/auth");

test.describe("Workouts and routines", () => {
  test.beforeEach(async ({ page }) => {
    await registerUser(page);
  });

  test("create workout and see it in routine selector", async ({ page }) => {
    const workoutName = `Workout ${Date.now()}`;

    await page.locator("#workoutName").fill(workoutName);
    await page.locator("#workoutDescription").fill("E2E test workout");
    await page
      .locator("#collapseOne form")
      .getByRole("button", { name: "Create Workout" })
      .click();

    await page.locator('[data-bs-target="#collapseTwo"]').click();
    await expect(page.locator("#workoutSelect")).toContainText(workoutName);
  });

  test("create routine with a workout", async ({ page }) => {
    const workoutName = `Workout ${Date.now()}`;
    const routineName = `Routine ${Date.now()}`;

    await page.locator("#workoutName").fill(workoutName);
    await page.locator("#workoutDescription").fill("Morning cardio");
    await page
      .locator("#collapseOne form")
      .getByRole("button", { name: "Create Workout" })
      .click();

    await page.locator('[data-bs-target="#collapseTwo"]').click();
    await page.locator("#routineName").fill(routineName);
    await page.locator("#routineDescription").fill("Weekly plan");
    await page.locator("#workoutSelect").selectOption({ label: workoutName });
    await page
      .locator("#collapseTwo form")
      .getByRole("button", { name: "Create Routine" })
      .click();

    await expect(page.getByText(routineName)).toBeVisible();
    await expect(page.getByText("Morning cardio")).toBeVisible();
    await expect(page.getByText(`${workoutName}: Morning cardio`)).toBeVisible();
  });
});
