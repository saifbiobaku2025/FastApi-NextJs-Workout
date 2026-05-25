import { useContext } from "react";
import { act, render, screen, waitFor } from "@testing-library/react";
import axios from "axios";
import AuthContext, { AuthProvider } from "../app/context/AuthContext";
import { API_BASE_URL } from "../lib/api";

jest.mock("axios");

let authContextValue;

function AuthTestConsumer() {
  const context = useContext(AuthContext);
  authContextValue = context;

  return (
    <div>
      <span data-testid="loading">{String(context.isAuthLoading)}</span>
      <span data-testid="user">{context.user ? "logged-in" : "logged-out"}</span>
    </div>
  );
}

function renderAuthProvider() {
  authContextValue = undefined;
  render(
    <AuthProvider>
      <AuthTestConsumer />
    </AuthProvider>,
  );
}

describe("AuthProvider", () => {
  beforeEach(() => {
    axios.post.mockReset();
    axios.defaults = { headers: { common: {} } };
  });

  it("starts loading then reports logged-out when no token exists", async () => {
    renderAuthProvider();

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false");
    });
    expect(screen.getByTestId("user")).toHaveTextContent("logged-out");
  });

  it("restores session from localStorage token on mount", async () => {
    localStorage.setItem("token", "saved-token");

    renderAuthProvider();

    await waitFor(() => {
      expect(screen.getByTestId("user")).toHaveTextContent("logged-in");
    });
    expect(axios.defaults.headers.common.Authorization).toBe(
      "Bearer saved-token",
    );
  });

  it("login stores token, sets auth header, and navigates home", async () => {
    axios.post.mockResolvedValue({
      data: { access_token: "new-token", token_type: "bearer" },
    });

    renderAuthProvider();

    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false");
    });

    await act(async () => {
      await authContextValue.login("alice", "secret");
    });

    expect(screen.getByTestId("user")).toHaveTextContent("logged-in");
    expect(axios.post).toHaveBeenCalledWith(
      `${API_BASE_URL}/auth/token`,
      expect.any(URLSearchParams),
      {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      },
    );
    expect(localStorage.getItem("token")).toBe("new-token");
    expect(axios.defaults.headers.common.Authorization).toBe("Bearer new-token");
    expect(global.mockPush).toHaveBeenCalledWith("/");
  });

  it("logout clears token, auth header, and navigates to login", async () => {
    localStorage.setItem("token", "saved-token");
    axios.defaults.headers.common.Authorization = "Bearer saved-token";

    renderAuthProvider();

    await waitFor(() => {
      expect(screen.getByTestId("user")).toHaveTextContent("logged-in");
    });

    act(() => {
      authContextValue.logout();
    });

    expect(screen.getByTestId("user")).toHaveTextContent("logged-out");
    expect(localStorage.getItem("token")).toBeNull();
    expect(axios.defaults.headers.common.Authorization).toBeUndefined();
    expect(global.mockPush).toHaveBeenCalledWith("/login");
  });
});
