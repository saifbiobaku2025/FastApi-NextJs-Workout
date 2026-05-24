import { render, screen, waitFor } from "@testing-library/react";
import AuthContext from "../app/context/AuthContext";
import ProtectedRoute from "../app/components/ProtectedRoute";

function renderWithAuth(value) {
  return render(
    <AuthContext.Provider value={value}>
      <ProtectedRoute>
        <div>protected-content</div>
      </ProtectedRoute>
    </AuthContext.Provider>,
  );
}

describe("ProtectedRoute", () => {
  it("renders nothing while auth is loading", () => {
    renderWithAuth({
      user: null,
      isAuthLoading: true,
    });

    expect(screen.queryByText("protected-content")).not.toBeInTheDocument();
  });

  it("redirects to login when user is not authenticated", async () => {
    renderWithAuth({
      user: null,
      isAuthLoading: false,
    });

    await waitFor(() => {
      expect(global.mockPush).toHaveBeenCalledWith("/login");
    });
    expect(screen.queryByText("protected-content")).not.toBeInTheDocument();
  });

  it("renders children when user is authenticated", () => {
    renderWithAuth({
      user: { authenticated: true },
      isAuthLoading: false,
    });

    expect(screen.getByText("protected-content")).toBeInTheDocument();
    expect(global.mockPush).not.toHaveBeenCalled();
  });
});
