import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import axios from "axios";
import AuthContext from "../app/context/AuthContext";
import Login from "../app/login/page";
import { API_BASE_URL } from "../config/api";

jest.mock("axios");

const mockLogin = jest.fn();

function renderLogin() {
  return render(
    <AuthContext.Provider value={{ login: mockLogin }}>
      <Login />
    </AuthContext.Provider>,
  );
}

function getLoginForm() {
  return within(document.getElementById("username").closest("form"));
}

function getRegisterForm() {
  return within(document.getElementById("registerUsername").closest("form"));
}

describe("Login page", () => {
  beforeEach(() => {
    mockLogin.mockReset();
    axios.post.mockReset();
    jest.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    console.error.mockRestore();
  });

  it("renders login and register forms", () => {
    renderLogin();

    expect(screen.getByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Register" })).toBeInTheDocument();
    expect(getLoginForm().getByLabelText("Username")).toBeInTheDocument();
    expect(getLoginForm().getByLabelText("Password")).toBeInTheDocument();
    expect(getRegisterForm().getByLabelText("Username")).toBeInTheDocument();
    expect(getRegisterForm().getByLabelText("Password")).toBeInTheDocument();
  });

  it("submits login credentials to auth context", async () => {
    mockLogin.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderLogin();

    const loginForm = getLoginForm();
    await user.type(loginForm.getByLabelText("Username"), "alice");
    await user.type(loginForm.getByLabelText("Password"), "secret");
    await user.click(loginForm.getByRole("button", { name: "Login" }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("alice", "secret");
    });
  });

  it("shows an error when login fails", async () => {
    mockLogin.mockRejectedValue(new Error("invalid credentials"));
    const user = userEvent.setup();
    renderLogin();

    const loginForm = getLoginForm();
    await user.type(loginForm.getByLabelText("Username"), "alice");
    await user.type(loginForm.getByLabelText("Password"), "wrong");
    await user.click(loginForm.getByRole("button", { name: "Login" }));

    expect(
      await screen.findByText(
        "Login failed. Check your username and password.",
      ),
    ).toBeInTheDocument();
  });

  it("registers a user then logs in", async () => {
    axios.post.mockResolvedValue({ data: { id: 1, username: "bob" } });
    mockLogin.mockResolvedValue(undefined);
    const user = userEvent.setup();
    renderLogin();

    const registerForm = getRegisterForm();
    await user.type(registerForm.getByLabelText("Username"), "bob");
    await user.type(registerForm.getByLabelText("Password"), "secret123");
    await user.click(registerForm.getByRole("button", { name: "Register" }));

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(`${API_BASE_URL}/auth`, {
        username: "bob",
        password: "secret123",
      });
    });
    expect(mockLogin).toHaveBeenCalledWith("bob", "secret123");
  });

  it("shows conflict message when username is already registered", async () => {
    axios.post.mockRejectedValue({ response: { status: 409 } });
    const user = userEvent.setup();
    renderLogin();

    const registerForm = getRegisterForm();
    await user.type(registerForm.getByLabelText("Username"), "existing");
    await user.type(registerForm.getByLabelText("Password"), "secret123");
    await user.click(registerForm.getByRole("button", { name: "Register" }));

    expect(
      await screen.findByText("Username already registered."),
    ).toBeInTheDocument();
  });

  it("shows generic error when registration fails", async () => {
    axios.post.mockRejectedValue(new Error("network error"));
    const user = userEvent.setup();
    renderLogin();

    const registerForm = getRegisterForm();
    await user.type(registerForm.getByLabelText("Username"), "bob");
    await user.type(registerForm.getByLabelText("Password"), "secret123");
    await user.click(registerForm.getByRole("button", { name: "Register" }));

    expect(
      await screen.findByText("Failed to register user."),
    ).toBeInTheDocument();
  });
});
