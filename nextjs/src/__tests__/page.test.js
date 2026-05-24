import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axios from "axios";
import AuthContext from "../app/context/AuthContext";
import Home from "../app/page";

jest.mock("axios");

const mockLogout = jest.fn();

const sampleWorkouts = [
  { id: 1, name: "Push Day", description: "Chest and triceps" },
  { id: 2, name: "Pull Day", description: "Back and biceps" },
];

const sampleRoutines = [
  {
    id: 10,
    name: "Upper Body",
    description: "Two-day split",
    workouts: [sampleWorkouts[0]],
  },
];

function renderHome(authOverrides = {}) {
  const authValue = {
    user: { authenticated: true },
    logout: mockLogout,
    isAuthLoading: false,
    ...authOverrides,
  };

  return render(
    <AuthContext.Provider value={authValue}>
      <Home />
    </AuthContext.Provider>,
  );
}

describe("Home page", () => {
  beforeEach(() => {
    mockLogout.mockReset();
    axios.get.mockReset();
    axios.post.mockReset();
    jest.spyOn(console, "error").mockImplementation(() => {});

    axios.get.mockImplementation((url) => {
      if (url.includes("/workouts/workouts")) {
        return Promise.resolve({ data: sampleWorkouts });
      }
      if (url.includes("/routines")) {
        return Promise.resolve({ data: sampleRoutines });
      }
      return Promise.reject(new Error(`Unexpected GET ${url}`));
    });
  });

  afterEach(() => {
    console.error.mockRestore();
  });

  it("loads and displays workouts and routines for authenticated users", async () => {
    renderHome();

    expect(await screen.findByText("Welcome!")).toBeInTheDocument();
    expect(await screen.findByText("Upper Body")).toBeInTheDocument();
    expect(screen.getByText("Push Day: Chest and triceps")).toBeInTheDocument();
    expect(axios.get).toHaveBeenCalledWith(
      "http://localhost:8000/workouts/workouts",
    );
    expect(axios.get).toHaveBeenCalledWith("http://localhost:8000/routines");
  });

  it("does not fetch data while auth is loading", () => {
    renderHome({ user: null, isAuthLoading: true });

    expect(axios.get).not.toHaveBeenCalled();
  });

  it("does not fetch data when user is not authenticated", () => {
    renderHome({ user: null, isAuthLoading: false });

    expect(axios.get).not.toHaveBeenCalled();
  });

  it("creates a workout and adds it to the list", async () => {
    axios.post.mockResolvedValue({
      data: { id: 3, name: "Leg Day", description: "Squats and lunges" },
    });
    const user = userEvent.setup();
    renderHome();

    await screen.findByText("Welcome!");

    const workoutForm = within(screen.getByLabelText("Workout Name").closest("form"));
    await user.type(workoutForm.getByLabelText("Workout Name"), "Leg Day");
    await user.type(
      workoutForm.getByLabelText("Workout Description"),
      "Squats and lunges",
    );
    await user.click(workoutForm.getByRole("button", { name: "Create Workout" }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        "http://localhost:8000/workouts",
        {
          name: "Leg Day",
          description: "Squats and lunges",
        },
      );
    });
    expect(await screen.findByText("Leg Day")).toBeInTheDocument();
  });

  it("creates a routine and adds it to the list", async () => {
    axios.post.mockResolvedValue({
      data: {
        id: 11,
        name: "Full Body",
        description: "All major lifts",
        workouts: [],
      },
    });
    const user = userEvent.setup();
    renderHome();

    await screen.findByText("Welcome!");

    const routineForm = within(
      screen.getByLabelText("Routine Name").closest("form"),
    );

    await user.type(routineForm.getByLabelText("Routine Name"), "Full Body");
    await user.type(
      routineForm.getByLabelText("Routine Description"),
      "All major lifts",
    );
    await user.selectOptions(
      routineForm.getByLabelText("Select Workouts"),
      ["1"],
    );
    await user.click(routineForm.getByRole("button", { name: "Create Routine" }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        "http://localhost:8000/routines",
        {
          name: "Full Body",
          description: "All major lifts",
          workouts: [1],
        },
      );
    });
    expect(await screen.findByText("Full Body")).toBeInTheDocument();
  });

  it("calls logout when the logout button is clicked", async () => {
    const user = userEvent.setup();
    renderHome();

    await user.click(await screen.findByRole("button", { name: "Logout" }));

    expect(mockLogout).toHaveBeenCalledTimes(1);
  });
});
